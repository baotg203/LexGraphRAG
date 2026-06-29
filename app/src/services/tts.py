import io
from gtts import gTTS


class TTSService:
    def generate(self, text: str):
        tts = gTTS(text, lang="vi")

        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)

        return buf