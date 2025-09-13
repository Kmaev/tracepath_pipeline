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
    logging.error(f"PR_TRACEPATH_FRAMEWORK values if {str(FRAMEWORK_ROOT)}. Export it first.")
    sys.exit(1)

REPO = "AcademySoftwareFoundation/rez"
REZ_URL_TMPL = "https://github.com/{repo}/archive/refs/tags/{tag}.zip"
FALLBACK_TAG = "2.112.0"  # used if API call fails

REZ_DOWNLOAD_FOLDER = FRAMEWORK_ROOT / "_temp/rez"
REZ_INST_PATH = FRAMEWORK_ROOT / "rez"

ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification


def get_latest_release_tag(repo: str, timeout: int = 10) -> str:
    """Return the latest GitHub release tag (stable only)."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rez-bootstrap"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print(f"[warn] Could not fetch latest release: {e}. Falling back to {FALLBACK_TAG}")
        return FALLBACK_TAG


def unzip(url, folder):
    zip_file = ZipFile(BytesIO(urllib.request.urlopen(url).read()))
    zip_file.extractall(str(folder))


def get_rez_download_url():
    latest_tag = get_latest_release_tag(REPO)
    rez_download_url = REZ_URL_TMPL.format(repo=REPO, tag=latest_tag)
    return rez_download_url


def run(cmd, cwd=None, env=None):
    """Helper to run a shell command and stream output."""
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd, env=env)


def rez_install():
    for folder in os.listdir(REZ_DOWNLOAD_FOLDER):
        if folder.startswith("rez"):
            inst_script = os.path.join(str(REZ_DOWNLOAD_FOLDER), folder, "install.py")
            if os.path.exists(inst_script):
                print(inst_script)
                run(
                    ["python", inst_script, "-v", str(REZ_INST_PATH)]
                )


def bind_python():
    run(["rez-bind", "python"])


if __name__ == "__main__":
    try:
        rez_url = get_rez_download_url()
        unzip(rez_url, REZ_DOWNLOAD_FOLDER)
        rez_install()
        bind_python()
    finally:
        if REZ_DOWNLOAD_FOLDER.exists():
            print(f"Cleaning up {REZ_DOWNLOAD_FOLDER} ...")
            shutil.rmtree(REZ_DOWNLOAD_FOLDER, ignore_errors=True)
