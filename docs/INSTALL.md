# EOS 60D installation notes

These packages target **EOS 60D / Canon 1.1.1 only**. They are experimental community builds; compilation and checksum checks are not hardware testing. Firmware installation can make a camera unusable if interrupted. Canon's 1.1.1 notice describes an upgrade from 1.1.0, not a downgrade guarantee.

1. Use a fully charged battery and an SD/SDHC card no larger than 32 GB for the first ML installation. Back up the card.
2. Verify Canon **1.1.1** in the camera menu. If changing Canon firmware, follow the included Canon PDF first, then check ordinary photography before installing ML.
3. Low-level format the card in the camera. Extract one language ZIP to the card root: `autoexec.bin`, `ML/`, and `ML-SETUP.FIR`.
4. Set **M** mode and run Firmware Update. Follow the installer display. When it says **Please restart your camera**, restart; do not wait out a countdown labelled **uninstall**.
5. Press the trash/delete button to open ML. Test basic menus, shooting and playback before enabling optional modules. Save any generated `ML/LOGS/ROM*.BIN` privately.

Installation changes the camera boot flag. Do not delete `autoexec.bin` from a bootable ML card; follow the matching upstream uninstall procedure. Turn the camera off and wait for card access to finish before removing the card.

Firmware ZIPs contain no personal settings and do not pre-enable optional modules. For still photography, start with RAW histogram/zebras and playback zoom; use focus peaking, bracketing or focus stacking as needed. Dual ISO requires special postprocessing and is not a default image-quality upgrade.

Upstream instructions: [INSTALL.txt](https://github.com/reticulatedpines/magiclantern_simplified/blob/142472e95054d73640f50789ac0fd66325499d82/doc/INSTALL.txt).
