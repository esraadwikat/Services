import os
import fitz
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf2image import convert_from_path
import pytesseract

# --- مسار Tesseract OCR (عدّل حسب مسارك إذا لزم) ---
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pdf_path = r"C:\Users\Sabitu\chunk\Biology.pdf"
output_csv = "biology_chunks_with_pages.csv"

if not os.path.exists(pdf_path):
    print(f"الملف غير موجود: {pdf_path}")
    exit()

# --- محاولة استخراج النصوص مباشرة ---
pages_text = []
with fitz.open(pdf_path) as pdf:
    for i, page in enumerate(pdf):
        text = page.get_text().strip()
        print(f"[PyMuPDF] صفحة {i+1}: {len(text)} حرف")
        if text:
            pages_text.append({"page_number": i+1, "text": text})

# --- إذا لم يوجد نص، استخدم OCR ---
#if not pages_text:
  #  print("لم يتم استخراج نصوص مباشرة، سيتم استخدام OCR...")
   # images = convert_from_path(pdf_path)
    #for i, img in enumerate(images):
       # text = pytesseract.image_to_string(img).strip()
       # print(f"[OCR] صفحة {i+1}: {len(text)} حرف")
        #if text:
           # pages_text.append({"page_number": i+1, "text": text})

if not pages_text:
    print("لم يتم استخراج أي نصوص من الملف حتى بعد OCR.")
    exit()

# --- تقسيم النصوص إلى Chunks ---
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

all_chunks = []
for page in pages_text:
    chunks = splitter.split_text(page["text"])
    for chunk in chunks:
        all_chunks.append({"page_number": page["page_number"], "chunk": chunk})

# --- حفظ في CSV ---
df = pd.DataFrame(all_chunks)
df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"تم حفظ {len(all_chunks)} جزء في الملف: {output_csv}")

# --- عرض أول جزء كمثال ---
print("أول جزء:")
print(all_chunks[0])