import requests
import tkinter as tk
import tkinter.ttk as ttk
import asyncio
import os
import threading
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from telethon import TelegramClient


from dotenv import load_dotenv

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


load_dotenv()

env_api_id = os.getenv("TELEGRAM_API_ID", "0")
env_api_hash = os.getenv("TELEGRAM_API_HASH", "")
env_phone_number = os.getenv("TELEGRAM_PHONE", "")

api_id = int(env_api_id) if env_api_id.isdigit() else 0
api_hash = env_api_hash
phone_number = env_phone_number

client = TelegramClient("anon_session", api_id, api_hash)

TELEGRAM_API_URL = "https://api.telegram.org/bot"

class TelegramGUI:
    def __init__(self, root):

        self.root = root
        self.root.title("Matkap by 0x6rss")
        self.root.geometry("850x600")
        self.root.resizable(True, True)


        self.themes = {
            "Light": {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "header_bg": "#AAAAAA",
                "main_bg": "#FFFFFF"
            },
            "Dark": {
                "bg": "#2E2E2E",
                "fg": "#FFFFFF",
                "header_bg": "#333333",
                "main_bg": "#2E2E2E"
            }
        }
        self.current_theme = "Light"  
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_theme(self.current_theme)

        self.style.configure("TLabel", background="#D9D9D9", foreground="black")
        self.style.configure("TButton", background="#E1E1E1", foreground="black")
        self.style.configure("TLabelframe", background="#C9C9C9", foreground="black")
        self.style.configure("TLabelframe.Label", font=("Arial", 11, "bold"))
        self.style.configure("TEntry", fieldbackground="#FFFFFF", foreground="black")

        self.header_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["header_bg"])
        self.header_frame.grid(row=0, column=0, columnspan=5, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.logo_image = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "logo.png")
        if os.path.isfile(logo_path):
            try:
                if PIL_AVAILABLE:
                    pil_img = Image.open(logo_path)
                    self.logo_image = ImageTk.PhotoImage(pil_img)
                else:
                    self.logo_image = tk.PhotoImage(file=logo_path)
            except Exception as e:
                print("Logo load error:", e)
                self.logo_image = None

        self.header_label = tk.Label(
            self.header_frame,
            text="Matkap - hunt down malicious telegram bots",
            font=("Arial", 16, "bold"),
            bg=self.themes[self.current_theme]["header_bg"],
            fg=self.themes[self.current_theme]["fg"],
            image=self.logo_image,
            compound="left",
            padx=10
        )
        self.header_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.main_frame = tk.Frame(self.root,
                                   bg=self.themes[self.current_theme]["main_bg"],
                                   highlightthickness=2, bd=0, relief="groove")
        self.main_frame.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        ttk.Label(self.main_frame, text="Color Theme:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.theme_combo = ttk.Combobox(self.main_frame, values=list(self.themes.keys()), state="readonly")
        self.theme_combo.current(0)  
        self.theme_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.theme_combo.bind("<<ComboboxSelected>>", self.switch_theme)

        self.token_label = ttk.Label(self.main_frame, text="Malicious Bot Token:")
        self.token_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.token_entry = ttk.Entry(self.main_frame, width=45)
        self.token_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.token_entry, "Example: bot12345678:AsHy7q9QB755Lx4owv76xjLqZwHDcFf7CSE")

        self.chat_label = ttk.Label(self.main_frame, text="Malicious Chat ID (Forward):")
        self.chat_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.chatid_entry = ttk.Entry(self.main_frame, width=45)
        self.chatid_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.chatid_entry, "Example: 123456789")

        self.infiltrate_button = ttk.Button(
            self.main_frame,
            text="1) Start Attack",
            command=self.start_infiltration
        )
        self.infiltrate_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.forward_button = ttk.Button(
            self.main_frame,
            text="2) Forward All Messages",
            command=self.forward_all_messages
        )
        self.forward_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.stop_button = ttk.Button(
            self.main_frame,
            text="Stop",
            command=self.stop_forwarding
        )
        self.stop_button.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        self.resume_button = ttk.Button(
            self.main_frame,
            text="Continue",
            command=self.resume_forward,
            state="disabled"
        )
        self.resume_button.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        self.log_frame = ttk.LabelFrame(self.main_frame, text="Process Log")
        self.log_frame.grid(row=4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.log_text = ScrolledText(self.log_frame, width=75, height=15, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)


        clear_logs_btn = ttk.Button(self.log_frame, text="Clear Logs", command=self.clear_logs)
        clear_logs_btn.pack(side="bottom", anchor="e", pady=5)

        self.bot_token = None
        self.bot_username = None
        self.my_chat_id = None
        self.last_message_id = None

        self.stop_flag = False
        self.stopped_id = 0
        self.current_msg_id = 0
        self.max_older_attempts = 200

    def configure_theme(self, theme_name):
        theme_info = self.themes[theme_name]
        bg = theme_info["bg"]
        fg = theme_info["fg"]
        self.style.configure(".", background=bg, foreground=fg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background=bg, foreground=fg)
        self.style.configure("TLabelframe", background=bg, foreground=fg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg)
        self.style.configure("TEntry", fieldbackground="#FFFFFF", foreground="#000000")

    def switch_theme(self, event):
        selected_theme = self.theme_combo.get()
        if selected_theme in self.themes:
            self.current_theme = selected_theme
            self.configure_theme(selected_theme)

            self.header_frame.config(bg=self.themes[self.current_theme]["header_bg"])
            self.header_label.config(bg=self.themes[self.current_theme]["header_bg"],
                                     fg=self.themes[self.current_theme]["fg"])

            self.main_frame.config(bg=self.themes[self.current_theme]["main_bg"])

            self.log(f"🌀 Switched theme to: {selected_theme}")

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def add_placeholder(self, entry_widget, placeholder_text):
        def on_focus_in(event):
            if entry_widget.get() == placeholder_text:
                entry_widget.delete(0, "end")
                entry_widget.configure(foreground="black")

        def on_focus_out(event):
            if entry_widget.get().strip() == "":
                entry_widget.insert(0, placeholder_text)
                entry_widget.configure(foreground="grey")

        entry_widget.insert(0, placeholder_text)
        entry_widget.configure(foreground="grey")
        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def stop_forwarding(self):
        self.stop_flag = True
        self.log("➡️ [Stop Button] Stop request sent.")
        self.resume_button.config(state="normal")

    def resume_forward(self):
        self.log(f"▶️ [Resume] Resuming from ID {self.stopped_id + 1}")
        self.stop_flag = False
        self.resume_button.config(state="disabled")

        from_chat_id = self.chatid_entry.get().strip()
        if not from_chat_id or "Example:" in from_chat_id:
            messagebox.showerror("Error", "Malicious Chat ID is empty!")
            return

        self.forward_continuation(from_chat_id, start_id=self.stopped_id + 1)

    def parse_bot_token(self, raw_token):
        raw_token = raw_token.strip()
        if raw_token.lower().startswith("bot"):
            raw_token = raw_token[3:]
        return raw_token

    def get_me(self, bot_token):
        url = f"{TELEGRAM_API_URL}{bot_token}/getMe"
        try:
            r = requests.get(url)
            data = r.json()
            if data.get("ok"):
                return data["result"]
            else:
                self.log(f"[getMe] Error: {data}")
                return None
        except Exception as e:
            self.log(f"[getMe] Req error: {e}")
            return None

    async def telethon_send_start(self, bot_username):
        await client.start(phone_number)
        self.log("✅ [Telethon] Logged in with your account.")
        try:
            if not bot_username.startswith("@"):
                bot_username = "@" + bot_username
            await client.send_message(bot_username, "/start")
            self.log(f"✅ [Telethon] '/start' sent to {bot_username}.")
        except Exception as e:
            self.log(f"❌ [Telethon] Send error: {e}")
        finally:
            await client.disconnect()

    def get_updates(self, bot_token):
        url = f"{TELEGRAM_API_URL}{bot_token}/getUpdates"
        try:
            r = requests.get(url)
            data = r.json()
            if data.get("ok") and data["result"]:
                last_update = data["result"][-1]
                msg = last_update["message"]
                my_chat_id = msg["chat"]["id"]
                last_message_id = msg["message_id"]
                self.log(f"[getUpdates] my_chat_id={my_chat_id}, last_msg_id={last_message_id}")
                return my_chat_id, last_message_id
            else:
                self.log(f"[getUpdates] no result: {data}")
                return None, None
        except Exception as e:
            self.log(f"[getUpdates] error: {e}")
            return None, None

    def forward_msg(self, bot_token, from_chat_id, to_chat_id, message_id):
        url = f"{TELEGRAM_API_URL}{bot_token}/forwardMessage"
        payload = {
            "from_chat_id": from_chat_id,
            "chat_id": to_chat_id,
            "message_id": message_id
        }
        try:
            r = requests.post(url, json=payload)
            data = r.json()
            if data.get("ok"):
                self.log(f"✅ Forwarded message ID {message_id}.")
                return True
            else:
                self.log(f"⚠️ Forward fail ID {message_id}, reason: {data}")
                return False
        except Exception as e:
            self.log(f"❌ Forward error ID {message_id}: {e}")
            return False

    def infiltration_process(self, attacker_id):
        found_any = False
        start_id = self.last_message_id
        stop_id = max(1, self.last_message_id - self.max_older_attempts)
        self.log(f"Trying older IDs from {start_id} down to {stop_id}")

        for test_id in range(start_id, stop_id - 1, -1):
            if self.stop_flag:
                self.log("⏹️ Infiltration older ID check stopped by user.")
                return
            success = self.forward_msg(self.bot_token, attacker_id, self.my_chat_id, test_id)
            if success:
                self.log(f"✅ First older message captured! ID={test_id}")
                found_any = True
                break
            else:
                self.log(f"Try next older ID {test_id-1}...")

        if found_any:
            self.log("Now you can forward all messages if needed.")
        else:
            self.log("No older ID worked within our limit. Possibly no older messages or limit insufficient.")

    def start_infiltration(self):
        raw_token = self.token_entry.get().strip()
        if not raw_token or "Example:" in raw_token:
            messagebox.showerror("Error", "Bot Token cannot be empty!")
            return

        parsed_token = self.parse_bot_token(raw_token)
        info = self.get_me(parsed_token)
        if not info:
            messagebox.showerror("Error", "getMe failed or not a valid bot token!")
            return
        bot_user = info.get("username", None)
        if not bot_user:
            messagebox.showerror("Error", "No username found in getMe result!")
            return

        self.log(f"[getMe] Bot validated: @{bot_user}")
        messagebox.showinfo("getMe", f"Bot validated: @{bot_user}")

        self.bot_token = parsed_token
        self.bot_username = bot_user

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.telethon_send_start(bot_user))

        my_id, last_id = self.get_updates(parsed_token)
        if not my_id or not last_id:
            messagebox.showerror("Error", "getUpdates gave no valid results.")
            return

        self.my_chat_id = my_id
        self.last_message_id = last_id

        info_msg = (
            f"Bot username: @{bot_user}\n"
            f"my_chat_id: {my_id}\n"
            f"last_message_id: {last_id}\n\n"
            "We will now try older IDs in a background thread..."
        )
        self.log("[Infiltration] " + info_msg.replace("\n", " | "))
        messagebox.showinfo("Infiltration Complete", info_msg)

        attacker_id = self.chatid_entry.get().strip()
        if not attacker_id or "Example:" in attacker_id:
            self.log("⚠️ No attacker chat ID provided. Skipping older ID check.")
            return

        self.stop_flag = False

        t = threading.Thread(target=self.infiltration_process, args=(attacker_id,))
        t.start()

    def forward_all_messages(self):
        if not self.bot_token or not self.bot_username or not self.my_chat_id or not self.last_message_id:
            messagebox.showerror("Error", "You must do Infiltration Steps first!")
            return

        from_chat_id = self.chatid_entry.get().strip()
        if not from_chat_id or "Example:" in from_chat_id:
            messagebox.showerror("Error", "Malicious Chat ID is empty!")
            return

        self.stop_flag = False
        self.stopped_id = 0
        self.current_msg_id = 0
        self.resume_button.config(state="disabled")

        self.forward_continuation(from_chat_id, start_id=1)

    def forward_continuation(self, attacker_chat_id, start_id):
        def do_forward():
            max_id = self.last_message_id
            success_count = 0

            for msg_id in range(start_id, max_id + 1):
                if self.stop_flag:
                    self.stopped_id = msg_id
                    self.root.after(0, lambda: self.log(f"⏹️ Stopped at ID {msg_id} by user."))
                    break
                ok = self.forward_msg(self.bot_token, attacker_chat_id, self.my_chat_id, msg_id)
                if ok:
                    success_count += 1

            if not self.stop_flag:
                txt = f"Forwarded from ID {start_id}..{max_id}, total success: {success_count}"
                self.root.after(0, lambda: [
                    self.log("[Result] " + txt.replace("\n", " | ")),
                    messagebox.showinfo("Result", txt)
                ])
            else:
                partial_txt = f"Stopped at ID {self.stopped_id}, total success: {success_count}.\nResume if needed."
                self.root.after(0, lambda: [
                    self.log("[Result] " + partial_txt.replace("\n", " | "))
                ])

        t = threading.Thread(target=do_forward)
        t.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramGUI(root)
    root.mainloop()
