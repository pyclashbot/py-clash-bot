# NSIS custom installer

This directory contains `installer.nsh` and `/plugins` directory with custom NSIS plugins.

## `installer.nsh`

This file contains custom NSIS installer script. This file is included in the elecron-builder NSIS script, modifying the default installer behavior.

## `/plugins`

This directory contains custom NSIS plugins. These plugins are used in the `installer.nsh` file.

### `/plugins/INetC.dll`

This plugin is used to download files from the internet. It is used to install dependencies for the production install. This file is a [custom fork](https://github.com/DigitalMediaServer/NSIS-INetC-plugin) of the [INetC plugin](https://nsis.sourceforge.io/Inetc_plug-in). The license for use is included in the `LICENSE` file in this directory.
