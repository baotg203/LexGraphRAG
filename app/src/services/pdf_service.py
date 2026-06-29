from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract


class PdfService:

    def extract_text(self, path):
        reader = PdfReader(path)

        texts = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                texts.append(text)

        merged = "\n".join(texts)

        if len(merged) > 500:
            return merged

        return self.extract_ocr(path)

    def extract_ocr(self, path):
        pages = convert_from_path(path)

        texts = []

        for page in pages:
            texts.append(
                pytesseract.image_to_string(
                    page,
                    lang="vie"
                )
            )

        return "\n".join(texts)