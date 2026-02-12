import subprocess
import os

MODEL_PATH = "voice_models/en_US-lessac-medium.onnx"

def speak(text):
    command = [
        "piper",
        "--model", MODEL_PATH,
        "--output_file", "output.wav"
    ]

    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    process.communicate(input=text.encode())

    os.system("start output.wav")

if __name__ == "__main__":
    user_text = input("Enter text to speak: ")
    speak(user_text)
