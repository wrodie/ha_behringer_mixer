# Behringer Digital Mixer Integration For Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]


This integration allows you to connect a Behringer Digital Mixer to Home Assistant.

**Mixers Supported**
- X32
- XR12
- XR16
- XR18

*Testing has been mostly on the X32, but has been physically tested agains X32 and XR18*

For each mixer configured by this integration entities for the following are provided.:

For each Channel, Bus, DCA, Matrix, AuxIn and Main Faders
 - Name (Read only)
 - Mute (SWITCH) (Read/Write)
 - Fader (NUMBER) (Read/Write)
 - Fader Value - dB (SENSOR) (Read only)

In addition to these 'fader' related variables, also provided is
 - Current scene/snapshot number/index (Read/Write)
 - Firmware (Read only)

## Data Updates
The data for the mixer is updated in real time, so each time a button is pressed or fader is moved on the mixer, this is updated in Home Assistant immediately.



## Installation

**HACS installation (recommended)**

1. Install HACS. That way you get updates automatically.
1. Add this Github repository as custom repository in HACS settings.
1. Aearch and install "Behringer Mixer" in HACS and click install.
1. Restart Home Assistant,
1. Then you can add a Behringer Mixer integration in the integration page.

**Manual installation**

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `ha_berhringer_mixer`.
1. Download _all_ the files from the `custom_components/ha_berhringer_mixer/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Behringer Mixer"


## Configuration is done in the UI

<!---->
- You are asked for the ip address/hostname
- You are asked for the type of mixer (choose from the list)
- You are asked for the name of the mixer


## Caveats
Connection to the mixer is performed via ip address using UDP. If the IP address for the mixer changes, you will need to edit the integration setup. To avoid this, set up a DHCP reservation on your router for your mixer so that it always has the same IP address.

This information on changes to the mixer is written to the HA history/recorder databases so this may result in lots of state being stored if the mixer changes a lot.  You may want to consider excluding these entities from storing history.




## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***


[commits-shield]: https://img.shields.io/github/commit-activity/y/wrodie/ha_behringer_mixer.svg?style=for-the-badge
[commits]: https://github.com/wrodie/ha_behringer_mixer/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/wrodie/ha_behringer_mixer.svg?style=for-the-badge
[releases]: https://github.com/wrodie/ha_behringer_mixer/releases
[integration_blueprint]: https://github.com/ludeeus/integration_blueprint
[license-shield]: https://img.shields.io/github/license/ludeeus/integration_blueprint.svg?style=for-the-badge
