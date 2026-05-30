import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribe_audio(file_path: str) -> dict:
    filename = os.path.basename(file_path)
    print(f"[whisper] Транскрибирую: {filename}")

    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            file=(filename, f),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            language="ru",
            timestamp_granularities=["segment"],
        )

    segments = []
    if hasattr(response, "segments") and response.segments:
        for seg in response.segments:
            if isinstance(seg, dict):
                segments.append({
                    "start": float(seg.get("start", 0)),
                    "end":   float(seg.get("end", 0)),
                    "text":  str(seg.get("text", "")).strip(),
                })
            else:
                segments.append({
                    "start": float(seg.start),
                    "end":   float(seg.end),
                    "text":  seg.text.strip(),
                })

    print(f"[whisper] Готово.")
    return {"text": response.text, "segments": segments}
