import json
import logging
import os
import shutil
import ssl
import subprocess
import sys
import urllib.request
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

FRAMEWORK_ROOT = Path(os.environ.get("PR_TRACEPATH_FRAMEWORK"))
if not FRAMEWORK_ROOT:
    logging.error(f"PR_TRACEPATH_FRAMEWORK values if {FRAMEWORK_ROOT}. Export it first.")
    sys.exit(1)

THIRD_PARTY_PACKAGES = FRAMEWORK_ROOT / "rez_packages"
TRACE_MODULES = FRAMEWORK_ROOT / "modules"
TRACE_PATH_TERMINAL = FRAMEWORK_ROOT / "setup/tracepath_terminal"

REPO = "PixarAnimationStudios/OpenUSD"
USD_URL_TMPL = "https://github.com/{repo}/archive/refs/tags/v{tag}.zip"
FALLBACK_TAG = "25.08"  # used if API call fails

USD_DOWNLOAD_FOLDER = FRAMEWORK_ROOT / "_temp/usd"
USD_BUILD_DIR = THIRD_PARTY_PACKAGES / "usd/OpenUSD"

ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification


def get_build_exec(usd_download_folder):
    usd_build = None
    for folder in usd_download_folder.iterdir():
        if folder.name.startswith("OpenUSD"):

            usd_build = usd_download_folder / folder / "build_scripts" / "build_usd.py"
        else:
            continue

    return usd_build


def get_latest_release_tag(repo: str, timeout: int = 10) -> str:
    """Return the latest GitHub release tag."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rez-bootstrap"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print(f"[warn] Could not fetch latest release: {e}. Falling back to {FALLBACK_TAG}")
        return FALLBACK_TAG


def get_usd_download_url():
    latest_tag = get_latest_release_tag(REPO)
    usd_download_url = USD_URL_TMPL.format(repo=REPO, tag=latest_tag)
    return usd_download_url


def run(cmd, cwd=None, env=None):
    """Helper to run a shell command and stream output."""
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd, env=env)


def rez_pip_install(package: str):
    run(["rez-pip", "--install", package])


def rez_pip_bootstrap():
    rez_pip_pkg_list = ["PySide6", "PyOpenGL", "PyOpenGL-accelerate"]
    for pkg in rez_pip_pkg_list:
        rez_pip_install(pkg)


def unzip(url, folder):
    zip_file = ZipFile(BytesIO(urllib.request.urlopen(url).read()))
    zip_file.extractall(str(folder))


def execute_build_usd(build_exec: str, build_dir: str):
    """
    Run a deploy process inside a Rez environment
    with PySide6, PyOpenGL, and PyOpenGL_accelerate available.

    Args:
        build_exec (str): Path to the Python build/deploy script.
        build_dir (str): Directory where the package will be built/installed.
    """
    cmd = [
        "rez", "env", "PySide6", "PyOpenGL", "PyOpenGL_accelerate",
        "--", "python", build_exec, build_dir
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


def build_rez_third_party_package():
    for package in os.listdir(THIRD_PARTY_PACKAGES):
        if not package.startswith("."):  # Is there a better way to filter temp Py foders
            package_path = THIRD_PARTY_PACKAGES / package
            run(
                ["rez", "build", "--install"],
                cwd=package_path
            )


def build_rez_tracepath_packages():
    for package in os.listdir(TRACE_MODULES):
        if not package.startswith("."):
            package_path = TRACE_MODULES / package
            run(
                ["rez", "build", "--install"],
                cwd=package_path
            )


def build_rez_tracepath_terminal():
    run(
        ["rez", "build", "--install"],
        cwd=TRACE_PATH_TERMINAL
    )

if __name__ == "__main__":
    try:
        # Install packages that go via rez pip
        rez_pip_bootstrap()

        # Download and build USD
        usd_url = get_usd_download_url()
        unzip(usd_url, USD_DOWNLOAD_FOLDER)

        usd_build_script = get_build_exec(USD_DOWNLOAD_FOLDER)
        execute_build_usd(str(usd_build_script), str(USD_BUILD_DIR))

        build_rez_third_party_package()
        build_rez_tracepath_packages()
        build_rez_tracepath_terminal()

    finally:
        if USD_DOWNLOAD_FOLDER.exists():
            print(f"Cleaning up {USD_DOWNLOAD_FOLDER} ...")
            shutil.rmtree(USD_DOWNLOAD_FOLDER, ignore_errors=True)
