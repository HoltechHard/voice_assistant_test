import asyncio
import os

# Add ffmpeg to PATH before importing pydub (installed via ffmpeg-downloader)
_ffmpeg_dir = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "ffmpegio", "ffmpeg-downloader", "ffmpeg", "bin"
)
if os.path.isdir(_ffmpeg_dir) and _ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

import pygame
from pydub import AudioSegment

# Make sure pygame is initialized
pygame.mixer.init()

def play_audio(filename):
    """Plays an audio file. Converts OGG Opus to WAV first since pygame
    only supports OGG Vorbis, not OGG Opus (Telegram's format)."""
    print(f"Playing audio: {filename}...")
    wav_path = None
    try:
        # Convert to WAV via pydub (handles OGG Opus via ffmpeg)
        base, _ = os.path.splitext(filename)
        wav_path = base + "_converted.wav"
        audio = AudioSegment.from_file(filename)
        audio.export(wav_path, format="wav")

        pygame.mixer.music.load(wav_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print("✅ Playback finished.")
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        # Clean up temporary WAV file
        if wav_path and os.path.exists(wav_path):
            pygame.mixer.music.unload()
            os.remove(wav_path)

async def activate_tts_mode(client, bot_username):
    """Sends the command to the bot to activate Text to Voice mode."""
    print("Activating Text to Voice mode...")
    # Send the mode selection text
    # When interacting with inline keyboards, often sending the exact text of the button works
    # Or sending /start first to get the menu
    await client.send_message(bot_username, "🔊 Text to Voice")
    await asyncio.sleep(1) # Give it a moment to process

async def tts_operation(client, bot_username):
    # Ensure the bot is in the correct mode
    await activate_tts_mode(client, bot_username)

    text = input("\nEnter the text you want to convert to voice: ").strip()
    if not text:
        print("Text cannot be empty.")
        return

    print(f"Sending text to {bot_username}...")
    
    # Get last message to track new ones
    history = await client.get_messages(bot_username, limit=1)
    last_id = history[0].id if history else 0
    
    await client.send_message(bot_username, text)
    print("Waiting for audio response from bot... (timeout in 60s)")
    
    response_msg = None
    for _ in range(60):
        await asyncio.sleep(1)
        history = await client.get_messages(bot_username, limit=1)
        if history and history[0].id > last_id:
            msg = history[0]
            # If the bot replies with an audio/voice note
            if msg.media:
                response_msg = msg
                break 
            elif msg.text:
                # Some bots send intermediate textual messages like 'Generating...'
                print(f"[Bot] {msg.text}")
                last_id = msg.id # Update last_id to listen for the next message

    if response_msg and response_msg.media:
        print("⬇️ Audio received! Downloading...")
        # Save as .ogg because telegram voice notes are usually OGG Opus
        path = await client.download_media(response_msg.media, file="bot_voice_response.ogg")
        print(f"✅ Downloaded to '{path}'")
        play_audio(path)
    elif response_msg is None:
        print("❌ Timeout waiting for bot response.")
