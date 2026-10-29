"""Print release notes from the two verified build manifests (cwd: assets)."""
import json
from pathlib import Path

print("Experimental **Canon EOS 60D** builds. Requires **Canon firmware 1.1.1**; incompatible with 1.1.2.\n")
print("| Language | Source commit |\n| --- | --- |")
for language, label in [("en", "English"), ("zh", "Chinese")]:
    data = json.loads(Path(f"magiclantern-eos60d-111-{language}.json").read_text())
    spec = data["source"]
    url = spec["url"].removesuffix(".git")
    print(f"| {label} | [{spec['commit'][:12]}]({url}/commit/{spec['commit']}) |")
print("\nChoose one language ZIP. Source archives, build manifests and SHA256SUMS.txt accompany the binaries.")
print("\nBoth packages passed static validation. These CI binaries have **not been hardware-tested**. Chinese translation includes some English labels. No optional modules are pre-enabled.")
print("\nRead the [installation notes](https://github.com/xhd0728/canon-firmware/blob/main/docs/INSTALL.md). Canon firmware links are in the [README](https://github.com/xhd0728/canon-firmware#downloads).")
