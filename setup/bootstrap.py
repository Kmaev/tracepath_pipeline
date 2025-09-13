import logging
import os
import ssl
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

FRAMEWORK_ROOT = Path(os.environ.get("PR_TRACEPATH_FRAMEWORK"))
if not FRAMEWORK_ROOT:
    logging.error(f"PR_TRACEPATH_FRAMEWORK values if {str(FRAMEWORK_ROOT)}. Export it first.")
    sys.exit(1)

# TODO Add option to get the latest version of the release using github api
REZ_URL = "https://github.com/AcademySoftwareFoundation/rez/archive/refs/tags/2.112.0.zip"
REZ_DOWNLOAD_FOLDER = "/Users/kmaev/Documents/rez_test_iso"
REZ_INST_PATH = FRAMEWORK_ROOT / "rez"

ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification


def unzip(url, folder):
    zip_file = ZipFile(BytesIO(urlopen(url).read()))
    zip_file.extractall(str(folder))


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
    unzip(REZ_URL, REZ_DOWNLOAD_FOLDER)
    rez_install()
    bind_python()
