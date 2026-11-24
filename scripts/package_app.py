"""Build a deployable zip package for one Function App in this workspace.

Usage:
    uv run scripts/package_app.py api-app
    uv run scripts/package_app.py --all

The Azure Functions host expects `function_app.py` and `host.json` at the root of
the package and the dependencies in `.python_packages/lib/site-packages`. Workspace
packages (the app's own `src/` package and shared packages such as `common`) are
not on PyPI, so instead of letting Azure run `pip install -r requirements.txt` we
install everything here, for Linux, and deploy the result as-is
(remote build disabled).

The output is `dist/<app>.zip`; the unzipped staging folder is kept in `build/<app>`.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS_DIR = ROOT / "apps"
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"

# Files from the app folder that the Functions host needs at the package root.
APP_FILES = ("function_app.py", "host.json")

# Azure Functions on Linux runs on x86_64 with glibc.
PYTHON_PLATFORM = "x86_64-manylinux_2_28"


def available_apps() -> list[str]:
    return sorted(p.parent.name for p in APPS_DIR.glob("*/function_app.py"))


def run(*args: str) -> None:
    print("$", " ".join(args), flush=True)
    subprocess.run(args, check=True, cwd=ROOT)


def package_app(app: str, python_version: str) -> Path:
    app_dir = APPS_DIR / app
    staging = BUILD_DIR / app
    site_packages = staging / ".python_packages" / "lib" / "site-packages"
    requirements = BUILD_DIR / f"{app}.requirements.txt"

    shutil.rmtree(staging, ignore_errors=True)
    site_packages.mkdir(parents=True)

    # 1. Pin the app's runtime dependencies from uv.lock (no dev tools). Workspace
    #    members are exported as local paths and installed non-editable.
    run(
        "uv", "export", "--package", app, "--frozen", "--no-dev", "--no-editable",
        "--no-hashes", "--no-header", "--output-file", str(requirements),
    )  # fmt: skip

    # 2. Install them for the Azure (Linux) target, whatever OS we build on.
    run(
        "uv", "pip", "install", "--requirements", str(requirements), "--target", str(site_packages),
        "--python-version", python_version, "--python-platform", PYTHON_PLATFORM, "--no-deps", "--no-cache",
    )  # fmt: skip

    # 3. Add the files the host indexes.
    for name in APP_FILES:
        shutil.copy2(app_dir / name, staging / name)

    # 4. Smoke test: index the app using only the packaged files. `-S` keeps the
    #    workspace .venv off sys.path, so a missing dependency fails here, not in Azure.
    if python_version == f"{sys.version_info.major}.{sys.version_info.minor}":
        check = "import function_app; print(sorted(f.get_function_name() for f in function_app.app.get_functions()))"
        env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(staging), str(site_packages)])}
        print("Indexed functions: ", end="", flush=True)
        subprocess.run([sys.executable, "-S", "-c", check], check=True, cwd=staging, env=env)

    # 5. Zip it.
    DIST_DIR.mkdir(exist_ok=True)
    archive = shutil.make_archive(str(DIST_DIR / app), "zip", root_dir=staging)
    print(f"Packaged {app} -> {Path(archive).relative_to(ROOT)}")
    return Path(archive)


def main(argv: list[str] | None = None) -> int:
    apps = available_apps()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("app", nargs="?", choices=apps, help="the app folder name under apps/")
    target.add_argument("--all", action="store_true", help="package every app")
    parser.add_argument(
        "--python-version",
        default=(ROOT / ".python-version").read_text(encoding="utf-8").strip(),
        help="Python version of the Function App in Azure (default: .python-version)",
    )
    args = parser.parse_args(argv)

    for app in apps if args.all else [args.app]:
        package_app(app, args.python_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
