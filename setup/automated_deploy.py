import logging
import os
import shutil
import ssl
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

FRAMEWORK_ROOT = os.environ.get("PR_TRACEPATH_FRAMEWORK")
if not FRAMEWORK_ROOT:
    logging.error(f"PR_TRACEPATH_FRAMEWORK values if {FRAMEWORK_ROOT}. Export it first.")
    sys.exit(1)

THIRD_PARTY_PACKAGES = FRAMEWORK_ROOT / "rez_packages"
TRACE_MODULES = FRAMEWORK_ROOT / "modules"
TRACE_PATH_TERMINAL = FRAMEWORK_ROOT / "setup/tracepath_terminal"

USD_URL = "https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v25.08.zip"
USD_DOWNLOAD_FOLDER = Path(tempfile.gettempdir()) / "usd_test"  # temp folder
USD_BUILD_EXEC = USD_DOWNLOAD_FOLDER / "OpenUSD-25.08" / "build_scripts" / "build_usd.py"
USD_BUILD_DIR = THIRD_PARTY_PACKAGES / "usd/OpenUSD"

ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification


def run(cmd, cwd=None, env=None):
    """Helper to run a shell command and stream output."""
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd, env=env)


def rez_pip_install(package: str):
    # Install PySide6 into a Rez package with rez-pip
    run(["rez-pip", "--install", package])


def rez_pip_bootstrap():
    rez_pip_pkg_list = ["PySide6", "PyOpenGL", "PyOpenGL-accelerate"]
    for pkg in rez_pip_pkg_list:
        rez_pip_install(pkg)


def unzip(url, folder):
    zip_file = ZipFile(BytesIO(urlopen(url).read()))
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


try:
    # Install packages that go via rez pip
    rez_pip_bootstrap()
    # Download and build USD
    unzip(USD_URL, USD_DOWNLOAD_FOLDER)

    # For build execute to work in local package repo should be: arch, os, platform, python
    # TODO This should be automated from the first part of the installation process .py script that automates rez instalation

    execute_build_usd(str(USD_BUILD_EXEC), str(USD_BUILD_DIR))

    build_rez_third_party_package()
    build_rez_tracepath_packages()
    build_rez_tracepath_terminal()

finally:
    # Cleanup temp folder after install
    if USD_DOWNLOAD_FOLDER.exists():
        print(f"Cleaning up {USD_DOWNLOAD_FOLDER} ...")
        shutil.rmtree(USD_DOWNLOAD_FOLDER, ignore_errors=True)
