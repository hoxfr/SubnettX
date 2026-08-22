import fitz
import cv2
import numpy as np
import sys

pdf_path = sys.argv[1]
doc = fitz.open(pdf_path)

def get_page_image(page_idx):
    page = doc[page_idx]
    pix = page.get_pixmap()
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def find_text_bbox(img, text_color_approx=(30, 30, 30), tolerance=20):
    # Find pixels matching the text color roughly
    lower = np.array([max(0, c - tolerance) for c in text_color_approx])
    upper = np.array([min(255, c + tolerance) for c in text_color_approx])
    mask = cv2.inRange(img, lower, upper)
    
    # We expect text to be clustered. Let's find contours.
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
        
    # Get bounding box of all contours
    x_min, y_min = img.shape[1], img.shape[0]
    x_max, y_max = 0, 0
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 1000 or h > 1000: # Ignore giant borders
            continue
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)
        
    return (x_min, y_min, x_max, y_max)

print("Slide 3:")
img3 = get_page_image(2)
print("Image shape:", img3.shape)
# Look for text in the right half
right_half = img3[:, img3.shape[1]//2:]
bbox3 = find_text_bbox(right_half)
if bbox3:
    print(f"Text in right half: {bbox3[0] + img3.shape[1]//2}, {bbox3[1]}, {bbox3[2] + img3.shape[1]//2}, {bbox3[3]}")

print("Slide 8:")
img8 = get_page_image(7)
# Look for text in the left third
left_third = img8[:, :img8.shape[1]//3]
bbox8 = find_text_bbox(left_third)
if bbox8:
    print(f"Text in left third: {bbox8}")

