from flask import Flask, request, jsonify
import whisper
import tempfile
import os

app = Flask(__name__)

MODEL_SIZE = "base"
print(f"Загрузка модели Whisper '{MODEL_SIZE}'...")
model = whisper.load_model(MODEL_SIZE)
print("Модель загружена. Сервер готов.")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "no audio file"}), 400

    audio_file = request.files["audio"]

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path, fp16=False, language="ru")
        text = result["text"].strip()
        return jsonify({"text": text})
    finally:
        os.unlink(tmp_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
