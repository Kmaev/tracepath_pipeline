name = "project_index"
version = "1.0.0"
build_command = "python {root}/build.py {install}"

requires = ["pyside6"]

def commands():
    global env

    env.PYTHONPATH.append("{root}/python")

    env.STYLE_PROJECT_INDEX.set("{root}/resources")
    alias("trace_project", "python -m project_index.trace_project_index_ui")
