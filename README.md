# py-clash-bot

**py-clash-bot** is an open-source automation tool that allows you to automate your Clash Royale gameplay on Windows using an emulated Android phone. The bot uses advanced image recognition, mouse control, and Android emulation to perform a comprehensive range of tasks automatically, letting you focus on strategy while it handles the daily grind.

_Join our [Discord server](https://discord.gg/nqKRkyq2UU) for support, updates, and community discussions!_

## ✨ Features

### 🎮 **Battle Automation**

- **Trophy Road 1v1 Battles** - Automatically fight in trophy road ladder matches
- **Path of Legends 1v1 Battles** - Battle in the competitive Path of Legends mode
- **2v2 Battles** - Team up with clan members for 2v2 matches
- **Random Decks** - Randomize your deck selection before each battle
- **Smart Battle Management** - Skip fights when chests are full, disable win/loss tracking

### 🎁 **Rewards & Collection**

- **Card Mastery Rewards** - Collect mastery rewards earned from battles
- **Card Upgrades** - Upgrade your current deck after each battle

### ⚙️ **Advanced Settings**

- **Emulator Support** - Works with MEmu, BlueStacks 5, and Google Play Games emulators
- **Render Mode Selection** - Choose between OpenGL, DirectX, and Vulkan rendering
- **Real-time Statistics** - Track wins, losses, chests opened, and more
- **Performance Monitoring** - Monitor bot runtime, failures, and account switches
- **Discord Webhook Notifications** - Receive real-time notifications about bot status, battle results, and errors directly in Discord

## 🚀 Setup Instructions

**py-clash-bot** supports three emulators. Choose the one that works best for your system:

### Option 1: MEmu Emulator

1. **Download MEmu 9.2.5.0** - Get it from the [official site](https://www.memuplay.com/) or use this [working installer](https://drive.google.com/file/d/1FDMa5oKIhbM_X2TGHg6qSi3bnIuIXcPf/view?usp=sharing) (version 9.2.5.0 recommended)
2. **Install MEmu** - Run the MEmu installer
3. **Download py-clash-bot** - Get the latest release from [https://github.com/pyclashbot/py-clash-bot/releases](https://github.com/pyclashbot/py-clash-bot/releases)
4. **Install py-clash-bot** - Run the installer
5. **Create the VM** - Start the bot once to let it automatically create the "pyclashbot-96" MEmu emulator
6. **Install Clash Royale** - Install Clash Royale manually on the "pyclashbot-96" emulator via Google Play Store
7. **Complete setup** - Open Clash Royale manually, complete the tutorial, and optionally sign in to your account
8. **Close MEmu** - Close the MEmu emulator completely
9. **Start automation** - Start the bot, configure your settings, then click "Start" to begin automation

**Troubleshooting MEmu:**
- Switch render mode to Vulkan, DirectX, or OpenGL if experiencing issues
- Delete the VM and let the bot create a new one
- Enable UEFI in BIOS if needed

### Option 2: BlueStacks 5 Emulator

1. **Download BlueStacks 5** - Get it from the official site: https://www.bluestacks.com (ensure BlueStacks 5, not X/10)
2. **Install BlueStacks 5** - Run the BlueStacks 5 installer
3. **Download py-clash-bot** - Get the latest release from [https://github.com/pyclashbot/py-clash-bot/releases](https://github.com/pyclashbot/py-clash-bot/releases)
4. **Install py-clash-bot** - Run the installer
5. **Create the instance** - Start the bot, choose `Emulator Type: BlueStacks 5`, select a render mode (OpenGL/DirectX/Vulkan) under BlueStacks Settings and then click "Start" to let it automatically create the "pyclashbot-96" Bluestacks 5 emulator Instance. Alternativly open the BlueStacks Multi-Instance Manager and create a fresh Pie 64-bit instance and retry it will automatically rename/configure it as "pyclashbot-96"
6. **Install Clash Royale** - Install Clash Royale manually on the "pyclashbot-96" emulator via Google Play Store
7. **Complete setup** - Open Clash Royale manually, complete the tutorial, and optionally sign in to your account
8. **Close BlueStacks 5** - Fully close the BlueStacks 5 emulator
9. **Start automation** - Start the bot, choose `Emulator Type: BlueStacks 5`, select a render mode (OpenGL/DirectX/Vulkan) under BlueStacks Settings, then click "Start"

**Troubleshooting BlueStacks 5:**
- Open the Bluestacks Multi-Instance Manger -> Click on Instance (Blue, Bottom left) -> Choose Fresh instance -> Choose Android Version Pie 64-bit -> Click on Next -> Click on Create, then click Retry in the bot or restart it fully.
- Try switching render mode (OpenGL/DirectX/Vulkan) in the bot and start again
- Restart your PC and let the bot try it again

### Option 3: Google Play Games Emulator

1. **Download Google Play Games Emulator** - Get it from [https://developer.android.com/games/playgames/emulator](https://developer.android.com/games/playgames/emulator)
2. **Install the emulator** - Run the Google Play installer
3. **Initial setup** - Boot the Google Play Games Emulator once. This will trigger a Google sign-in flow in your web browser - complete this process. If prompted to allow USB debugging, click "Accept"
4. **Download py-clash-bot** - Get the latest release from [https://github.com/pyclashbot/py-clash-bot/releases](https://github.com/pyclashbot/py-clash-bot/releases)
5. **Install Clash Royale** - Download Clash Royale manually from the emulator
6. **Complete setup** - Start Clash Royale manually, complete the tutorial, and optionally sign in to your account
7. **Optional: Set display ratio** - Go to Google Play Emulator > Developer Options > Display Ratio > 9:16 (Portrait) for optimal look
8. **Close emulator** - Close the Google Play emulator completely
9. **Start automation** - Start the bot, configure your settings, then click "Start" to begin automation

### Important Notes

- **Language Setting** - Ensure Clash Royale is set to English for optimal bot performance
- **Tutorial Completion** - The tutorial must be completed manually before starting the bot
- **Account Setup** - Sign in with SuperCell ID or create a new account as needed

## 📢 Discord Webhook Notifications

Receive real-time notifications about your bot's activity directly in Discord! This feature allows you to monitor your bot remotely, getting notified about important events like bot starts, stops, battle results, and errors.

### Setting Up Discord Webhooks

1. **Create a Discord Webhook**
   - Open your Discord server
   - Go to **Server Settings** → **Integrations** → **Webhooks**
   - Click **New Webhook** or **Create Webhook**
   - Name your webhook (e.g., "PyClashBot Notifications")
   - Copy the webhook URL (starts with `https://discord.com/api/webhooks/`)

2. **Configure in py-clash-bot**
   - Open the bot application
   - Navigate to the **Misc** tab
   - Find the **Discord Webhook** section
   - Paste your webhook URL into the **Webhook URL** field
   - The webhook URL is automatically saved in your settings

### What You'll Receive

The bot will send notifications for:

- **🤖 Bot Started** - When the bot begins automation (includes current state)
- **🛑 Bot Stopped** - When the bot stops (includes final statistics: wins, losses, win rate, runtime, failures)
- **🎉 Battle Won** - When you win a battle (includes battle type and win rate)
- **😔 Battle Lost** - When you lose a battle (includes battle type and win rate)
- **⚠️ Bot Error** - When an error occurs (includes error message and context)

### Notes

- **Optional Feature** - Discord webhooks are completely optional. Leave the field empty to disable notifications.
- **Privacy** - Webhook URLs are stored locally in your user settings and are not shared with anyone.
- **Non-Blocking** - Webhook notifications are sent asynchronously and won't slow down or interfere with bot operation.
- **Error Handling** - If a webhook fails to send (e.g., invalid URL or network issues), the bot will continue operating normally without disruption.

## 🔧 Emulator Debugging

Having trouble with your emulator? This section provides troubleshooting tips for common issues with all supported emulators.

### BlueStacks 5 Emulator Debugging

- Use BlueStacks 5 only (BlueStacks 10/X are not supported)
- Ensure install path exists: `C:\Program Files\BlueStacks_nxt`
- If startup fails, create a clean "Pie 64-bit (Android 9)" instance in Multi-Instance Manager (no Google account yet), then click Retry in the bot so it can auto-configure
- Switch render mode in the bot (OpenGL/DirectX/Vulkan) if you see black screens or poor performance, then start again
- Fully close BlueStacks if it becomes unresponsive; the bot will relaunch it

### Google Play Games Emulator Debugging

- **Use the correct version** - Make sure you're using the DEVELOPER Google Play Games emulator, not the BETA version. Download it from [https://developer.android.com/games/playgames/emulator](https://developer.android.com/games/playgames/emulator)
- **Watch for login prompts** - Google Play makes a popup in your default browser for the Google sign-in prompt. Sometimes you might miss this during emulator boot, and it'll hang forever. If you're experiencing booting issues, check for a login prompt in a minimized browser window!
- **Adjust rendering settings** - If it's still not rendering properly, try adjusting render mode settings at System tray > Google Play Games emulator > Graphics settings > Vulkan device override OR Graphics > Graphics stack override
- **Installer download fix** - If you're having trouble downloading the emulator installer, this tested solution works: Open your task manager, click File, press "Run new task", drop the installer path, and press "Run as admin"

### MEmu Emulator Debugging  

- **Hardware requirements** - MEmu is more hardware intensive, so if you're on a low-end machine try using Google Play Games emulator instead
- **Black screen or boot issues** - If it's showing a black screen or never fully booting, try adjusting render mode via the ClashBot settings, then start the bot to apply those settings
- **BIOS requirements** - MEmu REQUIRES your BIOS to have UEFI and Hyper-V enabled!
  - Enable UEFI: [https://www.youtube.com/watch?v=uAMLGIlFMdI](https://www.youtube.com/watch?v=uAMLGIlFMdI)  
  - Enable Hyper-V: [https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v?tabs=powershell&pivots=windows](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v?tabs=powershell&pivots=windows)
- **Version conflicts** - Some old versions of pyclashbot create corrupt instances of MEmu. If you're switching between versions and MEmu is breaking, try deleting your existing MEmu VMs, or reinstalling MEmu entirely

## 🎯 Demo

<img src="https://github.com/pyclashbot/py-clash-bot/blob/master/assets/demo-game.gif?raw=true" width="50%" alt="Game Demo"/><img src="https://github.com/pyclashbot/py-clash-bot/blob/master/assets/demo-gui.gif?raw=true" width="50%" alt="GUI Demo"/>

_Left: Bot automation in action | Right: User interface and controls_

## 🤝 Contributing

We welcome contributions from the community! Whether you have ideas for new features, bug reports, or want to help with development, there are many ways to get involved:

- **Report Issues** - Open an issue on [GitHub Issues](https://github.com/pyclashbot/py-clash-bot/issues)
- **Feature Requests** - Suggest new automation features or improvements
- **Code Contributions** - Check out our [Contributing Guide](CONTRIBUTING.md)
- **Community Support** - Help other users on our [Discord server](https://discord.gg/nqKRkyq2UU)

## ⚠️ Disclaimer

This tool is designed for educational and automation purposes. Please ensure you comply with Clash Royale's Terms of Service and use responsibly. The developers are not responsible for any consequences resulting from the use of this software.

---

**Made with ❤️ by the py-clash-bot community**

_Automate your Clash Royale experience and focus on what matters most - strategy and fun!_
