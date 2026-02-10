"""
有效期管理工具 - 证书到期提醒和状态管理
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class ExpiryStatus(str, Enum):
    """有效期状态"""
    VALID = "valid"  # 有效
    EXPIRING_SOON = "expiring_soon"  # 即将过期
    EXPIRED = "expired"  # 已过期
    NO_EXPIRY = "no_expiry"  # 无有效期


class AlertLevel(str, Enum):
    """提醒级别"""
    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    DANGER = "danger"  # 危险
    CRITICAL = "critical"  # 紧急


class ExpiryManager:
    """有效期管理器"""
    
    # 提醒阈值（天数）
    ALERT_THRESHOLDS = {
        'days_30': 30,
        'days_7': 7,
        'days_1': 1,
    }
    
    def __init__(self):
        """初始化有效期管理器"""
        pass
    
    def calculate_expiry_status(self, expiry_date: Optional[date]) -> ExpiryStatus:
        """
        计算有效期状态
        
        Args:
            expiry_date: 有效期日期
            
        Returns:
            ExpiryStatus: 有效期状态
        """
        if expiry_date is None:
            return ExpiryStatus.NO_EXPIRY
        
        today = date.today()
        
        if expiry_date < today:
            return ExpiryStatus.EXPIRED
        
        days_until_expiry = (expiry_date - today).days
        
        if days_until_expiry <= 30:
            return ExpiryStatus.EXPIRING_SOON
        
        return ExpiryStatus.VALID
    
    def calculate_days_until_expiry(self, expiry_date: Optional[date]) -> Optional[int]:
        """
        计算距离过期的天数
        
        Args:
            expiry_date: 有效期日期
            
        Returns:
            int: 距离过期的天数，负数表示已过期，None表示无有效期
        """
        if expiry_date is None:
            return None
        
        today = date.today()
        delta = expiry_date - today
        return delta.days
    
    def get_alert_level(self, days_until_expiry: Optional[int]) -> AlertLevel:
        """
        根据剩余天数获取提醒级别
        
        Args:
            days_until_expiry: 距离过期的天数
            
        Returns:
            AlertLevel: 提醒级别
        """
        if days_until_expiry is None:
            return AlertLevel.INFO
        
        if days_until_expiry < 0:
            return AlertLevel.CRITICAL  # 已过期
        elif days_until_expiry <= 1:
            return AlertLevel.DANGER  # 1天内
        elif days_until_expiry <= 7:
            return AlertLevel.WARNING  # 7天内
        elif days_until_expiry <= 30:
            return AlertLevel.INFO  # 30天内
        else:
            return AlertLevel.INFO
    
    def should_send_alert(self, expiry_date: Optional[date], 
                         last_alert_date: Optional[date] = None,
                         alert_type: str = 'days_30') -> bool:
        """
        判断是否应该发送提醒
        
        Args:
            expiry_date: 有效期日期
            last_alert_date: 上次提醒日期
            alert_type: 提醒类型（days_30/days_7/days_1/expired）
            
        Returns:
            bool: 是否应该发送提醒
        """
        if expiry_date is None:
            return False
        
        today = date.today()
        days_until_expiry = (expiry_date - today).days
        
        # 已过期提醒
        if alert_type == 'expired':
            if days_until_expiry < 0:
                # 每天提醒一次
                if last_alert_date is None or last_alert_date < today:
                    return True
            return False
        
        # 提前N天提醒
        threshold = self.ALERT_THRESHOLDS.get(alert_type, 30)
        
        if days_until_expiry <= threshold and days_until_expiry >= 0:
            # 如果从未提醒过，或者距离上次提醒已经超过1天
            if last_alert_date is None or (today - last_alert_date).days >= 1:
                return True
        
        return False
    
    def get_expiry_info(self, expiry_date: Optional[date]) -> Dict[str, Any]:
        """
        获取完整的有效期信息
        
        Args:
            expiry_date: 有效期日期
            
        Returns:
            dict: 有效期信息
        """
        days_until_expiry = self.calculate_days_until_expiry(expiry_date)
        status = self.calculate_expiry_status(expiry_date)
        alert_level = self.get_alert_level(days_until_expiry)
        
        info = {
            'expiry_date': expiry_date,
            'days_until_expiry': days_until_expiry,
            'status': status.value,
            'alert_level': alert_level.value,
            'is_expired': status == ExpiryStatus.EXPIRED,
            'is_expiring_soon': status == ExpiryStatus.EXPIRING_SOON,
            'message': self._get_expiry_message(days_until_expiry),
        }
        
        return info
    
    def _get_expiry_message(self, days_until_expiry: Optional[int]) -> str:
        """
        获取有效期消息
        
        Args:
            days_until_expiry: 距离过期的天数
            
        Returns:
            str: 消息文本
        """
        if days_until_expiry is None:
            return "该证书无有效期限制"
        
        if days_until_expiry < 0:
            return f"证书已过期 {abs(days_until_expiry)} 天"
        elif days_until_expiry == 0:
            return "证书今天到期"
        elif days_until_expiry == 1:
            return "证书明天到期"
        elif days_until_expiry <= 7:
            return f"证书将在 {days_until_expiry} 天后到期"
        elif days_until_expiry <= 30:
            return f"证书将在 {days_until_expiry} 天后到期"
        else:
            return f"证书有效期还有 {days_until_expiry} 天"
    
    def batch_check_expiry(self, certificates: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量检查证书有效期
        
        Args:
            certificates: 证书列表，每个证书包含id和expiry_date
            
        Returns:
            dict: 按状态分组的证书列表
        """
        result = {
            'expired': [],
            'expiring_1_day': [],
            'expiring_7_days': [],
            'expiring_30_days': [],
            'valid': [],
            'no_expiry': [],
        }
        
        for cert in certificates:
            expiry_date = cert.get('expiry_date')
            
            if expiry_date is None:
                result['no_expiry'].append(cert)
                continue
            
            days_until_expiry = self.calculate_days_until_expiry(expiry_date)
            
            if days_until_expiry < 0:
                result['expired'].append(cert)
            elif days_until_expiry <= 1:
                result['expiring_1_day'].append(cert)
            elif days_until_expiry <= 7:
                result['expiring_7_days'].append(cert)
            elif days_until_expiry <= 30:
                result['expiring_30_days'].append(cert)
            else:
                result['valid'].append(cert)
        
        return result
    
    def generate_alert_content(self, certificate: Dict[str, Any], 
                              alert_type: str) -> Tuple[str, str]:
        """
        生成提醒内容
        
        Args:
            certificate: 证书信息
            alert_type: 提醒类型
            
        Returns:
            tuple: (标题, 内容)
        """
        cert_no = certificate.get('certificate_no', '未知')
        cert_name = certificate.get('certificate_name', '证书')
        expiry_date = certificate.get('expiry_date')
        
        if alert_type == 'expired':
            title = f"证书已过期提醒 - {cert_no}"
            content = f"""
尊敬的用户：

您的证书 "{cert_name}" (编号: {cert_no}) 已经过期。

有效期至: {expiry_date}

请及时办理续期手续，以免影响正常使用。

此为系统自动提醒，请勿回复。
            """.strip()
        
        elif alert_type == 'days_1':
            title = f"证书即将到期提醒（1天内）- {cert_no}"
            content = f"""
尊敬的用户：

您的证书 "{cert_name}" (编号: {cert_no}) 即将在1天内到期。

有效期至: {expiry_date}

请尽快办理续期手续。

此为系统自动提醒，请勿回复。
            """.strip()
        
        elif alert_type == 'days_7':
            title = f"证书即将到期提醒（7天内）- {cert_no}"
            content = f"""
尊敬的用户：

您的证书 "{cert_name}" (编号: {cert_no}) 即将在7天内到期。

有效期至: {expiry_date}

请及时办理续期手续。

此为系统自动提醒，请勿回复。
            """.strip()
        
        else:  # days_30
            title = f"证书即将到期提醒（30天内）- {cert_no}"
            content = f"""
尊敬的用户：

您的证书 "{cert_name}" (编号: {cert_no}) 即将在30天内到期。

有效期至: {expiry_date}

请提前准备续期材料。

此为系统自动提醒，请勿回复。
            """.strip()
        
        return title, content
    
    def calculate_renewal_date(self, expiry_date: date, 
                              renewal_period_days: int = 365) -> date:
        """
        计算续期后的有效期
        
        Args:
            expiry_date: 当前有效期
            renewal_period_days: 续期天数（默认365天）
            
        Returns:
            date: 续期后的有效期
        """
        return expiry_date + timedelta(days=renewal_period_days)
    
    def get_certificates_expiring_in_range(self, 
                                          certificates: List[Dict[str, Any]],
                                          start_days: int,
                                          end_days: int) -> List[Dict[str, Any]]:
        """
        获取在指定天数范围内到期的证书
        
        Args:
            certificates: 证书列表
            start_days: 开始天数（包含）
            end_days: 结束天数（包含）
            
        Returns:
            list: 符合条件的证书列表
        """
        result = []
        
        for cert in certificates:
            expiry_date = cert.get('expiry_date')
            if expiry_date is None:
                continue
            
            days_until_expiry = self.calculate_days_until_expiry(expiry_date)
            
            if days_until_expiry is not None and start_days <= days_until_expiry <= end_days:
                result.append(cert)
        
        return result


# 全局有效期管理器实例
_expiry_manager: Optional[ExpiryManager] = None


def get_expiry_manager() -> ExpiryManager:
    """
    获取有效期管理器单例
    
    Returns:
        ExpiryManager: 有效期管理器实例
    """
    global _expiry_manager
    
    if _expiry_manager is None:
        _expiry_manager = ExpiryManager()
    
    return _expiry_manager
