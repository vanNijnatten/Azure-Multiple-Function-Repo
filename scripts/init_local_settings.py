"""Create `local.settings.json` for every app from its committed example.

`local.settings.json` holds local secrets and is git-ignored. Existing files are
left untouched.

Usage:
    uv run scripts/init_local_settings.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for example in sorted(ROOT.glob("apps/*/local.settings.example.json")):
        target = example.with_name("local.settings.json")
        if target.exists():
            print(f"exists:  {target.relative_to(ROOT)}")
            continue
        shutil.copyfile(example, target)
        print(f"created: {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
