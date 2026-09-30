import os
import glob

adapters_dir = "src/ats/adapters"
for filepath in glob.glob(f"{adapters_dir}/*/crawler.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "TokenDiscoveryService.resolve_token(" in content:
        print(f"Patching {filepath}")
        # We find the assignment to self.board_token = TokenDiscoveryService...
        # and prepend the metadata check.
        new_content = content.replace(
            "self.board_token = TokenDiscoveryService.resolve_token(",
            "self.board_token = self.company.get('metadata', {}).get('board_token')\n        if not self.board_token:\n            self.board_token = TokenDiscoveryService.resolve_token("
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
    else:
        print(f"Skipping {filepath}, no TokenDiscoveryService call found.")
