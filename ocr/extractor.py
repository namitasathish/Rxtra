from PIL import Image
import pytesseract
import io

# Add this line below the imports
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text
