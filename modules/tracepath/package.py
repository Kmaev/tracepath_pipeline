name = "tracepath"
version = "2.0.0"
build_command = "python {root}/build.py {install}"


def commands():
    global env

    env.PYTHONPATH.append("{root}/python")
    env.STYLE_TRACEPATH.set("{root}/resources")