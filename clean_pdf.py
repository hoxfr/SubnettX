import pymupdf
import fitz
import cv2
import numpy as np
from PIL import Image
import io

input_pdf = 'SubnettX_Fixed_Presentation.pdf'
output_pdf = 'SubnettX_Cleaned_Presentation.pdf'

doc = pymupdf.open(input_pdf)
new_doc = pymupdf.open()

for page_num in range(len(doc)):
    page = doc[page_num]
    pix = page.get_pixmap(dpi=150) # Use higher DPI to preserve quality
    
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    
    if pix.n == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    elif pix.n == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
    h, w = img_array.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Define ROI for bottom right (presenter script)
    # The script is usually large text, maybe taking up the bottom right quadrant.
    roi_h, roi_w = int(h * 0.25), int(w * 0.4)
    roi_y, roi_x = h - roi_h, w - roi_w
    
    roi = img_array[roi_y:h, roi_x:w]
    
    # Create mask for text
    # Assuming text is lighter than background
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Adaptive thresholding might be better, or just a simple threshold
    # Since background is ~17,17,17, text is probably > 50
    _, thresh = cv2.threshold(gray_roi, 50, 255, cv2.THRESH_BINARY)
    
    # Dilate mask to ensure text borders are covered
    kernel = np.ones((4,4), np.uint8)
    dilated_mask = cv2.dilate(thresh, kernel, iterations=2)
    
    mask[roi_y:h, roi_x:w] = dilated_mask
    
    # Inpaint
    inpainted = cv2.inpaint(img_array, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    
    # Convert back to PDF page
    inpainted_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(inpainted_rgb)
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr = img_byte_arr.getvalue()
    
    # Add to new PDF
    img_doc = pymupdf.open("pdf", pymupdf.open("image", img_byte_arr).convert_to_pdf())
    new_doc.insert_pdf(img_doc)
    print(f"Processed page {page_num+1}/{len(doc)}")

new_doc.save(output_pdf)
print(f"Saved cleaned PDF to {output_pdf}")
