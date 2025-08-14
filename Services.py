import os
import fitz  # PyMuPDF
import docx
from PIL import Image
from io import BytesIO

# ---------------- إعداد مجلدات الإخراج ----------------
output_dir = "extracted_content"
texts_dir = os.path.join(output_dir, "texts")
images_dir = os.path.join(output_dir, "images")
os.makedirs(texts_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# ---------------- دالة تنظيف النصوص ----------------
def clean_text(text):
    return " ".join(text.split())

# ---------------- دالة تكبير الصورة ----------------
def save_enhanced_image(img, path, scale=4.17):  # تحويل 72 DPI إلى ~300 DPI
    width, height = img.size
    img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    img.save(path, format="PNG")

# ---------------- استخراج من PDF ----------------
def extract_from_pdf(file_path):
    pdf = fitz.open(file_path)
    for page_num, page in enumerate(pdf, start=1):
        elements = []
        image_counter = 1

        # استخراج النصوص مع مواقعها
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            if block_type == 0 and text.strip():
                elements.append({"type": "text", "y": y0, "x": x0, "content": clean_text(text)})

        # استخراج الصور مع مواقعها
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            img_pil = Image.open(BytesIO(image_bytes))
            image_name = f"page{page_num}_image{image_counter}.png"
            image_path = os.path.join(images_dir, image_name)
            save_enhanced_image(img_pil, image_path)
            elements.append({"type": "image", "y": 0, "x": 0, "content": f"[{image_name}]"})
            image_counter += 1

        # ترتيب العناصر حسب الموقع (y ثم x)
        elements_sorted = sorted(elements, key=lambda e: (e["y"], e["x"]))
        final_text = "\n".join([e["content"] for e in elements_sorted]).rstrip()

        # حفظ النصوص
        text_file = os.path.join(texts_dir, f"page{page_num}.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(final_text)

# ---------------- استخراج من Word ----------------
def extract_from_word(file_path):
    doc = docx.Document(file_path)
    text_blocks = []
    image_counter = 1
    page_num = 1  # Word لا يحتوي على صفحات فعلية

    # استخراج النصوص
    for para in doc.paragraphs:
        txt = clean_text(para.text)
        if txt:
            text_blocks.append({"type": "text", "content": txt})

    # استخراج الصور من العلاقات
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            img = Image.open(BytesIO(image_data))
            image_name = f"page{page_num}_image{image_counter}.png"
            image_path = os.path.join(images_dir, image_name)
            save_enhanced_image(img, image_path)
            text_blocks.append({"type": "image", "content": f"[{image_name}]"})
            image_counter += 1

    # دمج النصوص والصور
    final_text = "\n".join([block["content"] for block in text_blocks]).rstrip()

    # حفظ النصوص
    text_file = os.path.join(texts_dir, f"page{page_num}.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(final_text)

# ---------------- Main ----------------
if __name__ == "__main__":
    file_name = input("Enter the file name (PDF or DOCX): ").strip()
    file_path = os.path.abspath(file_name)

    if file_name.lower().endswith(".pdf"):
        extract_from_pdf(file_path)
        print("✅ PDF extraction completed.")
    elif file_name.lower().endswith(".docx"):
        extract_from_word(file_path)
        print("✅ Word extraction completed.")
    else:
        print("❌ Unsupported file format. Use PDF or DOCX.")
