import os
import hou


def _warn(msg):
    try:
        hou.ui.displayMessage(msg)
    except Exception:
        pass
    print("[TRACEPATH][WARN]", msg)


def add_env():
    env_vars = ["PR_PROJECTS_PATH", "PR_SHOW", "PR_GROUP", "PR_ITEM", "PR_TASK"]

    try:
        env = {var: os.getenv(var) for var in env_vars}
        missing = [var for var, val in env.items() if not val]
        if missing:
            _warn(f"Missing environment variables: {', '.join(missing)}.\n"
                  "Launching Houdini with default environment.")
        context = os.path.join(env["PR_PROJECTS_PATH"], env["PR_SHOW"],
                               env["PR_GROUP"], env["PR_ITEM"], env["PR_TASK"])

        scenes = os.path.join(context, "houdini/scenes")
        hip_file = os.path.join(scenes, "untitled.hip")

        hou.putenv("JOB", scenes)
        hou.putenv("HIP", scenes)
        hou.putenv("HIPFILE", hip_file)

    except Exception as e:
        _warn(
            f"Tracepath could not set Houdini environment because of the following error:\n{e!r}")


add_env()
