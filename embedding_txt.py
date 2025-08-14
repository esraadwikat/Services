# -------------------------------
# Biology PDF to SQLite Embeddings (Limited to 10 paragraphs)
# -------------------------------

# تثبيت المكتبات المطلوبة:
# pip install PyMuPDF openai numpy

import fitz  # PyMuPDF
import openai
import sqlite3
import json
import numpy as np
from numpy import dot
from numpy.linalg import norm

# -------------------------------
# 1. إعداد مفتاح OpenAI
# -------------------------------
openai.api_key = "YOUR_API_KEY"  # ضع مفتاحك الحقيقي هنا

# -------------------------------
# 2. استخراج النصوص من PDF
# -------------------------------
pdf_path = "Biology.pdf"
doc = fitz.open(pdf_path)

texts = []
for page in doc:
    texts.append(page.get_text())

full_text = "\n".join(texts)
paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

# -------------------------------
# 3. إنشاء قاعدة بيانات SQLite
# -------------------------------
conn = sqlite3.connect("biology_embeddings.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS biology_texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paragraph TEXT,
    embedding TEXT
)
''')
conn.commit()

# -------------------------------
# 4. دالة توليد Embedding
# -------------------------------
def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response['data'][0]['embedding']

# -------------------------------
# 5. تخزين أول 10 فقرات مع Embeddings
# -------------------------------
print("جاري توليد وتخزين embeddings لأول 10 فقرات ...")
for para in paragraphs[:10]:
    emb = get_embedding(para)
    c.execute(
        "INSERT INTO biology_texts (paragraph, embedding) VALUES (?, ?)",
        (para, json.dumps(emb))
    )
conn.commit()
print("تم التخزين بنجاح!")

# -------------------------------
# 6. دالة التشابه باستخدام Cosine Similarity
# -------------------------------
def cosine_similarity(vec1, vec2):
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

# -------------------------------
# 7. البحث عن نص مشابه
# -------------------------------
def search_similar_text(query, top_k=1):
    query_emb = get_embedding(query)
    c.execute("SELECT paragraph, embedding FROM biology_texts")
    rows = c.fetchall()

    similarities = []
    for paragraph, emb_json in rows:
        emb = np.array(json.loads(emb_json))
        score = cosine_similarity(query_emb, emb)
        similarities.append((score, paragraph))

    similarities.sort(reverse=True, key=lambda x: x[0])
    return similarities[:top_k]

# -------------------------------
# 8. تجربة البحث
# -------------------------------
query_text = "ما هي وظائف الخلية النباتية؟"
results = search_similar_text(query_text, top_k=3)

print("\nأقرب الفقرات للنص المطلوب:")
for score, para in results:
    print(f"\nالتشابه: {score:.4f}\n{para}\n")

# -------------------------------
# 9. إغلاق قاعدة البيانات
# -------------------------------
conn.close()