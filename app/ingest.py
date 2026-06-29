from collections import defaultdict
from pathlib import Path

from config import PDF_FOLDER, PDF_TEST
from app.core.db import get_connection
from app.core.graph import neo4j_driver
from app.src.container import IngestionContainer


def init_pdf_ingestion(data_path):
    """
    Group các file PDF theo document_code.
    """

    groups = defaultdict(list)

    for pdf_file in Path(data_path).glob("*.pdf"):

        pdf_name = pdf_file.stem

        if pdf_name not in PDF_TEST:
            print(
                f"⚠️ Skipping {pdf_name}: "
                f"not in predefined metadata."
            )
            continue

        metadata = PDF_TEST[pdf_name]

        groups[
            metadata["document_code"]
        ].append({
            "path": str(pdf_file),
            "meta": metadata
        })

    return groups


def ingest_documents():

    groups = init_pdf_ingestion(
        PDF_FOLDER
    )

    if not groups:
        print("No PDF found.")
        return

    conn = get_connection()
    cur = conn.cursor()

    container = IngestionContainer(
        cur=cur,
        neo4j_driver=neo4j_driver
    )

    try:
        for document_code, files in groups.items():

            metadata = files[0]["meta"]

            print(
                f"\n🚀 Processing "
                f"{metadata['title']}"
            )

            container.ingestion_service.ingest(
                conn=conn,
                metadata=metadata,
                files=files
            )

            conn.commit()

        print("\n✅ INGEST COMPLETED")

    except Exception as e:

        conn.rollback()

        print(
            f"\n❌ INGEST FAILED: {e}"
        )
        raise

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    ingest_documents()