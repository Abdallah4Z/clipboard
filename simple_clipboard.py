import os
import json
import time
import threading
import subprocess
from pathlib import Path
import pyperclip
import customtkinter as ctk
import sys

# ---------------- CONFIG ----------------
DATA_DIR = Path.home() / ".local" / "share" / "simple_clipboard"
DATA_FILE = DATA_DIR / "history.json"
POLL_INTERVAL = 0.5  # Check every 500ms
REFRESH_INTERVAL = 1000 # 1000ms = 1 second for GUI refresh
# ----------------------------------------

# UI Settings
MAX_HISTORY = 20
TRUNCATE_LENGTH = 65
POPUP_WIDTH = 400
FONT_SIZE = 12
THEME = "dark"  # dark or light
# ----------------------------------------

DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_history():
    """Load history from JSON file."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"Error loading history: {e}")
            pass
    return []


def save_history(history):
    """Save history to JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history[:MAX_HISTORY], f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving history:", e)


def add_to_history(text):
    """Add a new item to the history, preventing duplicates."""
    text = str(text)
    if len(text.strip()) == 0:
        return
    hist = load_history()
    # Check if the new text is the same as the MOST RECENT item
    if hist and hist[0] == text:
        return
    # Remove older duplicates before inserting
    hist = [item for item in hist if item != text]
    hist.insert(0, text)
    save_history(hist[:MAX_HISTORY])
    print(f"Added: {truncate(text)}")


def monitor_clipboard_daemon(stop_event):
    """
    Continuously poll ONLY the main (Ctrl+C) clipboard.
    """
    last_clipboard = ""
    while not stop_event.is_set():
        try:
            # 1. Check the main (Ctrl+C) clipboard
            cur_clipboard = pyperclip.paste()
            if cur_clipboard != last_clipboard:
                add_to_history(cur_clipboard)
                last_clipboard = cur_clipboard

        except pyperclip.PyperclipException as e:
            print(f"Pyperclip error: {e}. Is a clipboard tool installed (e.g., xclip/xsel)?")
            stop_event.wait(2)
        except Exception:
            pass
        stop_event.wait(POLL_INTERVAL)


def truncate(s, n=TRUNCATE_LENGTH):
    """Truncate text intelligently, preserving newlines as preview."""
    s = str(s).strip()
    # Show first line or two for multi-line content
    lines = s.split('\n')
    if len(lines) > 1:
        preview = lines[0][:n] + " ⏎ " + (lines[1][:15] if len(lines) > 1 else "")
        if len(preview) > n:
            return preview[:n-3] + "..."
        return preview
    return s if len(s) <= n else s[: n - 3] + "..."


def try_send_ctrl_v():
    """Simulate Ctrl+V keypress using xdotool (Linux only)."""
    if sys.platform != 'linux':
        return

    try:
        time.sleep(0.05)
        subprocess.Popen(["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("--- xdotool NOT FOUND ---")
        print("Auto-paste failed. Please install xdotool for this feature.")
        print("e.g., sudo apt install xdotool")
    except Exception as e:
        print(f"xdotool paste error: {e}")


def open_popup():
    """Display the clipboard history popup window."""
    history = load_history()

    # Apply theme
    if THEME == "light":
        ctk.set_appearance_mode("light")
        bg_color = "#f2f2f2"
        text_color = "#1a1a1a"
        hover_color = "#e0e0e0"
    else:  # dark
        ctk.set_appearance_mode("dark")
        bg_color = "#1e1e1e"
        text_color = "#e0e0e0"
        hover_color = "#2a2a2a"

    root = ctk.CTk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()  # Force focus on the popup
    root.is_pasting = False  # Flag to prevent focus-out on paste
    root.current_history = history # Store initial history

    # Calculate dimensions
    width = POPUP_WIDTH
    height = 500
    item_height = 40

    SCROLL_FRAME_PAD_X = 10
    ROW_FRAME_PAD_X = 5

    root.update()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    MARGIN = 20
    x = screen_w - width - MARGIN
    y = screen_h - height - MARGIN
    root.geometry(f"{width}x{height}+{x}+{y}")

    # === DRAG FUNCTIONALITY ===
    drag_data = {"x": 0, "y": 0}

    def start_move(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def do_move(event):
        deltax = event.x - drag_data["x"]
        deltay = event.y - drag_data["y"]
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    # === Ultra-flat main container ===
    container = ctk.CTkFrame(root, fg_color=bg_color, border_width=0)
    container.place(relx=0, rely=0, relwidth=1, relheight=1)

    def close_popup(_=None):
        try:
            root.grab_release()
        except Exception:
            pass
        root.destroy()

    def clear_all():
        save_history([])
        close_popup()

    # Top button bar
    btn_bar = ctk.CTkFrame(container, fg_color=bg_color, height=40)
    btn_bar.pack(fill="x", padx=10, pady=(10, 5))
    btn_bar.bind("<ButtonPress-1>", start_move)
    btn_bar.bind("<B1-Motion>", do_move)

    # Title Label
    title_label = ctk.CTkLabel(
        btn_bar,
        text="Clipboard 0.1",
        font=("Arial", FONT_SIZE, "bold"),
        text_color=text_color
    )
    title_label.pack(side="left", padx=(10, 0))
    title_label.bind("<ButtonPress-1>", start_move)
    title_label.bind("<B1-Motion>", do_move)

    # Right-aligned buttons
    close_btn = ctk.CTkButton(
        btn_bar, text="✖ Close", fg_color=bg_color, hover_color=hover_color,
        text_color=text_color, command=close_popup, width=80, height=30,
        font=("Arial", FONT_SIZE), border_width=0
    )
    close_btn.pack(side="right", padx=2)

    clear_btn = ctk.CTkButton(
        btn_bar, text="🗑 Clear All", fg_color=bg_color, hover_color=hover_color,
        text_color=text_color, command=clear_all, width=100, height=30,
        font=("Arial", FONT_SIZE), border_width=0
    )
    clear_btn.pack(side="right", padx=2)

    # Scrollable content area
    scroll = ctk.CTkScrollableFrame(
        container, fg_color=bg_color, border_width=0, width=width - 20,
        height=height - 60,
        scrollbar_fg_color=bg_color,
        scrollbar_button_color=bg_color,
        scrollbar_button_hover_color=bg_color
    )
    scroll.pack(padx=SCROLL_FRAME_PAD_X, pady=5, fill="both", expand=True)

    def paste_and_close(text):
        """Copy text, close window, and paste it with Ctrl+V."""
        try:
            root.is_pasting = True  # Set flag BEFORE losing focus
            
            # 1. Set clipboard
            pyperclip.copy(text)
            print(f"Copied to clipboard: {text[:50]}...")

            # 2. Close window
            try:
                root.grab_release()
            except:
                pass
            root.withdraw()

    
            # 3. Paste
            threading.Thread(target=try_send_ctrl_v).start()

            # 4. Then destroy
            root.after(100, root.destroy)
        except Exception as e:
            print(f"Paste error: {e}")
            close_popup()

    root.bind("<Escape>", close_popup)

    def on_focus_out(event):
        if not root.is_pasting:
            print("Focus lost, closing popup.")
            close_popup()

    root.bind("<FocusOut>", on_focus_out)


    def refresh_list():
        """Checks for history updates and rebuilds the list if needed."""
        try:
            new_history = load_history()
            
            # If the history hasn't changed, just reschedule and return
            if new_history == root.current_history:
                root.after(REFRESH_INTERVAL, refresh_list) # Check again
                return

            # History has changed, update the internal state
            root.current_history = new_history
            
            # Clear the old list
            for widget in scroll.winfo_children():
                widget.destroy()

            # --- Re-build the list ---
            if not new_history:
                ctk.CTkLabel(
                    scroll, text="📋 No clipboard history yet",
                    font=("Arial", FONT_SIZE + 1), text_color=text_color
                ).pack(pady=50)
            else:
                for idx, item in enumerate(new_history): # Use new_history
                    row = ctk.CTkFrame(scroll, fg_color=bg_color, height=item_height)
                    row.pack(fill="x", pady=1, padx=ROW_FRAME_PAD_X)

                    text_btn = ctk.CTkButton(
                        row, text=truncate(item), anchor="w", height=item_height,
                        command=lambda t=item: paste_and_close(t), fg_color=bg_color,
                        hover_color=hover_color, text_color=text_color,
                        font=("Arial", FONT_SIZE), border_width=0
                    )
                    text_btn.pack(side="left", fill="x", expand=True)
            
            # Schedule the next refresh
            root.after(REFRESH_INTERVAL, refresh_list)
        
        except Exception:
            # This can happen if the window is destroyed
            # while a refresh is pending. It's safe to ignore.
            pass

    # Start the refresh loop
    refresh_list()

    root.mainloop()


def main():
    """Main execution function."""
    stop_event = threading.Event()

    threading.Thread(target=monitor_clipboard_daemon, args=(stop_event,), daemon=True).start()

    if len(sys.argv) > 1 and sys.argv[1] == "--popup":
        open_popup()
        sys.exit()

    print("SimpleClipboard monitor running in background.")
    print("Monitoring ONLY Ctrl+C clipboard (selection is ignored).")
    print("Use the ' --popup ' argument to open the GUI (e.g., via a manual system shortcut).")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping SimpleClipboard...")
        stop_event.set()


if __name__ == "__main__":
    main()