"""
证书验证工具 - 证书有效性和防伪验证
"""
import hashlib
import hmac
import re
from typing import Dict, Any, Optional, Tuple
from datetime import date, datetime
import json

from app.utils.file_hash import calculate_bytes_hash


class CertificateValidator:
    """证书验证器 - 防伪和有效性验证"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化证书验证器
        
        Args:
            secret_key: 用于HMAC签名的密钥（可选）
        """
        self.secret_key = secret_key or "default_secret_key_change_in_production"
    
    def validate_certificate_no(self, certificate_no: str) -> Tuple[bool, str]:
        """
        验证证书编号格式
        
        Args:
            certificate_no: 证书编号
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not certificate_no:
            return False, "证书编号不能为空"
        
        # 长度检查
        if len(certificate_no) < 6 or len(certificate_no) > 100:
            return False, "证书编号长度应在6-100个字符之间"
        
        # 格式检查（字母、数字、连字符）
        if not re.match(r'^[A-Z0-9\-]+$', certificate_no, re.IGNORECASE):
            return False, "证书编号只能包含字母、数字和连字符"
        
        return True, "证书编号格式正确"
    
    def validate_file_hash(self, file_content: bytes, 
                          expected_hash: str,
                          algorithm: str = 'sha256') -> Tuple[bool, Dict[str, Any]]:
        """
        验证文件哈希值（防篡改）
        
        Args:
            file_content: 文件内容
            expected_hash: 期望的哈希值
            algorithm: 哈希算法
            
        Returns:
            tuple: (是否有效, 验证详情)
        """
        try:
            # 计算当前哈希
            current_hash = calculate_bytes_hash(file_content, algorithm)
            
            # 比对哈希值
            is_valid = current_hash.lower() == expected_hash.lower()
            
            details = {
                'is_valid': is_valid,
                'algorithm': algorithm,
                'expected_hash': expected_hash,
                'current_hash': current_hash,
                'message': '文件完整性验证通过' if is_valid else '警告：文件已被篡改！',
                'file_size': len(file_content),
            }
            
            return is_valid, details
        
        except Exception as e:
            return False, {
                'is_valid': False,
                'error': str(e),
                'message': f'哈希验证失败: {str(e)}',
            }
    
    def validate_digital_signature(self, data: str, 
                                   signature: str) -> Tuple[bool, str]:
        """
        验证数字签名
        
        Args:
            data: 原始数据
            signature: 数字签名
            
        Returns:
            tuple: (是否有效, 消息)
        """
        try:
            # 使用HMAC-SHA256验证签名
            expected_signature = self.generate_signature(data)
            
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            message = "数字签名验证通过" if is_valid else "数字签名验证失败"
            
            return is_valid, message
        
        except Exception as e:
            return False, f"签名验证异常: {str(e)}"
    
    def generate_signature(self, data: str) -> str:
        """
        生成数字签名
        
        Args:
            data: 原始数据
            
        Returns:
            str: 数字签名（十六进制）
        """
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def validate_expiry_date(self, issue_date: date, 
                            expiry_date: Optional[date]) -> Tuple[bool, str]:
        """
        验证有效期逻辑
        
        Args:
            issue_date: 颁发日期
            expiry_date: 有效期
            
        Returns:
            tuple: (是否有效, 消息)
        """
        if expiry_date is None:
            return True, "证书无有效期限制"
        
        # 有效期不能早于颁发日期
        if expiry_date < issue_date:
            return False, "有效期不能早于颁发日期"
        
        # 检查是否已过期
        today = date.today()
        if expiry_date < today:
            days_expired = (today - expiry_date).days
            return False, f"证书已过期 {days_expired} 天"
        
        # 检查是否即将过期
        days_until_expiry = (expiry_date - today).days
        if days_until_expiry <= 30:
            return True, f"证书即将在 {days_until_expiry} 天后到期"
        
        return True, "证书有效期正常"
    
    def validate_qr_code(self, qr_code_data: str, 
                        certificate_no: str) -> Tuple[bool, str]:
        """
        验证二维码数据
        
        Args:
            qr_code_data: 二维码数据
            certificate_no: 证书编号
            
        Returns:
            tuple: (是否有效, 消息)
        """
        try:
            # 尝试解析二维码数据（假设是JSON格式）
            try:
                qr_data = json.loads(qr_code_data)
            except json.JSONDecodeError:
                # 如果不是JSON，假设是简单的证书编号
                qr_data = {'certificate_no': qr_code_data}
            
            # 验证证书编号是否匹配
            qr_cert_no = qr_data.get('certificate_no', '')
            
            if qr_cert_no != certificate_no:
                return False, "二维码中的证书编号与证书不匹配"
            
            # 验证签名（如果有）
            if 'signature' in qr_data:
                data_to_sign = qr_cert_no
                signature = qr_data['signature']
                
                is_valid, message = self.validate_digital_signature(data_to_sign, signature)
                if not is_valid:
                    return False, f"二维码签名验证失败: {message}"
            
            return True, "二维码验证通过"
        
        except Exception as e:
            return False, f"二维码验证异常: {str(e)}"
    
    def validate_verification_code(self, verification_code: str,
                                   certificate_no: str) -> Tuple[bool, str]:
        """
        验证防伪验证码
        
        Args:
            verification_code: 防伪验证码
            certificate_no: 证书编号
            
        Returns:
            tuple: (是否有效, 消息)
        """
        try:
            # 生成期望的验证码
            expected_code = self.generate_verification_code(certificate_no)
            
            # 比对验证码
            is_valid = verification_code.upper() == expected_code.upper()
            
            message = "防伪验证码正确" if is_valid else "防伪验证码错误"
            
            return is_valid, message
        
        except Exception as e:
            return False, f"验证码验证异常: {str(e)}"
    
    def generate_verification_code(self, certificate_no: str, 
                                   length: int = 8) -> str:
        """
        生成防伪验证码
        
        Args:
            certificate_no: 证书编号
            length: 验证码长度
            
        Returns:
            str: 防伪验证码
        """
        # 使用HMAC生成验证码
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            certificate_no.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 取前N位作为验证码
        code = signature[:length].upper()
        
        return code
    
    def comprehensive_validation(self, certificate_data: Dict[str, Any],
                                file_content: Optional[bytes] = None) -> Dict[str, Any]:
        """
        综合验证证书
        
        Args:
            certificate_data: 证书数据
            file_content: 文件内容（可选）
            
        Returns:
            dict: 验证结果
        """
        results = {
            'is_valid': True,
            'validations': [],
            'errors': [],
            'warnings': [],
        }
        
        # 1. 验证证书编号
        cert_no = certificate_data.get('certificate_no', '')
        is_valid, message = self.validate_certificate_no(cert_no)
        results['validations'].append({
            'type': 'certificate_no',
            'is_valid': is_valid,
            'message': message,
        })
        if not is_valid:
            results['is_valid'] = False
            results['errors'].append(message)
        
        # 2. 验证有效期
        issue_date = certificate_data.get('issue_date')
        expiry_date = certificate_data.get('expiry_date')
        
        if issue_date and expiry_date:
            is_valid, message = self.validate_expiry_date(issue_date, expiry_date)
            results['validations'].append({
                'type': 'expiry_date',
                'is_valid': is_valid,
                'message': message,
            })
            if not is_valid:
                results['is_valid'] = False
                results['errors'].append(message)
            elif '即将' in message:
                results['warnings'].append(message)
        
        # 3. 验证文件哈希（如果提供了文件内容）
        if file_content and 'file_hash' in certificate_data:
            is_valid, details = self.validate_file_hash(
                file_content,
                certificate_data['file_hash']
            )
            results['validations'].append({
                'type': 'file_hash',
                'is_valid': is_valid,
                'details': details,
            })
            if not is_valid:
                results['is_valid'] = False
                results['errors'].append(details.get('message', '文件哈希验证失败'))
        
        # 4. 验证数字签名（如果有）
        if 'digital_signature' in certificate_data and certificate_data['digital_signature']:
            data_to_sign = cert_no
            signature = certificate_data['digital_signature']
            
            is_valid, message = self.validate_digital_signature(data_to_sign, signature)
            results['validations'].append({
                'type': 'digital_signature',
                'is_valid': is_valid,
                'message': message,
            })
            if not is_valid:
                results['warnings'].append(message)
        
        # 5. 验证二维码（如果有）
        if 'qr_code_data' in certificate_data and certificate_data['qr_code_data']:
            is_valid, message = self.validate_qr_code(
                certificate_data['qr_code_data'],
                cert_no
            )
            results['validations'].append({
                'type': 'qr_code',
                'is_valid': is_valid,
                'message': message,
            })
            if not is_valid:
                results['warnings'].append(message)
        
        # 6. 验证防伪验证码（如果有）
        if 'verification_code' in certificate_data and certificate_data['verification_code']:
            is_valid, message = self.validate_verification_code(
                certificate_data['verification_code'],
                cert_no
            )
            results['validations'].append({
                'type': 'verification_code',
                'is_valid': is_valid,
                'message': message,
            })
            if not is_valid:
                results['warnings'].append(message)
        
        # 生成总结消息
        if results['is_valid']:
            if results['warnings']:
                results['summary'] = f"证书验证通过，但有 {len(results['warnings'])} 个警告"
            else:
                results['summary'] = "证书验证通过，所有检查项均正常"
        else:
            results['summary'] = f"证书验证失败，发现 {len(results['errors'])} 个错误"
        
        return results
    
    def generate_certificate_fingerprint(self, certificate_data: Dict[str, Any]) -> str:
        """
        生成证书指纹（用于唯一标识）
        
        Args:
            certificate_data: 证书数据
            
        Returns:
            str: 证书指纹（SHA256哈希）
        """
        # 提取关键字段
        key_fields = [
            certificate_data.get('certificate_no', ''),
            certificate_data.get('issuing_authority', ''),
            str(certificate_data.get('issue_date', '')),
            certificate_data.get('holder_name', ''),
        ]
        
        # 拼接并计算哈希
        data = '|'.join(key_fields)
        fingerprint = hashlib.sha256(data.encode('utf-8')).hexdigest()
        
        return fingerprint


# 全局验证器实例
_certificate_validator: Optional[CertificateValidator] = None


def get_certificate_validator(secret_key: Optional[str] = None) -> CertificateValidator:
    """
    获取证书验证器单例
    
    Args:
        secret_key: 密钥（可选）
        
    Returns:
        CertificateValidator: 证书验证器实例
    """
    global _certificate_validator
    
    if _certificate_validator is None:
        _certificate_validator = CertificateValidator(secret_key=secret_key)
    
    return _certificate_validator
