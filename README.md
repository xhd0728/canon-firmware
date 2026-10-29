# Magic Lantern for Canon EOS 60D

English and Chinese community builds for **EOS 60D · Canon firmware 1.1.1**.
Experimental; not affiliated with Canon or an official Magic Lantern release.

## Downloads

[Releases](https://github.com/xhd0728/canon-firmware/releases) contain `en` and `zh` SD-card ZIPs, matching source archives, build manifests and SHA-256 checksums. Chinese builds include translated menus and help; some labels remain English.

Canon original firmware:

- **1.1.1 — required for these ML builds:** [official download (DMG)](https://gdlp01.c-wss.com/gds/1/0400000551/01/eos60d-v111-mac.dmg) · [Canon notice](https://www.cla.canon.com/en/support/product-advisories/eos-60d-firware-1)
- **1.1.2 — incompatible with these ML builds:** [Canon download page](https://hk.canon/en/support/0400283502)

Canon firmware is linked, not redistributed. See [installation notes](docs/INSTALL.md) before using either package. Never install a 60D package on another camera.

## Build / release

Open **Actions → Build EOS 60D → Run workflow**. Choose `both`, `en`, or `zh`. Builds are downloadable as workflow artifacts. To publish a prerelease, enable `publish` and provide a new tag, e.g. `60d-2026.10.30` (publishing builds both languages).

Local build (Ubuntu x86-64 or Apple Silicon macOS; Python 3.12+, make, Git, curl, zip):

```sh
python3 scripts/setup.py
python3 scripts/build.py --language en
python3 scripts/build.py --language zh
```

Sources and toolchains are pinned in [sources.lock.json](sources.lock.json). Builds validate package contents; this does not prove camera stability. Build timestamps make byte-for-byte reproducibility dependent on the build environment.

## Credits

[Magic Lantern upstream](https://github.com/reticulatedpines/magiclantern_simplified) · [Chinese translation by Chase Chan](https://github.com/ChaseChanCN/magiclantern) · [xPack Arm GCC](https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack)

GPL-2.0; upstream components retain their own notices. See [LICENSE](LICENSE). Use scoped Conventional Commits: `build(firmware): ...`, `ci(release): ...`.
