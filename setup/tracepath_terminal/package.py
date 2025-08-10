name = "tracepath_terminal"
version = "1.0.0"
build_command = "python {root}/build.py {install}"

requires = ["tracepath", "houdini", "project_index"]

def commands():
    import os
    global env

    env.PR_SHOW_ROOT = os.environ.get("PR_SHOW_ROOT", "")
    env.TRACEPATH_SHELL_ROOT.set("{root}/shell")
    source("{root}/shell/show_nav.sh")
