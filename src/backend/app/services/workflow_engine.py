"""
工作流引擎 - 状态机 + 并行审批 + 超时处理
数据资产管理平台核心模块
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workflow import (
    WorkflowDefinition, WorkflowInstance, WorkflowNode, ApprovalRecord
)
from app.models.asset import DataAsset
from app.models.system import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)

# 资产状态与工作流节点的映射
NODE_TO_ASSET_STATUS = {
    "pre_review": "pre_review",
    "first_review": "reviewing",
    "third_party": "reviewing",
    "final_review": "reviewing",
    "publicize": "publicizing",
}


class WorkflowEngine:
    """工作流引擎：管理审批流程的启动、推进、驳回、补正和超时"""

    # ─── 启动工作流 ───────────────────────────────────────────

    @staticmethod
    async def start_workflow(
        db: AsyncSession,
        asset_id: int,
        user: User,
    ) -> WorkflowInstance:
        """
        启动审批工作流
        1. 查找资产对应的默认流程定义
        2. 创建工作流实例
        3. 根据定义创建所有节点（初始pending）
        4. 激活第一个节点
        5. 更新资产状态为 submitted
        """
        # 查找资产
        asset = await db.get(DataAsset, asset_id)
        if not asset:
            raise ValueError(f"资产不存在: {asset_id}")
        if asset.status not in ("draft", "correction"):
            raise ValueError(f"资产状态 {asset.status} 不允许提交审批")

        # 查找默认流程定义
        stmt = select(WorkflowDefinition).where(
            and_(
                WorkflowDefinition.is_default == True,
                WorkflowDefinition.status == "active",
            )
        )
        result = await db.execute(stmt)
        definition = result.scalar_one_or_none()
        if not definition:
            raise ValueError("未找到默认工作流定义，请联系管理员配置")

        nodes_config = definition.nodes or []
        if not nodes_config:
            raise ValueError("工作流定义中没有节点配置")

        # 创建工作流实例
        instance = WorkflowInstance(
            asset_id=asset_id,
            definition_id=definition.id,
            current_node=nodes_config[0]["id"],
            status="active",
            started_at=datetime.now(),
            deadline=datetime.now() + timedelta(days=30),
            created_by=user.id,
        )
        db.add(instance)
        await db.flush()

        # 创建所有节点
        for i, node_cfg in enumerate(nodes_config):
            timeout_days = node_cfg.get("timeout_days", 7)
            node = WorkflowNode(
                workflow_id=instance.id,
                node_id=node_cfg["id"],
                node_type=node_cfg.get("type", "serial"),
                parallel_group=node_cfg.get("parallel_group"),
                status="pending",
                deadline=datetime.now() + timedelta(days=timeout_days),
            )
            # 第一个节点激活
            if i == 0:
                node.status = "active"
                node.started_at = datetime.now()
            db.add(node)

        # 更新资产状态
        asset.status = "submitted"
        await db.flush()

        # 审计日志
        await WorkflowEngine._log_audit(
            db, user.id, asset_id, "workflow_start",
            f"启动审批流程: {definition.name}"
        )

        # 检查第一个节点是否自动通过
        first_node_cfg = nodes_config[0]
        if first_node_cfg.get("auto_pass"):
            await WorkflowEngine._auto_advance(db, instance, first_node_cfg["id"], nodes_config, definition.transitions or [])

        await db.commit()
        await db.refresh(instance)
        return instance

    # ─── 审批通过 ─────────────────────────────────────────────

    @staticmethod
    async def approve_node(
        db: AsyncSession,
        node_id: int,
        user: User,
        comment: str = "",
    ) -> dict:
        """
        审批通过当前节点
        1. 验证节点状态为 active
        2. 记录审批意见
        3. 标记节点完成
        4. 检查并行组是否全部完成
        5. 推进到下一节点或完成流程
        """
        node = await db.get(WorkflowNode, node_id)
        if not node:
            raise ValueError(f"节点不存在: {node_id}")
        if node.status != "active":
            raise ValueError(f"节点状态 {node.status} 不允许审批")

        instance = await db.get(WorkflowInstance, node.workflow_id)
        if not instance or instance.status != "active":
            raise ValueError("工作流实例不存在或已结束")

        # 获取流程定义
        definition = await db.get(WorkflowDefinition, instance.definition_id)
        nodes_config = definition.nodes or []
        transitions = definition.transitions or []

        # 记录审批
        record = ApprovalRecord(
            workflow_id=instance.id,
            asset_id=instance.asset_id,
            node_name=node.node_id,
            action="approve",
            operator_id=user.id,
            comment=comment,
            operated_at=datetime.now(),
        )
        db.add(record)

        # 标记节点完成
        node.status = "completed"
        node.completed_at = datetime.now()
        node.result = "approved"
        node.comment = comment

        # 检查并行组
        if node.parallel_group:
            group_complete = await WorkflowEngine._check_parallel_group(
                db, instance.id, node.parallel_group
            )
            if not group_complete:
                await db.commit()
                return {"action": "approved", "message": "并行审批中，等待其他节点完成"}

        # 推进到下一节点
        result = await WorkflowEngine._advance_to_next(
            db, instance, node.node_id, nodes_config, transitions
        )

        await WorkflowEngine._log_audit(
            db, user.id, instance.asset_id, "workflow_approve",
            f"审批通过节点: {node.node_id}, 意见: {comment}"
        )

        await db.commit()
        return result

    # ─── 驳回 ─────────────────────────────────────────────────

    @staticmethod
    async def reject_node(
        db: AsyncSession,
        node_id: int,
        user: User,
        comment: str,
        reject_to_node: Optional[str] = None,
    ) -> dict:
        """
        驳回：回退到指定节点或直接驳回
        - reject_to_node 为空：直接驳回，流程结束
        - reject_to_node 有值：回退到该节点，中间节点重置
        """
        node = await db.get(WorkflowNode, node_id)
        if not node:
            raise ValueError(f"节点不存在: {node_id}")
        if node.status != "active":
            raise ValueError(f"节点状态 {node.status} 不允许驳回")

        instance = await db.get(WorkflowInstance, node.workflow_id)
        if not instance or instance.status != "active":
            raise ValueError("工作流实例不存在或已结束")

        # 记录驳回
        record = ApprovalRecord(
            workflow_id=instance.id,
            asset_id=instance.asset_id,
            node_name=node.node_id,
            action="reject",
            operator_id=user.id,
            comment=comment,
            reject_to_node=reject_to_node,
            operated_at=datetime.now(),
        )
        db.add(record)

        node.status = "rejected"
        node.completed_at = datetime.now()
        node.result = "rejected"
        node.comment = comment

        asset = await db.get(DataAsset, instance.asset_id)

        if reject_to_node:
            # 回退到指定节点：重置中间节点
            await WorkflowEngine._rollback_to_node(
                db, instance, node.node_id, reject_to_node
            )
            if asset:
                asset.status = "correction"
            result = {"action": "rejected", "message": f"已驳回并回退到 {reject_to_node}"}
        else:
            # 直接驳回，流程结束
            instance.status = "cancelled"
            instance.completed_at = datetime.now()
            if asset:
                asset.status = "rejected"
            result = {"action": "rejected", "message": "已驳回，流程终止"}

        await WorkflowEngine._log_audit(
            db, user.id, instance.asset_id, "workflow_reject",
            f"驳回节点: {node.node_id}, 回退到: {reject_to_node or '终止'}, 意见: {comment}"
        )

        await db.commit()
        return result

    # ─── 补正 ─────────────────────────────────────────────────

    @staticmethod
    async def request_correction(
        db: AsyncSession,
        node_id: int,
        user: User,
        comment: str,
    ) -> dict:
        """要求补正：资产进入correction状态，当前节点保持active"""
        node = await db.get(WorkflowNode, node_id)
        if not node:
            raise ValueError(f"节点不存在: {node_id}")
        if node.status != "active":
            raise ValueError(f"节点状态 {node.status} 不允许要求补正")

        instance = await db.get(WorkflowInstance, node.workflow_id)
        if not instance or instance.status != "active":
            raise ValueError("工作流实例不存在或已结束")

        # 记录补正要求
        record = ApprovalRecord(
            workflow_id=instance.id,
            asset_id=instance.asset_id,
            node_name=node.node_id,
            action="correct",
            operator_id=user.id,
            comment=comment,
            operated_at=datetime.now(),
        )
        db.add(record)

        # 更新资产状态
        asset = await db.get(DataAsset, instance.asset_id)
        if asset:
            asset.status = "correction"

        await WorkflowEngine._log_audit(
            db, user.id, instance.asset_id, "workflow_correct",
            f"要求补正: {node.node_id}, 意见: {comment}"
        )

        await db.commit()
        return {"action": "correction", "message": "已要求补正，等待持有方修改后重新提交"}

    # ─── 提交补正（持有方） ───────────────────────────────────

    @staticmethod
    async def submit_correction(
        db: AsyncSession,
        asset_id: int,
        user: User,
    ) -> dict:
        """持有方提交补正后，恢复流程继续审批"""
        asset = await db.get(DataAsset, asset_id)
        if not asset:
            raise ValueError(f"资产不存在: {asset_id}")
        if asset.status != "correction":
            raise ValueError("资产不在补正状态")

        # 查找活跃的工作流实例
        stmt = select(WorkflowInstance).where(
            and_(
                WorkflowInstance.asset_id == asset_id,
                WorkflowInstance.status == "active",
            )
        )
        result = await db.execute(stmt)
        instance = result.scalar_one_or_none()
        if not instance:
            raise ValueError("未找到活跃的工作流实例")

        # 恢复资产状态为审核中
        asset.status = "reviewing"

        await WorkflowEngine._log_audit(
            db, user.id, asset_id, "workflow_correction_submit",
            "持有方提交补正材料"
        )

        await db.commit()
        return {"action": "correction_submitted", "message": "补正已提交，等待继续审批"}

    # ─── 查询方法 ─────────────────────────────────────────────

    @staticmethod
    async def get_workflow_status(
        db: AsyncSession,
        asset_id: int,
    ) -> Optional[dict]:
        """获取资产的工作流状态"""
        stmt = select(WorkflowInstance).where(
            WorkflowInstance.asset_id == asset_id
        ).order_by(WorkflowInstance.started_at.desc())
        result = await db.execute(stmt)
        instance = result.scalar_one_or_none()
        if not instance:
            return None

        # 获取所有节点
        nodes_stmt = select(WorkflowNode).where(
            WorkflowNode.workflow_id == instance.id
        ).order_by(WorkflowNode.id)
        nodes_result = await db.execute(nodes_stmt)
        nodes = nodes_result.scalars().all()

        total = len(nodes)
        completed = sum(1 for n in nodes if n.status == "completed")
        progress = int((completed / total * 100)) if total > 0 else 0

        return {
            "workflow_id": instance.id,
            "asset_id": asset_id,
            "status": instance.status,
            "current_node": instance.current_node,
            "progress_percent": progress,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "nodes": [
                {
                    "id": n.id,
                    "node_id": n.node_id,
                    "node_type": n.node_type,
                    "status": n.status,
                    "result": n.result,
                    "comment": n.comment,
                    "started_at": n.started_at.isoformat() if n.started_at else None,
                    "completed_at": n.completed_at.isoformat() if n.completed_at else None,
                    "deadline": n.deadline.isoformat() if n.deadline else None,
                }
                for n in nodes
            ],
        }

    @staticmethod
    async def get_pending_tasks(
        db: AsyncSession,
        user: User,
    ) -> list[dict]:
        """获取用户的待办任务（根据角色匹配）"""
        stmt = (
            select(WorkflowNode, WorkflowInstance, DataAsset)
            .join(WorkflowInstance, WorkflowNode.workflow_id == WorkflowInstance.id)
            .join(DataAsset, WorkflowInstance.asset_id == DataAsset.id)
            .where(
                and_(
                    WorkflowNode.status == "active",
                    WorkflowInstance.status == "active",
                )
            )
            .order_by(WorkflowNode.deadline.asc())
        )
        result = await db.execute(stmt)
        rows = result.all()

        # 根据用户角色过滤
        user_role = user.role if hasattr(user, 'role') else ''
        tasks = []
        for node, instance, asset in rows:
            # 简单角色匹配（实际可根据流程定义中的role字段精确匹配）
            tasks.append({
                "node_id": node.id,
                "node_name": node.node_id,
                "node_type": node.node_type,
                "asset_id": asset.id,
                "asset_name": asset.asset_name,
                "asset_code": asset.asset_code,
                "workflow_id": instance.id,
                "deadline": node.deadline.isoformat() if node.deadline else None,
                "started_at": node.started_at.isoformat() if node.started_at else None,
            })

        return tasks

    @staticmethod
    async def get_approval_history(
        db: AsyncSession,
        asset_id: int,
    ) -> list[dict]:
        """获取资产的审批历史"""
        stmt = (
            select(ApprovalRecord, User)
            .outerjoin(User, ApprovalRecord.operator_id == User.id)
            .where(ApprovalRecord.asset_id == asset_id)
            .order_by(ApprovalRecord.operated_at.asc())
        )
        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": record.id,
                "node_name": record.node_name,
                "action": record.action,
                "operator_id": record.operator_id,
                "operator_name": user.real_name if user and hasattr(user, 'real_name') else str(record.operator_id),
                "comment": record.comment,
                "reject_to_node": record.reject_to_node,
                "operated_at": record.operated_at.isoformat() if record.operated_at else None,
            }
            for record, user in rows
        ]

    # ─── 超时检查 ─────────────────────────────────────────────

    @staticmethod
    async def check_timeout(db: AsyncSession) -> list[dict]:
        """
        检查超时节点（供定时任务调用）
        返回超时节点列表，不自动处理
        """
        now = datetime.now()
        stmt = (
            select(WorkflowNode, WorkflowInstance, DataAsset)
            .join(WorkflowInstance, WorkflowNode.workflow_id == WorkflowInstance.id)
            .join(DataAsset, WorkflowInstance.asset_id == DataAsset.id)
            .where(
                and_(
                    WorkflowNode.status == "active",
                    WorkflowNode.deadline < now,
                    WorkflowInstance.status == "active",
                )
            )
        )
        result = await db.execute(stmt)
        rows = result.all()

        timeout_list = []
        for node, instance, asset in rows:
            overdue_hours = int((now - node.deadline).total_seconds() / 3600)
            timeout_list.append({
                "node_id": node.id,
                "node_name": node.node_id,
                "asset_id": asset.id,
                "asset_name": asset.asset_name,
                "asset_code": asset.asset_code,
                "deadline": node.deadline.isoformat(),
                "overdue_hours": overdue_hours,
                "workflow_id": instance.id,
            })

        logger.info(f"超时检查完成，发现 {len(timeout_list)} 个超时节点")
        return timeout_list

    # ─── 内部方法 ─────────────────────────────────────────────

    @staticmethod
    async def _advance_to_next(
        db: AsyncSession,
        instance: WorkflowInstance,
        current_node_id: str,
        nodes_config: list[dict],
        transitions: list[dict],
    ) -> dict:
        """推进到下一个节点"""
        # 查找匹配的转换规则
        next_node_id = None
        for trans in transitions:
            if trans["from"] == current_node_id and trans["condition"] == "approved":
                # 检查条件（简化处理，实际可用eval或规则引擎）
                next_node_id = trans["to"]
                break

        if not next_node_id:
            # 没有下一个节点，尝试按顺序查找
            current_idx = None
            for i, cfg in enumerate(nodes_config):
                if cfg["id"] == current_node_id:
                    current_idx = i
                    break
            if current_idx is not None and current_idx + 1 < len(nodes_config):
                next_node_id = nodes_config[current_idx + 1]["id"]

        if not next_node_id:
            # 流程完成
            return await WorkflowEngine._complete_workflow(db, instance)

        # 激活下一个节点
        stmt = select(WorkflowNode).where(
            and_(
                WorkflowNode.workflow_id == instance.id,
                WorkflowNode.node_id == next_node_id,
            )
        )
        result = await db.execute(stmt)
        next_node = result.scalar_one_or_none()

        if next_node:
            next_node.status = "active"
            next_node.started_at = datetime.now()
            instance.current_node = next_node_id

            # 同步资产状态
            asset_status = NODE_TO_ASSET_STATUS.get(next_node_id, "reviewing")
            asset = await db.get(DataAsset, instance.asset_id)
            if asset:
                asset.status = asset_status

            # 检查是否自动通过
            for cfg in nodes_config:
                if cfg["id"] == next_node_id and cfg.get("auto_pass"):
                    return await WorkflowEngine._auto_advance(
                        db, instance, next_node_id, nodes_config, transitions
                    )

            return {"action": "advanced", "message": f"已推进到节点: {next_node_id}"}
        else:
            return await WorkflowEngine._complete_workflow(db, instance)

    @staticmethod
    async def _auto_advance(
        db: AsyncSession,
        instance: WorkflowInstance,
        node_id: str,
        nodes_config: list[dict],
        transitions: list[dict],
    ) -> dict:
        """自动通过节点并推进"""
        stmt = select(WorkflowNode).where(
            and_(
                WorkflowNode.workflow_id == instance.id,
                WorkflowNode.node_id == node_id,
            )
        )
        result = await db.execute(stmt)
        node = result.scalar_one_or_none()
        if node and node.status == "active":
            node.status = "completed"
            node.completed_at = datetime.now()
            node.result = "auto_approved"
            node.comment = "系统自动通过"

            # 记录自动审批
            record = ApprovalRecord(
                workflow_id=instance.id,
                asset_id=instance.asset_id,
                node_name=node_id,
                action="approve",
                operator_id=0,  # 系统操作
                comment="系统自动通过",
                operated_at=datetime.now(),
            )
            db.add(record)

            return await WorkflowEngine._advance_to_next(
                db, instance, node_id, nodes_config, transitions
            )
        return {"action": "auto_advanced", "message": f"节点 {node_id} 自动通过"}

    @staticmethod
    async def _complete_workflow(
        db: AsyncSession,
        instance: WorkflowInstance,
    ) -> dict:
        """完成工作流"""
        instance.status = "completed"
        instance.completed_at = datetime.now()

        # 更新资产状态为生效
        asset = await db.get(DataAsset, instance.asset_id)
        if asset:
            asset.status = "effective"

        return {"action": "completed", "message": "审批流程已完成，资产已生效"}

    @staticmethod
    async def _check_parallel_group(
        db: AsyncSession,
        workflow_id: int,
        parallel_group: str,
    ) -> bool:
        """检查并行组是否全部完成"""
        stmt = select(WorkflowNode).where(
            and_(
                WorkflowNode.workflow_id == workflow_id,
                WorkflowNode.parallel_group == parallel_group,
            )
        )
        result = await db.execute(stmt)
        nodes = result.scalars().all()
        return all(n.status == "completed" for n in nodes)

    @staticmethod
    async def _rollback_to_node(
        db: AsyncSession,
        instance: WorkflowInstance,
        from_node_id: str,
        to_node_id: str,
    ) -> None:
        """回退到指定节点，重置中间节点"""
        # 获取所有节点
        stmt = select(WorkflowNode).where(
            WorkflowNode.workflow_id == instance.id
        ).order_by(WorkflowNode.id)
        result = await db.execute(stmt)
        nodes = result.scalars().all()

        # 找到目标节点和当前节点的位置
        node_ids = [n.node_id for n in nodes]
        try:
            from_idx = node_ids.index(from_node_id)
            to_idx = node_ids.index(to_node_id)
        except ValueError:
            raise ValueError(f"节点 {to_node_id} 不存在于当前流程中")

        if to_idx >= from_idx:
            raise ValueError("只能回退到之前的节点")

        # 重置从目标节点到当前节点之间的所有节点
        for i in range(to_idx, from_idx + 1):
            nodes[i].status = "pending"
            nodes[i].started_at = None
            nodes[i].completed_at = None
            nodes[i].result = None
            nodes[i].comment = None

        # 激活目标节点
        nodes[to_idx].status = "active"
        nodes[to_idx].started_at = datetime.now()

        # 更新实例当前节点
        instance.current_node = to_node_id

    @staticmethod
    async def _log_audit(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        action: str,
        detail: str,
    ) -> None:
        """记录审计日志"""
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type="workflow",
                resource_id=str(asset_id),
                detail=detail,
                ip_address="system",
            )
            db.add(log)
        except Exception as e:
            logger.warning(f"审计日志记录失败: {e}")
