import os
from pathlib import Path
import tempfile
import shutil
import ssl, urllib.request
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen, urlretrieve
import subprocess
import sys



USD_URL = "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v25.08.zip"
USD_DOWNLOAD_FOLDER = Path(tempfile.gettempdir()) / "usd_test"  # temp folder
USD_BUILD_EXEC = USD_DOWNLOAD_FOLDER / "OpenUSD-25.08" / "build_scripts" / "build_usd.py"
USD_BUILD_DIR = Path(__file__).resolve().parent / "OpenUSD"

ssl._create_default_https_context = ssl._create_unverified_context # Disable SSL verification


def unzip(url, folder):
    zip_file = ZipFile(BytesIO(urlopen(url).read()))
    zip_file.extractall(str(folder))


def install(build_exec:str, build_dir:str):
    """
    Run the build process.

    Args:
        build_exec (str): Path to the build script to execute.
        build_dir (str): Directory where the package will be built/installed.
    """
    cmd = [sys.executable, build_exec, build_dir]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

def rez_build_install(rez_package_root):

    cmd = ["rez", "build", "--clean", "--install"]
    print("Running:", " ".join(cmd), "in", rez_package_root)
    subprocess.check_call(cmd, cwd=rez_package_root)


try:
    unzip(USD_URL, USD_DOWNLOAD_FOLDER)
    install(str(USD_BUILD_EXEC), str(USD_BUILD_DIR))

    package_root = Path(__file__).resolve().parent
    rez_build_install(package_root)

finally:
    # Cleanup temp folder after install
    if USD_DOWNLOAD_FOLDER.exists():
        print(f"Cleaning up {USD_DOWNLOAD_FOLDER} ...")
        shutil.rmtree(USD_DOWNLOAD_FOLDER, ignore_errors=True)

