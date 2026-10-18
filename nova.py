import sounddevice as sd
import numpy as np
import requests
import mpd
import queue
import threading
import time
import re
import io
import wave

SERVER_URL = "http://192.168.0.228:5000/transcribe"  # поменяй на IP сервера.
SAMPLE_RATE = 16000
BLOCK_SIZE = int(SAMPLE_RATE * 0.5)
BUFFER_DURATION = 4.0
MPD_HOST = "localhost"
MPD_PORT = 6600


audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}")
    audio_queue.put(indata.copy())

def send_to_server(audio_data):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())
    buffer.seek(0)

    try:
        response = requests.post(
            SERVER_URL,
            files={"audio": ("audio.wav", buffer, "audio/wav")},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print(f"Fuck my ass: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return ""

def handle_command(text):
    trigger_words = ["вруби", "включи", "поставь", "играй"]
    if not any(word in text for word in trigger_words):
        return

    track_name = text
    for word in trigger_words:
        track_name = track_name.replace(word, "").strip()

    if not track_name:
        return

    print(f"Search: '{track_name}'")

    try:
        client = mpd.MPDClient()
        client.connect(MPD_HOST, MPD_PORT)
        client.timeout = 10

        client.clear()
        client.searchadd("any", track_name)

        playlist = client.playlistinfo()
        if playlist:
            client.play()
            print(f"Play: {playlist[0].get('file', 'not found in Music pull')}")
        else:
            print(f"Track '{track_name}' not found in Music pull")

        client.close()
        client.disconnect()
    except Exception as e:
        print(f"eRror MPD: {e}")

def process_audio():
    buffer = np.array([], dtype=np.float32)

    while True:
        try:
            chunk = audio_queue.get(timeout=1.0)
            buffer = np.concatenate([buffer, chunk.flatten()])
        except queue.Empty:
            continue

        if len(buffer) >= SAMPLE_RATE * BUFFER_DURATION:
            audio_to_process = buffer[-int(SAMPLE_RATE * BUFFER_DURATION):]
            text = send_to_server(audio_to_process)

            if text:
                print(f"Recognized: '{text}'")
                handle_command(text)

            buffer = np.array([], dtype=np.float32)

if __name__ == "__main__":
    processing_thread = threading.Thread(target=process_audio, daemon=True)
    processing_thread.start()

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE,
                            channels=1,
                            callback=audio_callback,
                            blocksize=BLOCK_SIZE):
            print("Learning...")
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\eXiting...")
