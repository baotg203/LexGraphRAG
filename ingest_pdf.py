import json
import re
from collections import defaultdict
from pathlib import Path

import psycopg2
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from app.llm import local_llm
from pdf2image import convert_from_path
import pytesseract
from neo4j import GraphDatabase
from config import DB_CONFIG, NEO4J_CONFIG, PDF_FOLDER



# =====================================================

# EMBEDDING MODEL

# =====================================================

model = SentenceTransformer(
"intfloat/multilingual-e5-base",
device="cpu"
)

# =====================================================

# NEO4J DRIVER

# =====================================================

neo4j_driver = GraphDatabase.driver(
    NEO4J_CONFIG["uri"],
    auth=(
        NEO4J_CONFIG["user"],
        NEO4J_CONFIG["password"]
    )
)

# =====================================================

# DB INIT

# =====================================================

def init_db(cur):

 
    cur.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,

        document_code TEXT,
        title TEXT,
        version_name TEXT,

        effective_from DATE,
        effective_to DATE,

        source TEXT,

        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS document_chunks (
        id SERIAL PRIMARY KEY,

        document_id INTEGER
            REFERENCES documents(id)
            ON DELETE CASCADE,

        article_number TEXT,

        content TEXT NOT NULL,

        embedding VECTOR(768)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS legal_triples (
        id SERIAL PRIMARY KEY,

        chunk_id INTEGER
            REFERENCES document_chunks(id)
            ON DELETE CASCADE,

        subject TEXT NOT NULL,
        predicate TEXT NOT NULL,
        object TEXT NOT NULL
    );
    """)
    

# =====================================================

# PDF

# =====================================================

def extract_text_from_OCR(path, max_pages=2):
    print(f"[OCR] Detected scanned PDF: {path}")

    # ===== OCR fallback =====
    pages = convert_from_path(
        path,
        dpi=300,
        first_page=1,
        last_page=max_pages
    )

    ocr_texts = []

    for page in pages:
        page_text = pytesseract.image_to_string(
            page,
            lang="vie"
        )

        if page_text.strip():
            ocr_texts.append(page_text)

    return "\n".join(ocr_texts)

def extract_text_from_pdf(path, min_text_length=500):

    # ===== Try normal PDF extraction =====
    reader = PdfReader(path)

    texts = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text and page_text.strip():
            texts.append(page_text)

    extracted_text = "\n".join(texts)

    # ===== If enough text -> use it =====
    if len(extracted_text.strip()) >= min_text_length:
        return extracted_text
    
    return extract_text_from_OCR(path)


def extract_preview_text(path, max_pages=2, min_text_length=500):

    
    reader = PdfReader(path)

    texts = []

    for page in reader.pages[:max_pages]:

        text = page.extract_text()

        if text:
            texts.append(text)
    
    extracted_text = "\n".join(texts)

    # ===== If enough text -> use it =====
    if len(extracted_text.strip()) >= min_text_length:
        return extracted_text
    
    return extract_text_from_OCR(path, max_pages=max_pages)
 
# =====================================================

# EXTRACT JSON

# =====================================================

def extract_json(text: str):

    # bỏ markdown fence
    text = text.replace("```json", "")
    text = text.replace("```", "")

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.S
    )

    if not match:
        raise ValueError("No JSON found")

    return json.loads(
        match.group(0)
    )

# =====================================================

# QWEN METADATA

# =====================================================

def analyze_document_with_qwen(preview_text):

    prompt = f"""
Bạn là chuyên gia phân tích văn bản pháp luật Việt Nam.

Nhiệm vụ:
Đọc đoạn văn bản dưới đây (là phần preview của một văn bản pháp luật).

Chỉ trả về JSON hợp lệ.
Tổng hợp và trả lời ngắn gọn xúc tích nhất các thông tin sau:

Schema:

{{
  "document_code": "Là mã số của bộ luật, nghị định, thông tư,...(có thể trùng với có sẵn trong hệ thống, nếu không tìm thấy thì để trống)",
  "title": "Tên bộ luật, nghị định, thông tư,...(có thể trùng với có sẵn trong hệ thống, nếu không tìm thấy thì để trống)",
  "version_name": "Thời gian ban hành văn bản (nếu có thể xác định được, nếu không thì để trống) (format: YYYY-MM-DD)",
  "effective_from": Thời gian có hiệu lực của văn bản (nếu có thể xác định được, nếu không thì để giống version_name hoặc để trống) (format: YYYY-MM-DD),
  "effective_to": Thời gian hết hiệu lực của văn bản (nếu có thể xác định được, nếu không thì để trống) (format: YYYY-MM-DD)
}}

Văn bản:

{preview_text[:500]}
"""

    content = local_llm(prompt)
    print(content)

    try:
        return extract_json(content)

    except Exception:

        print("Cannot parse JSON")

        return {
            "document_code": "UNKNOWN",
            "title": "UNKNOWN",
            "version_name": "UNKNOWN",
            "effective_from": None,
            "effective_to": None
        }
 

# =====================================================

# ARTICLE SPLIT

# =====================================================

def split_by_article(text):

 
    pattern = r"(Điều\s+\d+.*?)(?=Điều\s+\d+|$)"

    return re.findall(
        pattern,
        text,
        flags=re.S
    )
 

def extract_article_number(article):

 
    m = re.search(
        r"Điều\s+(\d+)",
        article
    )

    return m.group(1) if m else None

def extract_triples(article):

    prompt = f"""
Bạn là chuyên gia luật.

Trích xuất các quan hệ pháp lý
dưới dạng JSON.

Schema:

[
  {{
    "subject":"",
    "predicate":"",
    "object":""
  }}
]

Chỉ trả JSON.

TEXT:

{article[:2000]}
"""

    try:

        result = local_llm(prompt)

        result = (
            result
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        triples = json.loads(result)

        if isinstance(triples, list):
            return triples

    except Exception as e:

        print("Triple extraction error:", e)

    return []

# =====================================================

# SAVE TRIPLES TO POSTGRESQL

# =====================================================


def save_triples(cur, chunk_id, triples):

    for t in triples:

        subject = t.get("subject")
        predicate = t.get("predicate")
        obj = t.get("object")

        if not subject or not predicate or not obj:
            continue

        cur.execute(
            """
            INSERT INTO legal_triples(
                chunk_id,
                subject,
                predicate,
                object
            )
            VALUES (%s,%s,%s,%s)
            """,
            (
                chunk_id,
                subject,
                predicate,
                obj
            )
        )

# =====================================================

# SAVE TRIPLES TO NEO4J

# =====================================================


def save_triples_to_neo4j(
    chunk_id,
    article_no,
    document_title,
    triples
):

    with neo4j_driver.session() as session:

        for t in triples:

            subject = t.get("subject")
            predicate = t.get("predicate")
            obj = t.get("object")

            if not subject or not predicate or not obj:
                continue

            session.run(
                """
                MERGE (s:Entity {
                    name:$subject
                })

                MERGE (o:Entity {
                    name:$object
                })

                MERGE (c:Chunk {
                    chunk_id:$chunk_id
                })

                SET c.article_number = $article_no
                SET c.document_title = $document_title

                MERGE (f:LegalFact {
                    subject:$subject,
                    predicate:$predicate,
                    object:$object
                })

                MERGE (s)-[:SUBJECT_OF]->(f)

                MERGE (f)-[:OBJECT_OF]->(o)

                MERGE (f)-[:SUPPORTED_BY]->(c)
                """,
                subject=subject,
                predicate=predicate,
                object=obj,
                chunk_id=chunk_id,
                article_no=article_no,
                document_title=document_title
            )
 

# =====================================================

# EMBEDDING

# =====================================================

def embed_passage(text):

 
    return model.encode(
        f"passage: {text}",
        normalize_embeddings=True
    ).tolist()
 

# =====================================================

# GROUP PDF

# =====================================================

def discover_law_groups():

 
    pdf_files = list(
        Path(PDF_FOLDER).glob("*.pdf")
    )

    groups = defaultdict(list)

    for pdf in pdf_files:

        print(f"Processing {pdf}...")
        preview = extract_preview_text(pdf)

        meta = analyze_document_with_qwen(
            preview
        )

        groups[
            meta["document_code"]
        ].append(
            {
                "path": pdf,
                "meta": meta
            }
        )

    return groups
 

# =====================================================

# INSERT DOCUMENT

# =====================================================

def insert_document(cur, metadata, merged_source):

 
    required_fields = [
    "document_code",
    "title",
    "version_name",
    "effective_from",
    "effective_to"
    ]

    for field in required_fields:

        if field not in metadata:
            metadata[field] = None

        if metadata[field] == "":
            metadata[field] = None

        
    cur.execute(
        """
        INSERT INTO documents (
            document_code,
            title,
            version_name,
            effective_from,
            effective_to,
            source
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (
            metadata.get("document_code"),
            metadata.get("title"),
            metadata.get("version_name"),
            metadata.get("effective_from"),
            metadata.get("effective_to"),
            merged_source
        )
    )

    return cur.fetchone()[0]
    

# =====================================================

# INGEST GROUP

# =====================================================

def ingest_group(cur, metadata, files):

 
    print(
        f"Ingesting law: "
        f"{metadata['title']}"
    )

    merged_text = ""

    for item in files:

        merged_text += (
            extract_text_from_pdf(
                item["path"]
            )
            + "\n"
        )

    document_id = insert_document(
        cur,
        metadata,
        ";".join(
            str(f["path"])
            for f in files
        )
    )

    articles = split_by_article(
        merged_text
    )

    for article in articles:

        article_no = extract_article_number(
            article
        )

        emb = embed_passage(article)

        cur.execute(
            """
            INSERT INTO document_chunks(
                document_id,
                article_number,
                content,
                embedding
            )
            VALUES (%s,%s,%s,%s)
            RETURNING id
            """,
            (
                document_id,
                article_no,
                article,
                emb
            )
        )

        chunk_id = cur.fetchone()[0]
        triples = extract_triples(article)

        save_triples(
            cur,
            chunk_id,
            triples
        )

        save_triples_to_neo4j(
            chunk_id,
            article_no,
            metadata["title"],
            triples
        )

    print(
        f"Inserted {len(articles)} articles"
    )
 

# =====================================================

# MAIN

# =====================================================

def main():

 
    groups = discover_law_groups()

    conn = psycopg2.connect(
        **DB_CONFIG
    )

    cur = conn.cursor()

    init_db(cur)

    conn.commit()

    for law_code, files in groups.items():

        metadata = files[0]["meta"]

        ingest_group(
            cur,
            metadata,
            files
        )

    conn.commit()

    cur.close()
    conn.close()

    print("✅ INGEST COMPLETED")
    

if __name__ == "__main__":
    main()
