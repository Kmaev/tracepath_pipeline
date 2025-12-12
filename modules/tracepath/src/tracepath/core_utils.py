import json
import logging
import os
import re
from pathlib import Path

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")


# Generic functions to load environment and work with files in a project context

def get_env() -> dict:
    """
    Get environment variables used for a project repository and show path resolution.

    Return:
        dict: A dictionary containing:
            - "pr_projects_path": The root path to all projects, read from
              the PR_PROJECTS_PATH environment variable.
            - "pr_show": The current show identifier, read from the PR_SHOW
              environment variable.

    """
    env_data = {
        "pr_projects_path": os.getenv("PR_PROJECTS_PATH"),
        "pr_show": os.getenv("PR_SHOW")
    }
    return env_data


def get_path_structure_templ(template: str) -> str | list | None:
    """
    Retrieve a path structure template from the folder_structure.json file.

    This function loads the JSON file located alongside this module and
    returns the value associated with the specified template key. The value
    may be a string or a list, depending on how the template is defined.

    Args:
        template (str): The name of the template key to retrieve.

    Return:
        str | list | None:
            - The template value (string or list) if the key exists.
            - None if the key is not found.

    """
    json_path = Path(__file__).parent / "folder_structure.json"

    try:
        with open(json_path) as f:
            folder_structure = json.load(f)
        return folder_structure[template]
    except KeyError:
        logging.error(f"Template key '{template}' not found in {json_path.name}")
        return None


def find_file_in_context(base_path: str, version: int) -> str | None:
    """
    Find a version folder and a file inside a version folder.
    Shot manifest context is sources from the template, but the actual file is sources by listing folders.

    Args:
        base_path (str): A path to the folder with the versions
        version (int): A version to search

    Return:
        str | None:
            - The first matching file path if the specified version is found.
            - None if no file matching the version exists within the given path.

    """
    node_version = str(version).zfill(3)
    base = Path(base_path)
    results = []
    for subfolder in base.iterdir():
        if subfolder.is_dir() and node_version in subfolder.name:
            for file in subfolder.iterdir():

                if node_version in file.name:
                    results.append(file)
    return results[0] if results else None


def get_latest_version_number(context: str) -> int | None:
    """
    Get the highest version number from versioned subfolders in a given context.

    Args:
        context (str): A path to the folder that contains version

    Return:
        int: The latest version number

    """
    context_path = Path(context)
    if not context_path.exists():
        return None

    versioned_dirs = []
    for d in context_path.iterdir():
        match = re.search(r'\d+', d.name)
        if match:
            versioned_dirs.append(int(match.group()))
    if versioned_dirs:
        version = sorted(versioned_dirs, reverse=True)[0]
        return version
    else:
        return None


# Publishing

def get_show_data_folder() -> Path:
    """
    Helper function to get the data folder.

    Return:
        Path: A path to the folder that contains project data

    """
    env_vars = get_env()
    return Path(env_vars["pr_projects_path"]) / env_vars["pr_show"] / "show_data"


def get_published_data(data_folder: Path) -> dict:
    """
    Loads the published assets data from a JSON file.

    If the JSON file does not exist, it creates an empty one and returns an empty dictionary.

    Args:
        data_folder (Path): Path to the folder that contains the published data JSON file.

    Return:
        dict: loaded dictionary from the path.

    """
    data_folder.mkdir(parents=True, exist_ok=True)
    published_data_path = data_folder / "published_data.json"

    if not published_data_path.exists():
        published_data_path.write_text('{}')

    return json.loads(published_data_path.read_text())


def write_published_data(data_folder: Path, published_data: dict) -> None:
    """
    Writes the published assets data to a JSON file.

    Args:
        data_folder (Path): Path to the folder that contains the published data JSON file.
        published_data (dict): A dictionary containing the data to write.

    Return:
        None

    """
    published_data_path = data_folder / "published_data.json"
    published_data_path.write_text(json.dumps(published_data, indent=4))


# Save or open DCC scene files

def make_scene_path(dcc, ext, scene_name, ) -> str | None:
    """
    Create a scene file path based on the DCC application, file extension, and the scene file name.

    Args:
        dcc (str):
            Name of the current DCC application. Used to determine the appropriate
            folder where the scene file should be stored.
        ext: (str):
            File extension
        scene_name (str):
            The base name of the scene file.

    Return:
        str | None:
            - The resolved file path for a scene based on the 'scene_file' template
              and the given DCC.
            - None if the scene path could not be created (for example, if no scene
              name is provided).

    """

    if scene_name != "":
        check_required_env(["PR_PROJECTS_PATH", "PR_SHOW", "PR_ITEM", "PR_GROUP", "PR_TASK"])
        env_data = {
            "pr_projects_path": os.getenv("PR_PROJECTS_PATH"),
            "pr_show": os.getenv("PR_SHOW"),
            "pr_item": os.getenv("PR_ITEM"),
            "pr_group": os.getenv("PR_GROUP"),
            "pr_task": os.getenv("PR_TASK"),
            "dcc": dcc,
            "name": scene_name,
            "version": "001",
            "ext": ext,
        }
        templ = get_path_structure_templ("scene_file")
        if not templ:
            raise RuntimeError("Template 'scene_file' not found.")

        scene_path = os.path.normpath(templ.format(**env_data))
        scenes_folder = os.path.dirname(scene_path)
        if not os.path.isdir(scenes_folder) or not os.path.isfile(scene_path):
            return scene_path
        latest = (get_latest_version_number(scenes_folder) or 0) + 1
        env_data["version"] = "%03d" % latest
        return os.path.normpath(templ.format(**env_data))
    else:
        return None


def get_task_context() -> str:
    """
    Solve a task context path based on an environment variables.

    Return:
        str: A context path.

    """
    check_required_env(["PR_PROJECTS_PATH", "PR_SHOW", "PR_ITEM", "PR_GROUP", "PR_TASK"])
    context = os.path.join(os.environ.get("PR_PROJECTS_PATH"), os.environ.get("PR_SHOW"),
                           os.environ.get("PR_GROUP"),
                           os.environ.get("PR_ITEM"), os.getenv("PR_TASK"))
    context = os.path.normpath(context)
    return context


def check_required_env(keys):
    """
    Helper function to ensure that all required environment variables are set.

    """
    miss = [k for k in keys if not os.getenv(k)]
    if miss:
        raise RuntimeError("Missing environment variables: " + ", ".join(miss))
