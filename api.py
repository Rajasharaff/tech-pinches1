import asyncio
import threading
import tkinter as tk
from telethon import TelegramClient, events
from datetime import datetime
import os

# Replace these with your own values
api_id = 21484435
api_hash = '8071a988bf3e8eb900c94eaa5beafd86'
phone_number = '7708943187'  # Replace with your actual phone number

# Create the client with a session file
client = TelegramClient('nisha_session', api_id, api_hash)

# Set of users that have already been replied to
replied_users = set()
# Dictionary to track if a user has received a photo
user_photo_status = {}

# Define the responses for specific questions and statements
response_map = {
    # Existing responses...
    "name": "Nisha",
    "from": "naa erode pa, neenga",
    "place": "naa erode pa, neenga",
    "location": "naa erode pa, neenga",
    "b or f": "I'm female",
    "m or f": "I'm female",
    "ponna": "I'm female",
    "girla": "I'm female",
    "trans": "I'm female",
    "boy illa girl": "I'm female",
    "boy": "I'm female",
    "bro": "I'm female",
    "girl": "I'm female",
    "hi": "I'm a paid girl from Erode. Do you want VC service?",
    "how much": "This is my rate: 5 min - 100, 10 min - 200, 20 min - 250, 30 min - 300",
    "vc": "This is my rate: 5 min - 100, 10 min - 200, 20 min - 250, 30 min - 300",
    "price": "This is my rate: 5 min - 100, 10 min - 200, 20 min - 250, 30 min - 300",
    "want vc": "If you want a demo, wait. I will do it.",
    "demo": "If you want a demo, wait. I will do it.",
    "proof": "If you want a demo, wait. I will do it.",
    "pic": "Wait, anuparan",
    "pics": "Wait, anuparan",
    "photo": "Wait, anuparan",
    "age": "20",
    "vauasu": "20",
    "Looking for": "I'm a paid girl",
    "top": "I'm a paid girl",
    "btm": "I'm a paid girl",
    "bottom": "I'm a paid girl",
    "top or bottom": "I'm a paid girl",
    "t or b": "I'm a paid girl",
    "But work la iruken": "Carry on",
    "office la iruken": "Carry on",
    "home la iruken": "Carry on",
    "veetls la iruken": "Carry on",
    "no": "Ok",
    "bye": "bye",
    "state": "Tamil Nadu",
    "tamil": "Ama",
    "tamil ponna": "ama",
    "meet": "Only VC",
    "who are you": "I am a paid girl from Tamil Nadu, Erode",
    "rate": "This is my rate: 5 min - 100, 10 min - 200, 20 min - 250, 30 min - 300",
    "send": "Ok",
    "Don't call": "Ok",
    "Only live meet": "Sorry, first do VC service. If we have a good mutual understanding, then we can discuss further.",
    "real": "Sorry, first do VC service. If we have a good mutual understanding, then we can discuss further.",
    "area": "Komorapalayam",
    "Enga iruka": "I am a paid girl from Tamil Nadu, Erode",
    "Virgin ah": "ama",
    "Boy or girl": "I'm a paid girl",
    "gpay": "tho anuparan",
    "qr": "tho anuparan",
    "qrcode": "tho anuparan",
    "marriage": "time pass pannatheenga plz",
    "friends": "time pass pannatheenga plz, naa paid girl",
    # New responses
    "beautiful": "Thank you! 😊 You're very kind!",
    "beauty": "Thank you! 😊 You're very kind!",
    "looks good": "Thank you! 😊 You're very kind!",
    "நீங்கள் அழகாக இருக்கிறீர்கள்": "நன்றி! 😊 நீங்கள் மிகவும் நல்லவர்!",
    "அழகு": "நன்றி! 😊 !",
}


# Paths to the images (can be updated using environment variables)
image_paths = {
    "photo1": os.getenv('PHOTO1_PATH', r'C:\Users\raja\Downloads\photo_2024-08-14_06-13-17.jpg'),
    "photo2": os.getenv('PHOTO2_PATH', r'C:\Users\raja\Downloads\photo_2024-08-14_06-13-21.jpg'),
    "payment": os.getenv('PAYMENT_PATH', r'C:\Users\raja\Downloads\photo_2024-08-14_02-38-35.jpg'),
    "qr": os.getenv('QR_PATH', r'C:\Users\raja\Downloads\photo_2024-08-14_02-38-35.jpg')
}

class TelegramBotUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Telegram Auto-Chat Bot")

        # Start/Stop buttons
        self.start_button = tk.Button(master, text="Start Auto-Chat", command=self.start_chat)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Auto-Chat", command=self.stop_chat, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Group intro message toggle button
        self.group_intro_var = tk.BooleanVar(value=True)
        self.group_intro_button = tk.Checkbutton(master, text="Group Intro On/Off", variable=self.group_intro_var)
        self.group_intro_button.pack(pady=10)

        # Personal chat intro message toggle button
        self.chat_intro_var = tk.BooleanVar(value=True)
        self.chat_intro_button = tk.Checkbutton(master, text="Personal Chat Intro On/Off", variable=self.chat_intro_var)
        self.chat_intro_button.pack(pady=10)

        # Message interval setting
        self.message_interval = tk.IntVar(value=30)  # Default interval is 30 seconds
        self.interval_entry = tk.Entry(master, textvariable=self.message_interval)
        self.interval_entry.pack(pady=10)
        self.interval_button = tk.Button(master, text="Set Interval", command=self.set_message_interval)
        self.interval_button.pack(pady=10)

        # Message log
        self.log = tk.Text(master, height=15, width=50)
        self.log.pack(pady=10)

        # Thread control
        self.running = False
        self.chat_thread = None

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.insert(tk.END, f"{timestamp} - {message}\n")
        self.log.see(tk.END)

    def start_chat(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.chat_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.chat_thread.start()

    def stop_chat(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.chat_thread:
            self.chat_thread.join()

    def set_message_interval(self):
        try:
            interval = int(self.message_interval.get())
            if interval > 0:
                self.message_interval = interval
                self.log_message(f"Message interval set to {interval} seconds.")
            else:
                self.log_message("Invalid interval. Must be a positive number.")
        except ValueError:
            self.log_message("Invalid interval. Must be a number.")

    def run_bot(self):
        asyncio.run(self.main())

    async def main(self):
        await client.start(phone_number)
        print("Client is connected.")

        # Start periodic message task
        asyncio.create_task(self.send_periodic_messages())

        # Register event handler for new messages
        client.add_event_handler(self.handle_new_message, events.NewMessage)

        # Keeps the client running
        await client.run_until_disconnected()

    async def send_periodic_messages(self):
        await client.start(phone_number)  # Ensure the client is started

        # Fetch all dialogs (including groups, channels, and private chats)
        dialogs = await client.get_dialogs()

        # Filter only groups (including channels and supergroups)
        groups = [d for d in dialogs if d.is_group]

        self.log_message(f"Total groups joined: {len(groups)}")

        while self.running:
            for group in groups:
                try:
                    if self.group_intro_var.get():
                        await client.send_message(group.id, "DM me")
                        self.log_message(f"Message sent to {group.name}")
                except Exception as e:
                    self.log_message(f"Failed to send message to {group.name}: {e}")

            # Wait for the configured interval before sending the next batch of messages
            await asyncio.sleep(self.message_interval)

        self.log_message("Stopped messaging.")

    async def handle_new_message(self, event):
        sender = await event.get_sender()

        # Check if the message is from a personal chat (not a group or channel)
        if event.is_private:
            if self.chat_intro_var.get() and sender.id not in replied_users:
                # Send an intro message for personal chats
                await event.reply("Hi, I'm Nisha")
                replied_users.add(sender.id)
                self.log_message(f"Intro message sent to {sender.id}")

            # Process user queries
            message_text = event.message.text.lower()
            response_found = False
            for keyword, response in response_map.items():
                if keyword in message_text:
                    await event.reply(response)
                    self.log_message(f"Reply sent to {sender.id}: {response}")
                    response_found = True
                    break

            # Handle photo requests
            if "pic" in message_text or "photos" in message_text:
                if sender.id not in user_photo_status:
                    user_photo_status[sender.id] = 1
                    await self.send_photo(event.chat_id, "photo1")
                elif user_photo_status[sender.id] == 1:
                    user_photo_status[sender.id] = 2
                    await self.send_photo(event.chat_id, "photo2")
                else:
                    self.log_message(f"User {sender.id} has already received all photos.")
            
            elif any(keyword in message_text for keyword in ["gpay", "qr", "qrcode"]):
                if "qr" in message_text:
                    await self.send_photo(event.chat_id, "qr")
                else:
                    await self.send_photo(event.chat_id, "payment")

        elif event.is_group and self.group_intro_var.get():
            # Send a "DM me" message for group chats if enabled
            await event.reply("DM me")
            self.log_message(f"Group intro message sent to {sender.id}")

    async def send_photo(self, chat_id, photo_type):
        # Get the correct path for the photo type
        image_path = image_paths.get(photo_type, None)

        if image_path and os.path.isfile(image_path):
            # Determine TTL based on photo type
            ttl = 1 if photo_type != "qr" else None
            
            # Send a photo with or without TTL based on the type
            try:
                await client.send_file(
                    chat_id,
                    image_path,
                    caption="Pay pannunga plz",
                    ttl=ttl  # Time-to-live in seconds for self-destructing photos
                )
                self.log_message(f"Photo sent to chat {chat_id} ({photo_type})")
            except Exception as e:
                self.log_message(f"Failed to send photo: {e}")
        else:
            self.log_message(f"File not found or invalid path for {photo_type}: {image_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramBotUI(root)

    # Run the bot asynchronously in the background
    threading.Thread(target=lambda: asyncio.run(app.run_bot()), daemon=True).start()

    root.mainloop()
