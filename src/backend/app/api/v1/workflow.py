"""
Workflow API Routes
数据资产管理平台 - 工作流审批API接口
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_roles
from app.models.asset import DataAsset
from app.models.workflow import WorkflowInstance, WorkflowNode, ApprovalRecord
from app.services.workflow_engine import WorkflowEngine
from app.schemas.workflow import (
    ApproveRequest,
    RejectRequest,
    CorrectionRequest,
    WorkflowStatus,
    PendingTask,
    ApprovalHistory,
    WorkflowDefinitionInfo,
    ApiResponse
)

router = APIRouter(prefix="/api/v1/workflow", tags=["workflow"])


# ==================== Helper Functions ====================

async def get_workflow_engine(db: AsyncSession = Depends(get_db)) -> WorkflowEngine:
    """获取工作流引擎实例"""
    return WorkflowEngine(db)


def create_response(data=None, message: str = "success", code: int = 200) -> dict:
    """创建统一响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


# ==================== API Endpoints ====================

@router.post("/start/{asset_id}", summary="启动审批流程")
async def start_workflow(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    启动资产审批流程
    
    权限：holder_admin, holder_user
    """
    # 权限检查
    require_roles(current_user, ["holder_admin", "holder_user"])
    
    try:
        # 检查资产是否存在
        from sqlalchemy import select
        result = await db.execute(select(DataAsset).where(DataAsset.id == asset_id))
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"资产不存在: {asset_id}"
            )
        
        # 检查是否已有进行中的流程
        result = await db.execute(
            select(WorkflowInstance).where(
                WorkflowInstance.asset_id == asset_id,
                WorkflowInstance.status == "running"
            )
        )
        existing_workflow = result.scalar_one_or_none()
        
        if existing_workflow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该资产已有进行中的审批流程"
            )
        
        # 启动工作流
        workflow_instance = await engine.start_workflow(asset_id, current_user)
        
        return create_response(
            data={
                "workflow_id": workflow_instance.id,
                "asset_id": asset_id,
                "status": workflow_instance.status,
                "message": "审批流程已启动"
            },
            message="审批流程启动成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动流程失败: {str(e)}"
        )


@router.get("/{asset_id}/status", summary="获取流程状态")
async def get_workflow_status(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    获取资产审批流程状态
    
    返回当前节点、各节点状态、进度等信息
    """
    try:
        # 获取工作流状态
        workflow_status = await engine.get_workflow_status(asset_id)
        
        if not workflow_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到资产的审批流程: {asset_id}"
            )
        
        return create_response(
            data=workflow_status,
            message="获取流程状态成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取流程状态失败: {str(e)}"
        )


@router.post("/approve/{node_id}", summary="审批通过")
async def approve_node(
    node_id: str,
    request: ApproveRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    审批通过
    
    权限：center_admin, center_user（初审终审）, evaluator（第三方评估）
    """
    # 权限检查
    require_roles(current_user, ["center_admin", "center_user", "evaluator"])
    
    try:
        # 检查节点是否存在
        from sqlalchemy import select
        result = await db.execute(select(WorkflowNode).where(WorkflowNode.id == node_id))
        node = result.scalar_one_or_none()
        
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"节点不存在: {node_id}"
            )
        
        # 检查节点状态
        if node.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"节点状态不允许审批: {node.status}"
            )
        
        # 检查用户角色是否匹配节点要求
        if node.assignee_role and node.assignee_role not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限处理此节点"
            )
        
        # 执行审批通过
        result = await engine.approve_node(node_id, current_user, request.comment)
        
        return create_response(
            data={
                "node_id": node_id,
                "status": "approved",
                "next_node": result.get("next_node"),
                "workflow_status": result.get("workflow_status")
            },
            message="审批通过成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审批操作失败: {str(e)}"
        )


@router.post("/reject/{node_id}", summary="驳回")
async def reject_node(
    node_id: str,
    request: RejectRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    驳回审批
    
    权限：center_admin, center_user（初审终审）, evaluator（第三方评估）
    """
    # 权限检查
    require_roles(current_user, ["center_admin", "center_user", "evaluator"])
    
    try:
        # 检查节点是否存在
        from sqlalchemy import select
        result = await db.execute(select(WorkflowNode).where(WorkflowNode.id == node_id))
        node = result.scalar_one_or_none()
        
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"节点不存在: {node_id}"
            )
        
        # 检查节点状态
        if node.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"节点状态不允许驳回: {node.status}"
            )
        
        # 检查用户角色是否匹配节点要求
        if node.assignee_role and node.assignee_role not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限处理此节点"
            )
        
        # 执行驳回
        result = await engine.reject_node(
            node_id, 
            current_user, 
            request.comment, 
            request.reject_to_node
        )
        
        return create_response(
            data={
                "node_id": node_id,
                "status": "rejected",
                "reject_to": result.get("reject_to_node"),
                "workflow_status": result.get("workflow_status")
            },
            message="驳回成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"驳回操作失败: {str(e)}"
        )


@router.post("/correct/{asset_id}", summary="提交补正")
async def submit_correction(
    asset_id: str,
    request: CorrectionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    提交补正（holder角色在被驳回后补正资产信息并继续流程）
    
    权限：holder_admin, holder_user
    """
    # 权限检查
    require_roles(current_user, ["holder_admin", "holder_user"])
    
    try:
        # 检查资产是否存在
        from sqlalchemy import select
        result = await db.execute(select(DataAsset).where(DataAsset.id == asset_id))
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"资产不存在: {asset_id}"
            )
        
        # 检查是否有被驳回的流程
        result = await db.execute(
            select(WorkflowInstance).where(
                WorkflowInstance.asset_id == asset_id,
                WorkflowInstance.status.in_(["rejected", "correction_required"])
            ).order_by(WorkflowInstance.created_at.desc())
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该资产没有需要补正的审批流程"
            )
        
        # 提交补正（这里假设WorkflowEngine有request_correction方法）
        # 如果没有，我们在这里实现简单逻辑
        try:
            result = await engine.request_correction(workflow.id, current_user, request.comment)
        except AttributeError:
            # 如果WorkflowEngine没有这个方法，实现简单逻辑
            workflow.status = "running"
            # 找到当前被驳回的节点，重置为pending
            result = await db.execute(
                select(WorkflowNode).where(
                    WorkflowNode.workflow_id == workflow.id,
                    WorkflowNode.status == "rejected"
                ).order_by(WorkflowNode.sequence.desc())
            )
            rejected_node = result.scalar_one_or_none()
            
            if rejected_node:
                rejected_node.status = "pending"
            
            # 记录补正操作
            from datetime import datetime
            correction_record = ApprovalRecord(
                workflow_id=workflow.id,
                node_id=rejected_node.id if rejected_node else None,
                action="correct",
                operator_id=current_user.get("user_id"),
                operator_name=current_user.get("username"),
                operator_role=current_user.get("roles", [])[0] if current_user.get("roles") else None,
                comment=request.comment,
                timestamp=datetime.utcnow()
            )
            db.add(correction_record)
            await db.commit()
            
            result = {
                "workflow_id": workflow.id,
                "status": "running"
            }
        
        return create_response(
            data={
                "asset_id": asset_id,
                "workflow_id": result.get("workflow_id"),
                "status": result.get("status"),
                "message": "补正已提交，流程继续"
            },
            message="补正提交成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交补正失败: {str(e)}"
        )


@router.get("/pending", summary="我的待办列表")
async def get_pending_tasks(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    获取当前用户的待办任务列表
    
    根据用户角色自动匹配待处理节点
    """
    try:
        # 获取待办任务
        pending_tasks = await engine.get_pending_tasks(current_user)
        
        return create_response(
            data={
                "total": len(pending_tasks),
                "tasks": pending_tasks
            },
            message="获取待办列表成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取待办列表失败: {str(e)}"
        )


@router.get("/history/{asset_id}", summary="审批历史")
async def get_approval_history(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    获取资产的审批历史（时间线格式）
    
    所有相关角色可查看
    """
    try:
        # 检查资产是否存在
        from sqlalchemy import select
        result = await db.execute(select(DataAsset).where(DataAsset.id == asset_id))
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"资产不存在: {asset_id}"
            )
        
        # 获取审批历史
        approval_history = await engine.get_approval_history(asset_id)
        
        if not approval_history:
            return create_response(
                data={
                    "asset_id": asset_id,
                    "asset_name": asset.name,
                    "records": []
                },
                message="暂无审批历史"
            )
        
        return create_response(
            data=approval_history,
            message="获取审批历史成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审批历史失败: {str(e)}"
        )


@router.get("/definitions", summary="流程定义列表")
async def get_workflow_definitions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取工作流定义列表
    
    权限：管理员查看
    """
    # 权限检查（管理员角色）
    require_roles(current_user, ["center_admin", "holder_admin"])
    
    try:
        from sqlalchemy import select, func
        
        # 查询所有流程定义
        result = await db.execute(
            select(WorkflowDefinition).order_by(WorkflowDefinition.created_at.desc())
        )
        definitions = result.scalars().all()
        
        # 构建响应数据
        definition_list = []
        for definition in definitions:
            # 统计节点数量
            node_count_result = await db.execute(
                select(func.count()).select_from(WorkflowNode).where(
                    WorkflowNode.definition_id == definition.id
                )
            )
            node_count = node_count_result.scalar() or 0
            
            definition_list.append({
                "definition_id": definition.id,
                "name": definition.name,
                "description": definition.description,
                "version": definition.version,
                "status": definition.status,
                "node_count": node_count,
                "created_at": definition.created_at,
                "updated_at": definition.updated_at
            })
        
        return create_response(
            data={
                "total": len(definition_list),
                "definitions": definition_list
            },
            message="获取流程定义列表成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取流程定义列表失败: {str(e)}"
        )
