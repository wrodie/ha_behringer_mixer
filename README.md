# Behringer Digital Mixer Integration For Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

This integration allows you to connect a Behringer Digital Mixer to Home Assistant.

For each mixer configured by this integration entities for the following are provided.:

For each Channel, Bus, DCA, Matrix, AuxIn, Main Faders, Channel->Bus sends and Bus->Matrix sends.

- Name (Read-only)
- Mute (SWITCH) (Read/Write)
- Fader (NUMBER) (Read/Write)
- Fader Value - dB (SENSOR) (Read-only)

In addition to these 'fader' related variables, also provided is

- Current scene/snapshot number/index (Read/Write)
- Firmware (Read only)
- USB Filename (Read only)
- USB Player/Recorder status (Read/Write)

## Mixers Supported

- X32
- XR12
- XR16
- XR18
- Wing

*Testing has been mostly on the X32, but has been physically tested agains X32, Wing and XR18*

## Data Updates

The data for the mixer is updated in real time, so each time a button is pressed or fader is moved on the mixer, this is updated in Home Assistant immediately.

## Installation

### HACS installation (recommended)

1. Install HACS. That way you get updates automatically.
1. Add this Github repository as custom repository in HACS settings.
1. Aearch and install "Behringer Mixer" in HACS and click install.
1. Restart Home Assistant,
1. Then you can add a Behringer Mixer integration in the integration page.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `ha_berhringer_mixer`.
1. Download *all* the files from the `custom_components/ha_berhringer_mixer/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Behringer Mixer"

## Configuration is done in the UI

- You are asked for the ip address/hostname
- You are asked for the type of mixer (choose from the list)
- You are asked for the name of the mixer
- You can choose which channels/busses/dcas etc to actually import (If you import everything there can be a lot)

To reconfigure the integration, click the configuration icon for the integration (three dots) and choose reconfigure. Note: If you remove entities from being tracked, the integration will NOT remove them from HomeAssistant, you must remove the excess entities yourself.

## Caveats

Connection to the mixer is performed via ip address using UDP. If the IP address for the mixer changes, you will need to edit the integration setup. To avoid this, set up a DHCP reservation on your router for your mixer so that it always has the same IP address.

This information on changes to the mixer is written to the HA history/recorder databases so this may result in lots of state being stored if the mixer changes a lot.  You may want to consider excluding these entities from storing history.

### Behringer Wing
The Wing is quite different to how the other X/M/X series mixers work. Not all the functionality of the the other mixers is supported with the wing with this Integration:
 - No Headamp support
 - No USB recorder support - USB player is supported
 - Bus->Bus send controls (Bus to Matrix/Main is supported)

I don't believe any of these are impossible to achieve, just because they are tricker, I haven't put in the time yet.  I'm not even sure if they are needed.

**WARNING - Subscriptions** - This integration makes use of OSC subscription to get updated values of controls.  Differently to the X-Series mixers the Wing only supports one client to receive this data at a time.  So this means if you are using another integration that makes use of this same OSC subscription on the mixer, eg [Bitfocus Companion](https://bitfocus.io/companion), then they will compete for the same connection and both won't work properly.  I believe other software such as Wing Edit/WingQ/Mixing Station make use of a different protocol and don't suffer with this problem.

**WARNING 2 - Loading Scenes** - While this integration does support loading Wing Snapshots, the Wing API only supports doing this when the mixer already has a show loaded.  If you are powering up your mixer, then you will need to set a show to autoload by prefixing its name with `STARTUP_`.

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/wrodie/ha_behringer_mixer.svg?style=for-the-badge
[commits]: https://github.com/wrodie/ha_behringer_mixer/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/wrodie/ha_behringer_mixer.svg?style=for-the-badge
[releases]: https://github.com/wrodie/ha_behringer_mixer/releases
[license-shield]: https://img.shields.io/github/license/wrodie/ha_behringer_mixer.svg?style=for-the-badge
