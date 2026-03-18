import asyncio
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile

def record_audio(filename="user_voice.wav", samplerate=16000):
    print("\n[Press Enter to start recording]")
    input()
    print("🔴 Recording... [Press Enter to stop]")
    
    recording = []
    
    def callback(indata, frames, time, status):
        recording.append(indata.copy())
        
    stream = sd.InputStream(samplerate=samplerate, channels=1, callback=callback)
    with stream:
        input()
        
    if not recording:
        print("No audio recorded.")
        return None
        
    audio_data = np.concatenate(recording, axis=0)
    wavfile.write(filename, samplerate, audio_data)
    print(f"✅ Recording saved to '{filename}'")
    return filename

async def activate_stt_mode(client, bot_username):
    """Sends the command to the bot to activate Voice to Text mode."""
    print("Activating Voice to Text mode...")
    # Send the mode selection text
    await client.send_message(bot_username, "🎤 Voice to Text")
    await asyncio.sleep(1) # Give it a moment to process

async def stt_operation(client, bot_username):
    # Ensure the bot is in the correct mode
    await activate_stt_mode(client, bot_username)

    filename = record_audio()
    if not filename:
        return
        
    print(f"Sending voice note to {bot_username}...")
    
    history = await client.get_messages(bot_username, limit=1)
    last_id = history[0].id if history else 0
    
    await client.send_file(bot_username, filename, voice_note=True)
    print("Waiting for transcription from bot... (timeout in 60s)")
    
    response_msg = None
    # Status indicators the bot sends before the actual transcription
    status_indicators = ["⏳", "Transcribing", "Processing", "⌛"]
    
    for _ in range(60):
        await asyncio.sleep(1)
        history = await client.get_messages(bot_username, limit=1)
        if history and history[0].id > last_id:
            msg = history[0]
            if msg.text:
                # Check if this is an intermediate status message
                is_status = any(ind in msg.text for ind in status_indicators)
                
                if is_status:
                    # Print status but keep waiting for actual transcription
                    print(f"\n[Bot Status]: {msg.text}")
                    last_id = msg.id
                else:
                    # This is the actual transcription result
                    print(f"\n[Bot Transcription]:\n{msg.text}\n")
                    last_id = msg.id
                    response_msg = msg
                    break

    if not response_msg:
        print("❌ Timeout waiting for bot response.")
