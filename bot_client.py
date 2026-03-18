import os
import asyncio

from telethon import TelegramClient

from text_to_voice_bot import tts_operation
from voice_to_text_bot import stt_operation
from language_config import configure_language
from language_config import configure_voice_model

# --- Configuration ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_USERNAME = os.environ.get("BOT_USERNAME")


async def async_main():
    global API_ID, API_HASH, BOT_USERNAME
    
    print("=== Telegram Bot Client Setup ===")
    if not API_ID or not API_HASH:
        from dotenv import load_dotenv
        load_dotenv()
        API_ID = os.environ.get("API_ID")
        API_HASH = os.environ.get("API_HASH")
        BOT_USERNAME = os.environ.get("BOT_USERNAME")   

    if not API_ID or not API_HASH:
        print("Missing API credentials.")
        print("You can get these from https://my.telegram.org (API development tools)")
        try:
            API_ID = input("Enter your API ID: ").strip()
            API_HASH = input("Enter your API HASH: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            return

    if not API_ID or not API_HASH:
        print("API ID and API HASH are required to continue.")
        return

    try:
        api_id_int = int(API_ID)
    except ValueError:
        print("Error: API ID must be a number.")
        return

    client = TelegramClient('voicebot_session', api_id_int, API_HASH)
    
    print("\nConnecting to Telegram...")
    await client.start()
    print("✅ Logged in successfully!\n")
    
    while True:
        try:
            print("\n" + "="*40)
            print("   @ArdiopiaTTSBot Interaction Menu")
            print("="*40)
            print("1. Text to voice")
            print("2. Voice to text")
            print("3. Configure Language")
            print("4. Configure Voice Model")
            print("5. Exit")
            choice = input("Select an option (1/2/3/4/5): ").strip()
            
            if choice == '1':
                await tts_operation(client, BOT_USERNAME)
            elif choice == '2':
                await stt_operation(client, BOT_USERNAME)
            elif choice == '3':
                await configure_language(client, BOT_USERNAME)
            elif choice == '4':
                await configure_voice_model(client, BOT_USERNAME)
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid option. Please input 1, 2, 3, 4, or 5.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            
    await client.disconnect()

def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
