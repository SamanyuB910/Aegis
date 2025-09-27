import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os

from models.pydantic_schemas import OCRResult, ForgeryAnalysis

logger = logging.getLogger(__name__)

class ReceiptOCRAnalyzer:
    """
    OCR and forgery detection service for receipt analysis.
    
    Features:
    - Text extraction using Tesseract OCR
    - Receipt field parsing (amount, merchant, date)
    - Forgery detection using image analysis
    - Anomaly detection in receipt content
    """
    
    def __init__(self):
        # Set Tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Common receipt patterns
        self.amount_patterns = [
            r'\$[\d,]+\.?\d{0,2}',  # $123.45, $1,234.56
            r'TOTAL[\s:]+\$?[\d,]+\.?\d{0,2}',  # TOTAL: $123.45
            r'AMOUNT[\s:]+\$?[\d,]+\.?\d{0,2}',  # AMOUNT: $123.45
            r'[\d,]+\.?\d{2}\s*USD',  # 123.45 USD
        ]
        
        self.merchant_patterns = [
            r'^[A-Z\s&\-\'\.]{3,}$',  # All caps merchant names
            r'(?i)store|shop|mart|market|restaurant|cafe|gas|fuel',  # Common business words
        ]
        
        self.date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',   # YYYY/MM/DD
            r'[A-Za-z]{3}\s+\d{1,2},?\s+\d{4}',  # Jan 15, 2024
        ]
        
        logger.info("✅ Receipt OCR Analyzer initialized")
    
    async def analyze_receipt(self, image_path: str) -> OCRResult:
        """
        Extract text and structured data from receipt image
        """
        try:
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image_path)
            
            # Extract text using OCR
            ocr_text = pytesseract.image_to_string(processed_image, config='--oem 3 --psm 6')
            
            # Calculate OCR confidence
            ocr_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            confidence = avg_confidence / 100.0  # Convert to 0-1 scale
            
            # Extract structured fields
            extracted_fields = self._extract_receipt_fields(ocr_text)
            
            # Detect anomalies
            anomalies = self._detect_text_anomalies(ocr_text, extracted_fields)
            
            logger.info(f"OCR completed: confidence={confidence:.3f}, anomalies={len(anomalies)}")
            
            return OCRResult(
                text=ocr_text,
                confidence=confidence,
                extracted_fields=extracted_fields,
                anomalies=anomalies
            )
            
        except Exception as e:
            logger.error(f"❌ OCR analysis failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                extracted_fields={},
                anomalies=["OCR processing failed"]
            )
    
    def _preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image for better OCR results"""
        try:
            # Load image with PIL
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Convert to OpenCV format for preprocessing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(cleaned)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(1.5)
            
            return processed_image
            
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            return Image.open(image_path)
    
    def _extract_receipt_fields(self, ocr_text: str) -> Dict[str, Any]:
        """Extract structured fields from OCR text"""
        fields = {}
        
        try:
            # Extract amount
            amount = self._extract_amount(ocr_text)
            if amount:
                fields['amount'] = amount
            
            # Extract merchant name
            merchant = self._extract_merchant(ocr_text)
            if merchant:
                fields['merchant'] = merchant
            
            # Extract date
            date = self._extract_date(ocr_text)
            if date:
                fields['date'] = date
            
            # Extract other fields
            fields.update(self._extract_additional_fields(ocr_text))
            
        except Exception as e:
            logger.error(f"❌ Field extraction failed: {e}")
        
        return fields
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract transaction amount from text"""
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Process the first match
                amount_str = matches[0]
                # Remove non-numeric characters except decimal point
                amount_str = re.sub(r'[^\d\.]', '', amount_str)
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant name from text"""
        lines = text.strip().split('\n')
        
        # Usually merchant name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3:  # Minimum length for merchant name
                # Check if line looks like a merchant name
                if re.match(r'^[A-Z\s&\-\'\.]{3,}$', line):
                    return line
                # Check for common business keywords
                if any(keyword in line.lower() for keyword in ['store', 'shop', 'mart', 'market', 'restaurant', 'cafe']):
                    return line
        
        return None
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract transaction date from text"""
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                date_str = matches[0]
                # Try to parse the date
                try:
                    # Try different date formats
                    for date_format in ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d']:
                        try:
                            return datetime.strptime(date_str, date_format)
                        except ValueError:
                            continue
                    
                    # Try parsing month names
                    if re.match(r'[A-Za-z]{3}\s+\d{1,2},?\s+\d{4}', date_str):
                        return datetime.strptime(date_str, '%b %d, %Y')
                        
                except Exception:
                    continue
        
        return None
    
    def _extract_additional_fields(self, text: str) -> Dict[str, Any]:
        """Extract additional receipt fields"""
        fields = {}
        
        # Extract tax amount
        tax_match = re.search(r'TAX[\s:]+\$?[\d,]+\.?\d{0,2}', text, re.IGNORECASE)
        if tax_match:
            tax_str = re.sub(r'[^\d\.]', '', tax_match.group())
            try:
                fields['tax'] = float(tax_str)
            except ValueError:
                pass
        
        # Extract tip amount
        tip_match = re.search(r'TIP[\s:]+\$?[\d,]+\.?\d{0,2}', text, re.IGNORECASE)
        if tip_match:
            tip_str = re.sub(r'[^\d\.]', '', tip_match.group())
            try:
                fields['tip'] = float(tip_str)
            except ValueError:
                pass
        
        # Extract receipt/transaction ID
        id_match = re.search(r'(?:RECEIPT|TRANS|REF)[\s#:]*([A-Z0-9]{6,})', text, re.IGNORECASE)
        if id_match:
            fields['receipt_id'] = id_match.group(1)
        
        return fields
    
    def _detect_text_anomalies(self, ocr_text: str, extracted_fields: Dict[str, Any]) -> List[str]:
        """Detect anomalies in OCR text and extracted fields"""
        anomalies = []
        
        # Check for missing essential fields
        if 'amount' not in extracted_fields:
            anomalies.append("No transaction amount detected")
        
        if 'merchant' not in extracted_fields:
            anomalies.append("No merchant name detected")
        
        # Check for unrealistic amounts
        if 'amount' in extracted_fields:
            amount = extracted_fields['amount']
            if amount <= 0:
                anomalies.append("Invalid transaction amount")
            elif amount > 50000:  # Unusually high amount
                anomalies.append("Unusually high transaction amount")
        
        # Check text quality
        if len(ocr_text.strip()) < 20:
            anomalies.append("Very short OCR text - poor image quality")
        
        # Check for suspicious patterns
        if len(re.findall(r'[^\x00-\x7F]', ocr_text)) > 10:  # Too many non-ASCII characters
            anomalies.append("Excessive non-standard characters")
        
        # Check for repeated patterns (potential forgery)
        lines = ocr_text.split('\n')
        if len(lines) > len(set(lines)) * 1.5:  # Many duplicate lines
            anomalies.append("Suspicious repeated text patterns")
        
        return anomalies
    
    async def detect_forgery(self, image_path: str, ocr_result: OCRResult) -> ForgeryAnalysis:
        """
        Detect if receipt appears to be forged using image analysis
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return ForgeryAnalysis(
                    is_forged=False,
                    confidence=0.0,
                    reasons=["Could not load image"],
                    technical_details={}
                )
            
            forgery_score = 0.0
            reasons = []
            technical_details = {}
            
            # 1. Check image quality metrics
            quality_score = self._analyze_image_quality(image)
            technical_details['quality_metrics'] = quality_score
            
            if quality_score['sharpness'] < 0.3:
                forgery_score += 0.2
                reasons.append("Image appears artificially blurred")
            
            if quality_score['compression_artifacts'] > 0.7:
                forgery_score += 0.3
                reasons.append("High compression artifacts detected")
            
            # 2. Check for copy-paste artifacts
            copy_paste_score = self._detect_copy_paste_artifacts(image)
            technical_details['copy_paste_analysis'] = copy_paste_score
            
            if copy_paste_score > 0.6:
                forgery_score += 0.4
                reasons.append("Potential copy-paste manipulation detected")
            
            # 3. Check text consistency
            text_consistency = self._analyze_text_consistency(ocr_result.text)
            technical_details['text_consistency'] = text_consistency
            
            if not text_consistency['fonts_consistent']:
                forgery_score += 0.2
                reasons.append("Inconsistent font patterns")
            
            if not text_consistency['alignment_consistent']:
                forgery_score += 0.1
                reasons.append("Inconsistent text alignment")
            
            # 4. Check for digital manipulation signs
            manipulation_score = self._detect_digital_manipulation(image)
            technical_details['manipulation_analysis'] = manipulation_score
            
            if manipulation_score > 0.5:
                forgery_score += 0.3
                reasons.append("Digital manipulation signatures detected")
            
            # 5. Content-based checks
            if len(ocr_result.anomalies) > 3:
                forgery_score += 0.2
                reasons.append("Multiple content anomalies detected")
            
            # Final assessment
            is_forged = forgery_score > 0.6
            confidence = min(1.0, forgery_score)
            
            logger.info(f"Forgery analysis: score={forgery_score:.3f}, forged={is_forged}")
            
            return ForgeryAnalysis(
                is_forged=is_forged,
                confidence=confidence,
                reasons=reasons,
                technical_details=technical_details
            )
            
        except Exception as e:
            logger.error(f"❌ Forgery detection failed: {e}")
            return ForgeryAnalysis(
                is_forged=False,
                confidence=0.0,
                reasons=["Analysis failed"],
                technical_details={"error": str(e)}
            )
    
    def _analyze_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze image quality metrics"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var() / 10000  # Normalize
        
        # Compression artifacts (simplified)
        # Look for blocking artifacts by analyzing frequency domain
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift))
        compression_artifacts = np.std(magnitude_spectrum) / 10  # Simplified metric
        
        return {
            "sharpness": min(1.0, sharpness),
            "compression_artifacts": min(1.0, compression_artifacts),
            "resolution": image.shape[0] * image.shape[1]
        }
    
    def _detect_copy_paste_artifacts(self, image: np.ndarray) -> float:
        """Detect copy-paste artifacts (simplified implementation)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for duplicate regions using template matching
        # This is a simplified version - production would use more sophisticated methods
        height, width = gray.shape
        
        # Sample small regions and look for duplicates
        region_size = 50
        duplicate_score = 0.0
        
        try:
            for i in range(0, height - region_size, region_size):
                for j in range(0, width - region_size, region_size):
                    template = gray[i:i+region_size, j:j+region_size]
                    
                    # Search for similar regions in the rest of the image
                    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                    locations = np.where(result >= 0.9)  # High similarity threshold
                    
                    if len(locations[0]) > 1:  # Found duplicates
                        duplicate_score += 0.1
            
            return min(1.0, duplicate_score)
            
        except Exception:
            return 0.0
    
    def _analyze_text_consistency(self, text: str) -> Dict[str, bool]:
        """Analyze text consistency patterns"""
        lines = text.strip().split('\n')
        
        # Check font consistency (simplified - based on character patterns)
        fonts_consistent = True
        alignment_consistent = True
        
        # Look for mixed case patterns that might indicate different sources
        case_patterns = []
        for line in lines:
            if line.strip():
                upper_ratio = sum(1 for c in line if c.isupper()) / len(line)
                case_patterns.append(upper_ratio)
        
        if len(case_patterns) > 1:
            case_variance = np.var(case_patterns)
            if case_variance > 0.3:  # High variance in capitalization
                fonts_consistent = False
        
        # Check alignment consistency (simplified)
        leading_spaces = []
        for line in lines:
            if line.strip():
                leading_spaces.append(len(line) - len(line.lstrip()))
        
        if len(leading_spaces) > 1:
            alignment_variance = np.var(leading_spaces)
            if alignment_variance > 10:  # High variance in indentation
                alignment_consistent = False
        
        return {
            "fonts_consistent": fonts_consistent,
            "alignment_consistent": alignment_consistent,
            "case_patterns": case_patterns,
            "alignment_patterns": leading_spaces
        }
    
    def _detect_digital_manipulation(self, image: np.ndarray) -> float:
        """Detect signs of digital manipulation"""
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            manipulation_score = 0.0
            
            # Check for unusual color distributions
            for channel in range(3):
                hist = cv2.calcHist([hsv], [channel], None, [256], [0, 256])
                # Look for artificial peaks or gaps in histogram
                hist_variance = np.var(hist)
                if hist_variance < 1000:  # Too uniform
                    manipulation_score += 0.1
            
            # Check for edge inconsistencies
            edges = cv2.Canny(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            if edge_density < 0.01 or edge_density > 0.3:  # Unusual edge density
                manipulation_score += 0.2
            
            return min(1.0, manipulation_score)
            
        except Exception:
            return 0.0