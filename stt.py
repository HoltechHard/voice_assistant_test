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

MODEL_SIZE = "small"           # RAM: 1-2 GB | CPU load: moderate | accuracy: good 
SAMPLE_RATE = 16000            # number of numpy values samples per second
CHUNK_DURATION = 5             # seconds per transcription chunk
CONTEXT_DURATION = 2           # seconds of overlap
MAX_RECORD_SECONDS = 60        # maximum listening time
COMPUTE_TYPE = "int8"          # optimized for CPU

# ==============================
# |         LOAD MODEL         |
# ==============================

print("Loading Whisper model ...")
model = WhisperModel(MODEL_SIZE, 
                     compute_type=COMPUTE_TYPE,
                     cpu_threads=4)
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

def normalize_audio(audio):
    rms = np.sqrt(np.mean(audio**2))
    if rms > 0:
        audio = audio / rms
    return audio

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
                    
                    # overlap: keeps the last CONTEXT_DURATION seconds 
                    # as memory for the next chunk
                    accumulated_audio = accumulated_audio[
                        SAMPLE_RATE * (CHUNK_DURATION - CONTEXT_DURATION):
                    ]
                    
                    segments, _ = model.transcribe(
                        segment_audio,
                        beam_size=7,    # higher beam size = better accuracy but slower
                        vad_filter=False,
                        language="en",
                        condition_on_previous_text=True,  # use previous text as context
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
