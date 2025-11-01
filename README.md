# SimpleClipboard 0.1

A simple, fast, and minimal clipboard manager for Linux. It runs in the background to save your clipboard history and opens with a keyboard shortcut.

## 1. Installation

There are two small dependencies and the app itself.

**A. Install Dependencies**

Open a terminal and run this command to install `python3-tk` (which lets the window draw itself) and `xdotool` (which handles the auto-pasting):

```bash
sudo apt install python3-tk xdotool
```
1. Download the `simple_clipboard` file from the **[releases page](https://github.com/Abdallah4Z/clipboard/releases)**.
2. Move it to a permanent folder, like `~/.local/bin/` (keeps your home folder clean):

```bash
mkdir -p ~/.local/bin
mv simple_clipboard ~/.local/bin/
```

3. Make the file executable:

```bash
chmod +x ~/.local/bin/simple_clipboard
```

> 💡 **Tip:** You can also download it directly using `wget`:

```bash
mkdir -p ~/.local/bin && \
wget -O ~/.local/bin/simple_clipboard https://github.com/Abdallah4Z/clipboard/releases/download/v0.1/simple_clipboard
chmod +x ~/.local/bin/simple_clipboard
```

### 2. How to Use


**Set Your Keyboard Shortcut**

This shortcut will instantly open your clipboard window anytime you need it.

1. Go to your system **Settings** > **Keyboard** > **Keyboard Shortcuts**.
2. Click **“Add new shortcut”** (or the `+` icon).
3. Give it a name: `Clipboard Popup`.
4. Set your preferred shortcut — `Super+V` (Windows key + V) is a great choice.
5. For the **Command**, use the full path to your app with the `--popup` flag:

   ```bash
   /home/abdallah/.local/bin/simple_clipboard --popup
   ```

   *(Replace `abdallah` with your username if needed).*

**That’s it!**
Once you’ve set your shortcut, press it anytime to open your clipboard history instantly.
