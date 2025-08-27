# py-clash-bot

**py-clash-bot** is an open-source automation tool that allows you to automate your Clash Royale gameplay on Windows using an emulated Android phone. The bot uses advanced image recognition, mouse control, and Android emulation to perform a comprehensive range of tasks automatically, letting you focus on strategy while it handles the daily grind.

_Join our [Discord server](https://discord.gg/nqKRkyq2UU) for support, updates, and community discussions!_

## ✨ Features

### 🎮 **Battle Automation**

- **Trophy Road 1v1 Battles** - Automatically fight in trophy road ladder matches
- **Path of Legends 1v1 Battles** - Battle in the competitive Path of Legends mode
- **2v2 Battles** - Team up with clan members for 2v2 matches
- **War Battles** - Participate in clan war battles automatically
- **Random Decks** - Randomize your deck selection before each battle
- **Random Plays** - Play cards randomly (ideal for low-end machines)
- **Smart Battle Management** - Skip fights when chests are full, disable win/loss tracking

### 🎁 **Rewards & Collection**

- **Chest Management** - Automatically unlock and open chests earned from battles
- **Battlepass Rewards** - Collect battlepass rewards (works for non-battlepass owners too)
- **Card Mastery Rewards** - Collect mastery rewards earned from battles
- **Daily Challenges** - Automatically claim daily and weekly challenge rewards
- **Level Up Rewards** - Collect level up chests and rewards
- **Bannerbox Chests** - Open bannerbox crates for additional rewards
- **Trophy Road Rewards** - Collect rewards from climbing the trophy ladder
- **Season Shop** - Automatically spend currency from 2v2 battles and events

### 🃏 **Card Management**

- **Card Requests** - Automatically request cards from your clan
- **Card Donations** - Donate cards to clan members
- **Free Donations** - Donate cards without spending gold
- **Shop Management** - Buy daily free shop offers and gold offers
- **Card Upgrades** - Upgrade your current deck after each battle
- **Bulk Upgrades** - Upgrade all cards in your collection

### ⚙️ **Advanced Settings**

- **Account Switching** - Switch between multiple accounts using SuperCell ID
- **Dual Emulator Support** - Works with both MEmu and Google Play Games emulators
- **Render Mode Selection** - Choose between OpenGL, DirectX, and Vulkan rendering
- **Real-time Statistics** - Track wins, losses, chests opened, and more
- **Performance Monitoring** - Monitor bot runtime, failures, and account switches

### 📊 **Comprehensive Statistics**

The bot tracks detailed statistics across three categories:

- **Battle Stats**: Wins, losses, win rate, cards played, battle counts by mode
- **Collection Stats**: Requests, donations, chests unlocked, rewards collected
- **Bot Stats**: Runtime, failures, account switches, and performance metrics

## 🚀 Setup Instructions

**py-clash-bot** supports two emulators. Choose the one that works best for your system:

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

### Option 2: Google Play Games Emulator

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
