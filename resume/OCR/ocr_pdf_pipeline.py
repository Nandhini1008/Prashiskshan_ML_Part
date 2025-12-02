"""
Focused PDF OCR module: CRAFT detection + PaddleOCR recognition
Only contains the functions needed for processing PDFs to text using
- pdf2image + CRAFT + PaddleOCR (preferred)
- PyPDF2 fallback (direct text extraction)

This module intentionally omits LLM, TTS, and camera/image batch helpers.
"""

import os
import cv2
import torch
import numpy as np
from datetime import datetime
from collections import OrderedDict

# PDF conversion & fallback
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except Exception:
    PDF2IMAGE_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False

# PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except Exception:
    PADDLEOCR_AVAILABLE = False

# Try to import local CRAFT implementation if present
try:
    import sys
    craft_path = os.path.join(os.path.dirname(__file__), 'CRAFT_pytorch')
    if craft_path not in sys.path:
        sys.path.insert(0, craft_path)
    from craft import CRAFT
    CRAFT_MODULE_AVAILABLE = True
except Exception:
    CRAFT_MODULE_AVAILABLE = False


class CRAFTDetector:
    """CRAFT-based text detector (minimal set of methods used for PDF pages).
    If CRAFT model or module is missing, the detector falls back to simple image methods.
    """

    def __init__(self, use_cuda=True, model_paths=None):
        self.device = torch.device('cuda' if use_cuda and torch.cuda.is_available() else 'cpu')
        self.net = self._load_craft_model(model_paths)
        if self.net is not None:
            self.net.to(self.device)
            self.net.eval()

    def _load_craft_model(self, model_paths=None):
        if not CRAFT_MODULE_AVAILABLE:
            return None
        try:
            model = CRAFT()
            # search default locations
            candidates = model_paths or [
                'craft_mlt_25k.pth',
                os.path.join(os.path.dirname(__file__), 'craft_mlt_25k.pth'),
                r'D:\trafficdl\OCR\craft_mlt_25k.pth'
            ]
            model_path = None
            for p in candidates:
                if os.path.exists(p):
                    model_path = p
                    break
            if model_path is None:
                return None
            state_dict = torch.load(model_path, map_location='cpu')
            state_dict = self._copy_state_dict(state_dict)
            model.load_state_dict(state_dict)
            return model
        except Exception:
            return None

    def _copy_state_dict(self, state_dict):
        new_state = OrderedDict()
        try:
            for k, v in state_dict.items():
                if k.startswith('module.'):
                    new_state[k[7:]] = v
                else:
                    new_state[k] = v
        except Exception:
            return state_dict
        return new_state

    def detect_text_regions(self, image, text_threshold=0.3, link_threshold=0.2, low_text=0.2):
        """Return list of boxes (each box is list of 8 ints: x1,y1,x2,y2,x3,y3,x4,y4)
        If CRAFT not available, use a permissive fallback detector.
        """
        if self.net is None:
            return self._fallback_text_detection(image)

        try:
            img_resized, target_ratio, size_heatmap = self._resize_aspect_ratio(image, square_size=1280)
            x = self._normalize_mean_variance(img_resized)
            x = torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0).float().to(self.device)
            with torch.no_grad():
                y, _ = self.net(x)
            score_text = y[0, :, :, 0].cpu().numpy()
            score_link = y[0, :, :, 1].cpu().numpy()
            boxes = self._get_boxes(score_text, score_link, text_threshold, link_threshold, low_text)
            boxes = self._adjust_result_coordinates(boxes, target_ratio, size_heatmap)
            return boxes
        except Exception:
            return self._fallback_text_detection(image)

    def _resize_aspect_ratio(self, img, square_size=1280, interpolation=cv2.INTER_LINEAR):
        h, w, _ = img.shape
        ratio = min(square_size / float(h), square_size / float(w))
        target_h = int(h * ratio)
        target_w = int(w * ratio)
        proc = cv2.resize(img, (target_w, target_h), interpolation=interpolation)
        target_h32 = target_h + (32 - target_h % 32) if target_h % 32 != 0 else target_h
        target_w32 = target_w + (32 - target_w % 32) if target_w % 32 != 0 else target_w
        resized = np.zeros((target_h32, target_w32, 3), dtype=np.uint8)
        resized[0:target_h, 0:target_w, :] = proc
        size_heatmap = (int(target_w32 / 2), int(target_h32 / 2))
        return resized, ratio, size_heatmap

    def _normalize_mean_variance(self, img, mean=(0.485, 0.456, 0.406), variance=(0.229, 0.224, 0.225)):
        img = img.astype(np.float32) / 255.0
        img -= np.array(mean)
        img /= np.array(variance)
        return img

    def _get_boxes(self, score_text, score_link, text_threshold, link_threshold, low_text):
        text_score = score_text > text_threshold
        link_score = score_link > link_threshold
        text_score_comb = np.clip(text_score + link_score, 0, 1)
        text_score_comb = (text_score_comb * 255).astype(np.uint8)
        contours, _ = cv2.findContours(text_score_comb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 5:
                continue
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box).reshape(-1).tolist()
            boxes.append(box)
        return boxes

    def _adjust_result_coordinates(self, boxes, ratio, size_heatmap):
        if not boxes:
            return []
        boxes = np.array(boxes)
        boxes = boxes * 2
        boxes = boxes / ratio
        return boxes.astype(np.int32).tolist()

    def _fallback_text_detection(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 15, 3)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boxes = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w < 10 or h < 8:
                    continue
                box = [x, y, x+w, y, x+w, y+h, x, y+h]
                boxes.append(box)
            return boxes
        except Exception:
            return []


def sort_boxes_reading_order(boxes, line_height_threshold_ratio=0.5):
    if not boxes:
        return []
    indexed = []
    for idx, box in enumerate(boxes):
        arr = np.array(box).reshape(4, 2)
        y_min = int(arr[:, 1].min())
        y_max = int(arr[:, 1].max())
        x_min = int(arr[:, 0].min())
        center_y = (y_min + y_max) / 2
        center_x = (x_min + int(arr[:, 0].max())) / 2
        height = y_max - y_min
        indexed.append((idx, center_y, center_x, y_min, y_max, x_min, height, box))
    indexed.sort(key=lambda x: x[1])
    # grouping into lines
    lines = []
    current = [indexed[0]]
    for it in indexed[1:]:
        avg_h = sum([c[6] for c in current]) / len(current)
        dynamic_threshold = avg_h * line_height_threshold_ratio
        avg_y = sum([c[1] for c in current]) / len(current)
        if abs(it[1] - avg_y) <= dynamic_threshold:
            current.append(it)
        else:
            current.sort(key=lambda x: x[2])
            lines.append(current)
            current = [it]
    if current:
        current.sort(key=lambda x: x[2])
        lines.append(current)
    sorted_flat = []
    for line in lines:
        sorted_flat.extend(line)
    return sorted_flat


class PDFTextExtractor:
    """High-level helper for PDF -> text using either PyPDF2 or pdf2image+OCR (CRAFT + PaddleOCR)
    """

    def __init__(self, detector=None, ocr=None):
        self.detector = detector or CRAFTDetector()
        if ocr is None and PADDLEOCR_AVAILABLE:
            # default PaddleOCR initialization
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', rec_batch_num=1)
        else:
            self.ocr = ocr

    def extract_text_from_pdf(self, pdf_path, use_ocr=False):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(pdf_path)
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError('Not a PDF')

        # Direct extraction (fast) when not using OCR
        if not use_ocr and PYPDF2_AVAILABLE:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages = len(reader.pages)
                result = {'file_path': pdf_path, 'total_pages': pages, 'pages': [], 'method': 'PyPDF2'}
                for i, page in enumerate(reader.pages, start=1):
                    txt = page.extract_text() or ''
                    result['pages'].append({'page_number': i, 'text': txt})
                return result

        # OCR-based extraction
        if use_ocr:
            # Prefer pdf2image when available
            if PDF2IMAGE_AVAILABLE:
                try:
                    images = convert_from_path(pdf_path)
                except Exception as e:
                    # pdf2image failed (often due to missing poppler). Try PyPDF2 fallback if available.
                    if PYPDF2_AVAILABLE:
                        # Fallback: extract text via PyPDF2 and return that result
                        with open(pdf_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            pages = len(reader.pages)
                            result = {'file_path': pdf_path, 'total_pages': pages, 'pages': [], 'method': 'PyPDF2_fallback_due_to_pdf2image_error'}
                            for i, page in enumerate(reader.pages, start=1):
                                txt = page.extract_text() or ''
                                result['pages'].append({'page_number': i, 'text': txt})
                            return result
                    # If no fallback possible, raise informative error
                    raise RuntimeError(f"pdf2image failed (is poppler installed and on PATH?). Original error: {e}")

                results = {'file_path': pdf_path, 'total_pages': len(images), 'pages': [], 'method': 'pdf2image+CRAFT+PaddleOCR'}
                for i, pil_img in enumerate(images, start=1):
                    cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    boxes = self.detector.detect_text_regions(cv_image)
                    sorted_boxes = sort_boxes_reading_order(boxes)
                    page_detections = []
                    for order, (idx, cy, cx, y_min, y_max, x_min, height, box) in enumerate(sorted_boxes, start=1):
                        try:
                            arr = np.array(box).reshape(4, 2).astype(int)
                            x1 = max(0, int(arr[:, 0].min()))
                            y1 = max(0, int(arr[:, 1].min()))
                            x2 = min(cv_image.shape[1], int(arr[:, 0].max()))
                            y2 = min(cv_image.shape[0], int(arr[:, 1].max()))
                            if x2 <= x1 or y2 <= y1:
                                continue
                            region = cv_image[y1:y2, x1:x2]
                            if self.ocr is None:
                                text = ''
                                conf = 0.0
                            else:
                                res = self.ocr.ocr(region, cls=True)
                                text = ''
                                conf = 0.0
                                if res and res[0]:
                                    for line in res[0]:
                                        if isinstance(line[1], tuple):
                                            t, c = line[1]
                                        else:
                                            t, c = line[1], 0.0
                                        if t and (c >= conf):
                                            text = t
                                            conf = c
                            detection = {'reading_order': order, 'text': text.strip(), 'confidence': conf, 'box': box}
                            page_detections.append(detection)
                        except Exception:
                            continue
                    results['pages'].append({'page_number': i, 'detections': page_detections, 'total_detections': len(page_detections)})
                return results

            # If pdf2image isn't available, try a PyPDF2 fallback if the user only needs text
            if not PDF2IMAGE_AVAILABLE:
                if PYPDF2_AVAILABLE:
                    with open(pdf_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        pages = len(reader.pages)
                        result = {'file_path': pdf_path, 'total_pages': pages, 'pages': [], 'method': 'PyPDF2_fallback_no_pdf2image'}
                        for i, page in enumerate(reader.pages, start=1):
                            txt = page.extract_text() or ''
                            result['pages'].append({'page_number': i, 'text': txt})
                        return result
                raise RuntimeError('pdf2image (and system poppler) is required for OCR-based PDF extraction and PyPDF2 fallback is not available')

        # If we reach here and nothing applied
        raise RuntimeError('No suitable PDF extraction method available')


# Convenience API
def process_pdf(pdf_path, use_ocr=False, detector=None, ocr=None):
    extractor = PDFTextExtractor(detector=detector, ocr=ocr)
    return extractor.extract_text_from_pdf(pdf_path, use_ocr=use_ocr)
