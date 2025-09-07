name = "usd"
version = "0.1.0"
build_command = "python {root}/build.py {install}"


def commands():
    import os
    global env
    from pathlib import Path

    usd_root = "{root}/OpenUSD"
    env.PYTHONPATH.append(usd_root)
    env.PATH.prepend(os.path.join(usd_root, "bin"))
    env.PYTHONPATH.prepend(os.path.join(usd_root, "lib", "python"))
    env.PYTHONPATH.prepend(os.path.join(usd_root, "lib", "python", "site-packages"))
