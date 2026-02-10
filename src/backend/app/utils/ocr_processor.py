"""
OCR处理工具 - 证书内容识别
支持PDF和图片格式的文本提取和OCR识别
"""
import io
import re
from typing import Optional, Dict, Any, BinaryIO
from datetime import date, datetime
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class OCRProcessor:
    """OCR处理器 - 证书内容识别"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = 'chi_sim+eng'):
        """
        初始化OCR处理器
        
        Args:
            tesseract_cmd: Tesseract可执行文件路径（可选）
            lang: OCR语言，默认中文+英文
        """
        self.lang = lang
        
        if TESSERACT_AVAILABLE and tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        从PDF提取文本
        
        Args:
            file_content: PDF文件内容
            
        Returns:
            str: 提取的文本
        """
        text = ""
        
        # 优先使用pdfplumber（更准确）
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                
                if text.strip():
                    return text.strip()
            except Exception as e:
                print(f"pdfplumber提取失败: {e}")
        
        # 备用方案：使用PyMuPDF
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(stream=file_content, filetype="pdf")
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                
                if text.strip():
                    return text.strip()
            except Exception as e:
                print(f"PyMuPDF提取失败: {e}")
        
        return text.strip()
    
    def extract_text_from_image(self, file_content: bytes) -> str:
        """
        从图片提取文本（OCR）
        
        Args:
            file_content: 图片文件内容
            
        Returns:
            str: 识别的文本
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract OCR未安装，无法识别图片文本")
        
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # 图片预处理（提高识别率）
            image = self._preprocess_image(image)
            
            # OCR识别
            text = pytesseract.image_to_string(image, lang=self.lang)
            
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        图片预处理（提高OCR识别率）
        
        Args:
            image: PIL图片对象
            
        Returns:
            Image: 处理后的图片
        """
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 调整大小（如果图片太小）
        width, height = image.size
        if width < 1000 or height < 1000:
            scale = max(1000 / width, 1000 / height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def extract_text(self, file_content: bytes, file_format: str) -> str:
        """
        根据文件格式提取文本
        
        Args:
            file_content: 文件内容
            file_format: 文件格式（pdf/jpg/jpeg/png）
            
        Returns:
            str: 提取的文本
        """
        file_format = file_format.lower().replace('.', '')
        
        if file_format == 'pdf':
            return self.extract_text_from_pdf(file_content)
        elif file_format in ['jpg', 'jpeg', 'png']:
            return self.extract_text_from_image(file_content)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")
    
    def parse_certificate_info(self, text: str) -> Dict[str, Any]:
        """
        从文本中解析证书信息
        
        Args:
            text: 证书文本内容
            
        Returns:
            dict: 解析出的证书信息
        """
        info = {
            'certificate_no': None,
            'holder_name': None,
            'issue_date': None,
            'expiry_date': None,
            'issuing_authority': None,
            'id_number': None,
        }
        
        # 证书编号模式
        cert_no_patterns = [
            r'证书编号[：:]\s*([A-Z0-9\-]+)',
            r'编号[：:]\s*([A-Z0-9\-]+)',
            r'Certificate\s+No[.:]?\s*([A-Z0-9\-]+)',
            r'No[.:]?\s*([A-Z0-9\-]+)',
        ]
        
        for pattern in cert_no_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['certificate_no'] = match.group(1).strip()
                break
        
        # 持有人姓名模式
        holder_patterns = [
            r'持有人[：:]\s*([^\n\r]+)',
            r'姓名[：:]\s*([^\n\r]+)',
            r'Holder[：:]\s*([^\n\r]+)',
            r'Name[：:]\s*([^\n\r]+)',
        ]
        
        for pattern in holder_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['holder_name'] = match.group(1).strip()
                break
        
        # 身份证号/组织机构代码模式
        id_patterns = [
            r'身份证号[：:]\s*([0-9X]{15,18})',
            r'统一社会信用代码[：:]\s*([A-Z0-9]{18})',
            r'组织机构代码[：:]\s*([A-Z0-9\-]{8,})',
            r'ID\s+Number[：:]\s*([A-Z0-9]+)',
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['id_number'] = match.group(1).strip()
                break
        
        # 颁发日期模式
        issue_date_patterns = [
            r'颁发日期[：:]\s*(\d{4}[年\-/]\d{1,2}[月\-/]\d{1,2}日?)',
            r'发证日期[：:]\s*(\d{4}[年\-/]\d{1,2}[月\-/]\d{1,2}日?)',
            r'Issue\s+Date[：:]\s*(\d{4}[\-/]\d{1,2}[\-/]\d{1,2})',
        ]
        
        for pattern in issue_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                info['issue_date'] = self._parse_date(date_str)
                break
        
        # 有效期模式
        expiry_date_patterns = [
            r'有效期至[：:]\s*(\d{4}[年\-/]\d{1,2}[月\-/]\d{1,2}日?)',
            r'有效期[：:]\s*(\d{4}[年\-/]\d{1,2}[月\-/]\d{1,2}日?)',
            r'Expiry\s+Date[：:]\s*(\d{4}[\-/]\d{1,2}[\-/]\d{1,2})',
            r'Valid\s+Until[：:]\s*(\d{4}[\-/]\d{1,2}[\-/]\d{1,2})',
        ]
        
        for pattern in expiry_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                info['expiry_date'] = self._parse_date(date_str)
                break
        
        # 颁发机构模式
        authority_patterns = [
            r'颁发机构[：:]\s*([^\n\r]+)',
            r'发证机关[：:]\s*([^\n\r]+)',
            r'Issuing\s+Authority[：:]\s*([^\n\r]+)',
        ]
        
        for pattern in authority_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['issuing_authority'] = match.group(1).strip()
                break
        
        return info
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            date: 日期对象，解析失败返回None
        """
        # 清理日期字符串
        date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
        date_str = date_str.replace('/', '-')
        
        # 尝试多种日期格式
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d',
            '%Y%m%d',
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.date()
            except ValueError:
                continue
        
        return None
    
    def generate_thumbnail(self, file_content: bytes, file_format: str, 
                          max_width: int = 300, max_height: int = 400) -> Optional[bytes]:
        """
        生成缩略图
        
        Args:
            file_content: 文件内容
            file_format: 文件格式
            max_width: 最大宽度
            max_height: 最大高度
            
        Returns:
            bytes: 缩略图内容（JPEG格式），失败返回None
        """
        try:
            # PDF转图片
            if file_format.lower() == 'pdf':
                if not PYMUPDF_AVAILABLE:
                    return None
                
                doc = fitz.open(stream=file_content, filetype="pdf")
                page = doc[0]  # 第一页
                
                # 渲染为图片
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍缩放
                img_data = pix.tobytes("jpeg")
                doc.close()
                
                # 转换为PIL Image
                image = Image.open(io.BytesIO(img_data))
            else:
                # 直接打开图片
                image = Image.open(io.BytesIO(file_content))
            
            # 生成缩略图
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # 转换为JPEG
            output = io.BytesIO()
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            image.save(output, format='JPEG', quality=85)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return None


# 全局OCR处理器实例
_ocr_processor: Optional[OCRProcessor] = None


def get_ocr_processor(tesseract_cmd: Optional[str] = None) -> OCRProcessor:
    """
    获取OCR处理器单例
    
    Args:
        tesseract_cmd: Tesseract可执行文件路径（可选）
        
    Returns:
        OCRProcessor: OCR处理器实例
    """
    global _ocr_processor
    
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor(tesseract_cmd=tesseract_cmd)
    
    return _ocr_processor
