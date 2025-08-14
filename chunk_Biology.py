import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf2image import convert_from_path
import pytesseract

# --- مسار Tesseract OCR (عدّل حسب مسارك إذا لزم) ---
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pdf_path = r"C:\Users\Sabitu\chunk\Biology.pdf"  # مسار ملف PDF
output_folder = r"C:\Users\Sabitu\chunk\chunks"  # المجلد الذي سيتم حفظ الملفات فيه

# --- التأكد من وجود الملف ---
if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit()

# --- إنشاء المجلد إذا لم يكن موجود ---
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# --- استخراج النصوص مباشرة باستخدام PyMuPDF ---
pages_text = []
with fitz.open(pdf_path) as pdf:
    for i, page in enumerate(pdf):
        text = page.get_text().strip()
        print(f"[PyMuPDF] Page {i+1}: {len(text)} characters")
        if text:
            pages_text.append({"page_number": i+1, "text": text})

# --- إذا لم يتم استخراج أي نصوص، استخدم OCR ---
if not pages_text:
    print("No text found with PyMuPDF, using OCR...")
    images = convert_from_path(pdf_path)
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img).strip()
        print(f"[OCR] Page {i+1}: {len(text)} characters")
        if text:
            pages_text.append({"page_number": i+1, "text": text})

if not pages_text:
    print("No text could be extracted from the PDF even after OCR.")
    exit()

# --- تقسيم النصوص إلى chunks ---
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

# --- حفظ كل chunk في ملف نصي مستقل ---
for page in pages_text:
    page_folder = os.path.join(output_folder, f"page_{page['page_number']}")
    if not os.path.exists(page_folder):
        os.makedirs(page_folder)
    
    chunks = splitter.split_text(page["text"])
    for idx, chunk in enumerate(chunks, start=1):
        chunk_file = os.path.join(page_folder, f"chunk_{idx}.txt")
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(chunk)
    
    print(f"Saved {len(chunks)} chunks for page {page['page_number']}")

print("All chunks saved successfully!")