# py-clash-bot

An open-source automation tool for Clash Royale on Windows and macOS. Uses Android emulation and image recognition to automate card leveling, pass progression, and daily gameplay tasks.

[Join our Discord](https://discord.gg/nqKRkyq2UU) for support and updates.

## Features

**Battle Automation**
- Trophy Road 1v1, Path of Legends, and 2v2 battles
- Random deck selection
- Smart chest management

**Progression**
- Card mastery reward collection
- Automatic card upgrades
- Real-time win/loss tracking

**Emulator Support**
- MEmu, BlueStacks 5, Google Play Games
- OpenGL, DirectX, and Vulkan render modes

## Setup

### 1. Install py-clash-bot

**Windows:** Download the installer from [releases](https://github.com/pyclashbot/py-clash-bot/releases) and run it.

**macOS:** Download the DMG from [releases](https://github.com/pyclashbot/py-clash-bot/releases), drag to Applications. On first launch, go to **System Settings > Privacy & Security** and click "Allow" for py-clash-bot.

### 2. Install an Emulator

Choose one:

**MEmu (Windows only)**
- Download [MEmu 9.2.5.0](https://www.memuplay.com/) ([alternate link](https://drive.google.com/file/d/1FDMa5oKIhbM_X2TGHg6qSi3bnIuIXcPf/view?usp=sharing))
- Run the installer

**BlueStacks 5 (Windows/macOS)**
- Download [BlueStacks 5](https://www.bluestacks.com/) (not BlueStacks X/10)
- Run the installer

**Google Play Games (Windows only)**
- Download the [developer emulator](https://developer.android.com/games/playgames/emulator) (not BETA)
- Run the installer and complete the Google sign-in when prompted

### 3. Configure and Run

1. Start py-clash-bot
2. Go to the **Emulator** tab and select your emulator from the dropdown
3. Click **Start** — the bot creates the emulator instance automatically
4. Install Clash Royale on the emulator via Google Play Store
5. Open Clash Royale, complete the tutorial, set language to English
6. Close the emulator completely
7. Click **Start** again to begin automation

Default settings work for most users. Only enable "Show advanced settings" to change render mode if troubleshooting.

## Demo

<img src="https://github.com/pyclashbot/py-clash-bot/blob/master/assets/demo-game.gif?raw=true" width="50%" alt="Game Demo"/><img src="https://github.com/pyclashbot/py-clash-bot/blob/master/assets/demo-gui.gif?raw=true" width="50%" alt="GUI Demo"/>

## Troubleshooting

### MEmu

- Requires UEFI and Hyper-V enabled in BIOS ([enable UEFI](https://www.youtube.com/watch?v=uAMLGIlFMdI), [enable Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v))
- Hardware intensive — try Google Play Games on low-end machines
- Black screen or boot issues: switch render mode in bot settings (OpenGL/DirectX/Vulkan)
- Corrupt VMs from old versions: delete existing MEmu VMs or reinstall MEmu

### BlueStacks 5

- Must use BlueStacks 5, not BlueStacks X/10
- Expected install path: `C:\Program Files\BlueStacks_nxt`
- Startup fails: open Multi-Instance Manager, create fresh "Pie 64-bit" instance, leave other settings as default, click Retry in bot
- Black screen: switch render mode in bot settings

### Google Play Games

- Must use the DEVELOPER version, not BETA
- Hanging on boot: check for Google sign-in popup in a minimized browser window
- Rendering issues: adjust settings via System tray > Google Play Games > Graphics settings
- Installer won't download: open Task Manager > File > Run new task, paste installer path, check "Run as admin"
- Set emulator system language to English (in addition to game language)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) | [Discord](https://discord.gg/nqKRkyq2UU) | [Issues](https://github.com/pyclashbot/py-clash-bot/issues)

## License

Source: [NC-CL-1.0](LICENSE) | Assets: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) | [Commercial inquiries](LICENSE)
