# Real time Speech-to-Text using Faster Whisper
# Real time microphone streaming

import sounddevice as sd
import numpy as np
import queue
import sys
import time
from faster_whisper import WhisperModel

# ============================
# |     CONFIGURATION        |
# ============================

MODEL_SIZE = "small"            # or "small"
SAMPLE_RATE = 16000
CHUNK_DURATION = 3             # seconds per transcription chunk
MAX_RECORD_SECONDS = 60         # maximum listening time
COMPUTE_TYPE = "int8"           # optimized for CPU

# ==============================
# |         LOAD MODEL         |
# ==============================

print("Loading Whisper model ...")
model = WhisperModel(MODEL_SIZE, compute_type=COMPUTE_TYPE)
print("Model loaded...\n")

# ==============================
# |     AUDIO STREAM SETUP     |
# ==============================

audio_queue = queue.Queue()

def audio_callback(in_data, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(in_data.copy())

# ===============================
# |   STREAMING TRANSCRIPTION   |
# ===============================

def stream_transcription():
    print("?? Start speaking (max 60 seconds)...\n")

    start_time = time.time()
    accumulated_audio = np.empty((0,), dtype=np.float32)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback,
    ):
        while True:

            # Stop after 90 seconds
            if time.time() - start_time > MAX_RECORD_SECONDS:
                print("\n? Max recording time reached.")
                break

            try:
                audio_chunk = audio_queue.get(timeout=1)
                accumulated_audio = np.append(accumulated_audio, audio_chunk.flatten())

                # If we have enough audio for one chunk
                if len(accumulated_audio) >= SAMPLE_RATE * CHUNK_DURATION:

                    segment_audio = accumulated_audio[:SAMPLE_RATE * CHUNK_DURATION]
                    accumulated_audio = accumulated_audio[SAMPLE_RATE * CHUNK_DURATION:]

                    segments, _ = model.transcribe(
                        segment_audio,
                        beam_size=5,
                        vad_filter=True
                    )

                    for segment in segments:
                        print(segment.text, end=" ", flush=True)

            except queue.Empty:
                continue

# ===================
# |     MAIN        |
# ===================

if __name__ == "__main__":
    try:
        stream_transcription()
    except KeyboardInterrupt:
        print("\n? Recording stopped manually.")
