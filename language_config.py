import asyncio


async def configure_language(client, bot_username):
    """
    Programmatically configure the bot language by clicking
    inline keyboard buttons via Telethon's msg.click().

    Flow:
      1. Send the language menu command to the bot
      2. Wait for the bot's reply with inline keyboard buttons
      3. Display available language options to the user
      4. Click the selected button programmatically
    """
    print(f"\nConfiguring Language for {bot_username}...")

    # Step 1: Send the language menu command
    await client.send_message(bot_username, "\U0001F310 Language")
    await asyncio.sleep(2)  # Give the bot time to respond

    # Step 2: Fetch the bot's latest message (should contain inline buttons)
    history = await client.get_messages(bot_username, limit=1)
    if not history:
        print("No response from bot.")
        return

    bot_msg = history[0]

    # Step 3: Extract available buttons from the inline keyboard
    buttons = []
    if bot_msg.reply_markup:
        for row in bot_msg.reply_markup.rows:
            for button in row.buttons:
                buttons.append(button.text)

    if not buttons:
        # Fallback: show whatever text the bot sent
        if bot_msg.text:
            print(f"\n[Bot Response]:\n{bot_msg.text}")
        print("No inline buttons found in bot response.")
        return

    # Display available options
    print("\nAvailable Languages:")
    print("-" * 30)
    for i, btn_text in enumerate(buttons, 1):
        print(f"  {i}. {btn_text}")
    print("-" * 30)

    # Step 4: Get user selection
    selection = input(
        "\nEnter the number of the language to select (or press Enter to skip): "
    ).strip()

    if not selection:
        print("Language configuration skipped.")
        return

    try:
        idx = int(selection) - 1
        if idx < 0 or idx >= len(buttons):
            print("Invalid selection number.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    selected_lang = buttons[idx]
    print(f"Selecting: {selected_lang}...")

    # Step 5: Click the button programmatically
    try:
        await bot_msg.click(text=selected_lang)
        await asyncio.sleep(1)

        # Check for confirmation from bot
        confirmation = await client.get_messages(bot_username, limit=1)
        if confirmation and confirmation[0].id != bot_msg.id and confirmation[0].text:
            print(f"\n[Bot]: {confirmation[0].text}")
        else:
            print(f"Language set to: {selected_lang}")
    except Exception as e:
        print(f"Error clicking button: {e}")

# configure voice model
async def configure_voice_model(client, BOT_USERNAME):
    """Sends the command to configure the voice model."""
    print(f"Configuring Voice Model for {BOT_USERNAME}...")
    await client.send_message(BOT_USERNAME, "🗣️ Voice Model")
    await asyncio.sleep(1)
    
    # Wait for the bot's response with voice model options
    history = await client.get_messages(BOT_USERNAME, limit=1)
    if history and history[0].text:
        print("\n[Bot Voice Model Options]:")
        print(history[0].text)
        
    model_choice = input("\nEnter the exact text of the voice model button you want to select (or press Enter to skip): ").strip()
    if model_choice:
        await client.send_message(BOT_USERNAME, model_choice)
        await asyncio.sleep(1)
        print("Voice model selection sent.")
