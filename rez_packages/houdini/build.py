import glob
import os
import platform
import re
import stat
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PKG_NAME = "houdini"
LOCALROOT = os.environ.get("REZ_LOCAL_PACKAGES_PATH", os.path.expanduser("~/rez-packages"))

def build(source_path, build_path, install_path, targets):
    install_path = Path(install_path)
    source_path = Path(source_path)
    for ver, root, sysname in find_installs():
        logging.info(f"[rez:{PKG_NAME}] Installing wrapper for Houdini {ver} at {root} ({sysname})")
        install_one(ver, root, sysname)

def _extract_version_from_path(path):
    m = re.search(r"(\d+\.\d+\.\d+)", os.path.realpath(path))
    return m.group(1) if m else "0.0.0"

def find_installs():
    sysname = platform.system()
    results = []
    if sysname == "Darwin":
        # /Applications/Houdini/Houdini XX.YY.ZZ contains app bundles per edition
        for root in glob.glob("/Applications/Houdini/Houdini*"):
            v = _extract_version_from_path(root)
            results.append((v, root, sysname))
    elif sysname == "Linux":
        # Typical: /opt/hfs20.5.403 and/or symlink /opt/hfs -> /opt/hfs20.5.403
        for p in glob.glob("/opt/hfs*"):
            v = _extract_version_from_path(p)
            results.append((v, os.path.realpath(p), sysname))
    return results

def find_macos_app(root, ver):
    for n in (
        f"Houdini Indie {ver}.app",
        f"Houdini FX {ver}.app",
        f"Houdini {ver}.app",
        f"Houdini Apprentice {ver}.app",
    ):
        p = os.path.join(root, n)
        if os.path.isdir(p):
            return p
    # fallback to any .app inside the version folder
    apps = glob.glob(os.path.join(root, "*.app"))
    return apps[0] if apps else None

def make_exe(p):
    os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

PKG = '''name = "{name}"
version = "{ver}"

def commands():
    env.HOUDINI_VERSION = "{ver}"
    env.PATH.prepend("{{this.root}}/bin")
'''

WRAP_MAC = '#!/bin/bash\nopen -a "{app}" --args "$@"\n'
WRAP_LINUX = '#!/bin/bash\n"{bin}" "$@"\n'

def install_one(ver, root, sysname):
    pkg_dir = os.path.join(LOCALROOT, PKG_NAME, ver)
    bin_dir = os.path.join(pkg_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    with open(os.path.join(pkg_dir, "package.py"), "w") as f:
        f.write(PKG.format(name=PKG_NAME, ver=ver))

    wrapper = os.path.join(bin_dir, "houdini")
    if sysname == "Darwin":
        app = find_macos_app(root, ver)
        with open(wrapper, "w") as f:
            f.write(WRAP_MAC.format(app=app))
    else:
        houdini_bin = os.path.join(root, "bin", "houdini")
        with open(wrapper, "w") as f:
            f.write(WRAP_LINUX.format(bin=houdini_bin))
    make_exe(wrapper)

if __name__ == '__main__':
    build(
        source_path=os.environ['REZ_BUILD_SOURCE_PATH'],
        build_path=os.environ['REZ_BUILD_PATH'],
        install_path=os.environ['REZ_BUILD_INSTALL_PATH'],
        targets=sys.argv[1:]
    )
