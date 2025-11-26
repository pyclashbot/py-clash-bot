# py-clash-bot (macOS – BlueStacks ADB Edition)

This is an unofficial macOS build of **py-clash-bot**, an automation tool for Clash Royale that runs against a **BlueStacks emulator** using **ADB** (Android Debug Bridge).

On macOS, the bot:

- Connects to an existing BlueStacks instance over ADB  
- Uses image recognition + input automation to play Clash Royale for you  
- Handles the “grind” while you focus on your account and deck strategy  

> **Important:** This macOS version is **only tested with BlueStacks** (ADB mode).  
> MEmu and Google Play Games Emulator are **not** supported or tested on macOS.

---

## ✨ Features

### 🎮 Battle Automation

- Trophy Road 1v1 battles  
- Path of Legends 1v1 battles  
- 2v2 battles  
- Optional random deck selection  
- Smart battle management (skip fights when chests are full, etc.)

### 🎁 Rewards & Collection

- Collect card mastery rewards  
- Upgrade cards in your current deck automatically (if enabled)

### 📊 Stats & Settings

- Track wins, losses, chest cycles, and runtime  
- Adjust battle behavior and deck logic  
- Save / load user settings between sessions

> Note: Feature set is based on the original Windows project; some emulator-specific features (like auto-creating BlueStacks instances) are **not used** on macOS. Here you connect to an already-running BlueStacks instance via ADB.

---

## 💻 System Requirements (macOS)

- Apple Silicon Mac (M1, M2, M3, etc.)  
- macOS 13+ (tested on a recent macOS version)  
- **BlueStacks for macOS** installed  
- Clash Royale installed and working inside BlueStacks  
- Enough performance to run BlueStacks + the bot at the same time

The macOS app bundles:

- Its own Python runtime  
- A local copy of `adb`  

You do **not** need to install Python or Android platform-tools.

---

## 📦 Installation (macOS)

1. **Move to Applications**

   - Drag `ClashBot.app` into your `/Applications` folder.  
   - You can also keep it elsewhere, but `/Applications` is recommended.

2. **First launch (Gatekeeper)**

   macOS will likely warn about an “unidentified developer”:

   - Open **Finder** → **Applications**  
   - Right-click (or Control-click) `ClashBot.app` → **Open**  
   - In the dialog, click **Open** again  

   After the first time, you can open it normally by double-clicking.

---

## 🔗 BlueStacks Setup (ADB on macOS)

The bot talks to BlueStacks through **ADB**. On macOS, you must turn this on in BlueStacks itself.

### 1. Enable ADB in BlueStacks

1. Open **BlueStacks** on your Mac.
2. Go to **Settings** (gear icon).
3. Open **Advanced** (or **Advanced settings**).
4. Find the option **Android Debug Bridge (ADB)** or **Enable ADB**.
5. Turn **ADB** **ON**.
6. Make sure Clash Royale is installed and you can open it normally inside BlueStacks.

Leave BlueStacks running.

---

## 🤝 Connecting the Bot to BlueStacks (ADB Mode)

1. **Start ClashBot**

   - Open `ClashBot.app` from `/Applications`.

2. **Select the ADB device**

   - In the bot UI, make sure the emulator/device type is set to **ADB** (or the appropriate option for ADB devices).
   - Click the **Refresh** button in the ADB section to scan for ADB devices/ports.
   - You should see a device corresponding to your BlueStacks instance (typically something like `localhost:5555` or a similar ADB port).

3. **Connect**

   - Select the BlueStacks ADB device in the list.
   - Click **Connect** (or the button in the UI that attaches the bot to that device).
   - The status should show that you are connected.

4. **Set Resolution / DPI**

   To ensure the detection templates match the game:

   - Use the **Set Resolution** or similar button in the bot UI to apply the recommended resolution and pixel density (DPI) to Clash Royale within BlueStacks.
   - Follow any on-screen instructions in the bot UI about the required resolution and orientation.

---

## ▶️ Starting the Bot

Once you are connected and resolution is set:

1. Open **Clash Royale** in BlueStacks and get it to the appropriate screen (main menu / battle screen depending on the bot’s instructions).
2. In the ClashBot UI, configure your desired options:
   - Battle mode (Trophy Road, Path of Legends, 2v2, etc.)
   - Deck/strategy settings
   - Rewards/upgrade options
3. Click **Start** / **Start Bot**.

If everything is configured correctly, the bot will begin to:

- Read the game screen from BlueStacks over ADB  
- Decide on actions based on templates and logic  
- Simulate taps/clicks in the emulator to play for you  

---

## 🛠 Troubleshooting (macOS)

### Bot does nothing when I hit Start

- Make sure:
  - BlueStacks is **running**.
  - ADB is **enabled** in BlueStacks Settings → Advanced.
  - You clicked **Refresh** in the bot to detect ADB devices and then **Connect**.
  - You have set the **resolution** via the bot’s “Set Resolution” control.
  - Clash Royale is open and visible in BlueStacks.

If it still doesn’t do anything:

- Check log files:

  ```text
  ~/Library/Logs/pyclashbot/pyclashbot.log
  ~/Library/Logs/ClashBot-error.log