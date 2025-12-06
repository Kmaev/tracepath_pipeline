import json
import os
import re
from pathlib import Path

import hou


# Generic functions for Load and Write USD HDAs in houdini
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


def get_node_env_data(node: hou.Node) -> dict:
    """
    Retrieve environment variables from HDA parameters.

    Args:
        node (hou.Node): Houdini TracePath Load USD Stage or USD Write HDA

    Return:
        dict: A dictionary containing:
        "pr_group", "pr_item", "pr_task" environment variables.

    """
    _require_env(["PR_GROUP", "PR_ITEM", "PR_TASK"])
    node_data = {
        "pr_group": node.parm("grp").eval(),
        "pr_item": node.parm("item").eval(),
        "pr_task": node.parm("task").eval()
    }
    return node_data


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
        hou.ui.displayMessage(
            f"Template key '{template}' not found in {json_path.name}",
            severity=hou.severityType.Error
        )
        return None


def get_manifest_context(node: hou.Node, templ) -> str:
    """
    Resolve the full context path for the USD shot manifest using template and environment values.
    This function is used in houdini HDA

    Args:
        node (hou.Node): A Houdini node from a TracePath Load USD Stage or USD Write HDA.
        templ (str): Template key used to look up a path structure definition.

    Return:
        str: The resolved path to the main shot manifest folder.

    """
    env_vars = get_env()
    node_vars = get_node_env_data(node)
    all_node_data = {**env_vars, **node_vars}

    templ_folder, _ = get_path_structure_templ(templ)
    context = templ_folder.format(**all_node_data)

    return context


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


# Load USD Stage HDA

def set_latest_version(node: hou.Node, context: str):
    """
    Set the node's version parameter to the latest version found in the context folder (Run from HDA on node creation).

    Args:
        node (hou.Node): A Houdini node TracePath Load USD Stage or USD Write HDA.

    Return:
        None

    """
    version = get_latest_version_number(str(context))

    if not version:
        version = 1
    node.parm("version").set(version)


def load_shot_manifest(node: hou.Node) -> str:
    """
    Load the path to the main shot manifest file based on the version selected in the HDA.
    Used in HDA parameter as a callback

     Args:
        node (hou.Node): A Houdini node TracePath Load USD Stage or USD Write HDA.

    Return:
        str: Path to the main shot manifest usd file.

    """
    context = get_manifest_context(node, "usd_shot_manifest_output")
    node_version = node.parm("version").evalAsString()
    file = find_file_in_context(str(context), node_version)

    if not file or not Path(file).exists():
        raise RuntimeError(f"No matching file found for version '{node_version}' in: {context}")
    return str(file)


# Write USD HDA:

def get_usd_output_path(node: hou.Node, template) -> str:
    """
    Solve the usd output file path using environment variables and the selected template.

    Args:
        node (hou.Node): A Houdini node TracePath Load USD Stage or USD Write HDA.
        template (str): The name of the template key to retrieve.

    Return:
        str: A path to the usd file to write to.

    """
    env_vars = get_env()
    node_vars = get_node_env_data(node)

    node_vars["name"] = node.parm("name").eval()
    node_vars["version"] = str(node.parm("version").eval()).zfill(3)
    node_vars["file_format"] = node.parm("format").evalAsString()
    node_vars["padding"] = ".$F4" if node.evalParm("trange") else ""
    all_node_data = {**env_vars, **node_vars}

    templ = get_path_structure_templ(template)
    if not templ:
        raise RuntimeError(f"Template '{template}' not found.")
    output_path = templ.format(**all_node_data)
    return output_path


def get_first_frame_cache(node: hou.Node) -> float:
    """
    Get the first frame cache for a given node.

    This function is used to evaluate if just a single file cache or if it is a sequence should be written to disk.

    Args:
        node (hou.Node): A Houdini node TracePath Load USD Stage or USD Write HDA.

    Return:
        float: A first frame of the cache

    """
    first_frame = node.parm("f1").eval()
    cache_parm = node.parm("lopoutput").evalAtFrame(first_frame)
    return cache_parm


def apply_autoversion(node: hou.Node):
    """
    This function called from HDA to version up the file

    Args:
        node (hou.Node): A Houdini node TracePath Load USD Stage or USD Write HDA.

    Return:
        None

    """
    version = 1
    if node.parm("autoversion").eval() == 1:
        context = Path(node.parm("lopoutput").evalAsString()).parent.parent
        if context.exists():
            latest_version = get_latest_version_number(str(context))
            if latest_version:
                version = latest_version + 1
    else:
        version = node.parm("version").eval()

    node.parm("version").set(version)


def version_up_shot_manifest(node: hou.Node) -> str:
    """
    Create a versioned up output path, using re extract the version number and increase the version.
    This function called from Write USD HDA

    node (hou.Node): A Houdini node TracePath Load USD Stage or USD Write HDA.

    Return:
        str: Versioned up a main shot manifest output path.

    """
    new_output_path = ""
    context = Path(get_manifest_context(node, "usd_shot_manifest_output"))
    if context.exists():
        latest_version = get_latest_version_number(str(context))
        if latest_version:
            output_path = find_file_in_context(str(context), latest_version)
            if output_path:
                path = Path(output_path)
                parent_folder = path.parent
                file_name = path.name

                match = re.search(r"v(\d+)", parent_folder.name)

                if match:
                    version = match.group(1)
                    version_up = int(version) + (
                        1 if hou.frame() == node.parm("f1").eval() or node.parm("trange").eval() == 0 else 0)

                    new_version = str(version_up).zfill(len(version))
                    new_folder_name = parent_folder.name.replace(version, new_version)
                    new_folder = parent_folder.parent / new_folder_name

                    new_file_name = file_name.replace(f"v{version}", f"v{new_version}")
                    new_output_path = new_folder / new_file_name

    if not new_output_path:
        node_vars = {}
        node_vars["version"] = "001"
        node_vars["file_format"] = node.parm("format").evalAsString()

        _, templ_file = get_path_structure_templ("usd_shot_manifest_output")
        new_file_path = Path(templ_file.format(**node_vars))
        new_output_path = context / new_file_path

    return str(new_output_path)


def find_stage_source_layer(node: hou.node) -> str:
    """
    Retrieve the identifier of the USD layer on which the current edit was performed.

    This is used inside the HDA to determine the source layer for building the
    main shot manifest composition.

    Args:
        node (hou.Node): A Houdini node in LOP context

    Return:
        USD stage identifier from which the current edit has started

    """
    return node.sourceLayer().identifier


# Publishing

def get_data_folder() -> Path:
    """
    Helper function to get the data folder.

    Return:
        Path: A path to the folder that contains project data

    """
    env_vars = get_env()
    return Path(env_vars["pr_projects_path"]) / env_vars["pr_show"] / "show_data"


def get_publish_key(node: hou.Node) -> str:
    """
    Helper function to get the publish key, publish key consist of group and name what in classic vfx pipeline would be
    sequence and shot.

    Args:
        node (hou.Node): A Houdini node TracePath USD Write HDA.
    Return:
        str: A key combined from pr_group and pr_item sued for publishing.

    """
    node_data = get_node_env_data(node)
    return f"{node_data['pr_group']}_{node_data['pr_item']}"


def write_publish_comment(node: hou.Node) -> None:
    """
    Writes a publish comment to the published data file.

    Args:
        node (hou.Node): A Houdini node TracePath USD Write HDA.
    Return:
        None

    """
    comment = node.parm("comment").eval()
    file = node.parm("shot_manifest_output").eval()

    data_folder = get_data_folder()
    key = get_publish_key(node)

    published_data = get_published_data(data_folder)
    published_data.setdefault(key, {})
    published_data[key][file] = comment

    write_published_data(data_folder, published_data)
    node.parm("comment").set("")
    hou.ui.displayMessage(f"Shot manifest: \n{file} \npublished successfully!", severity=hou.severityType.Message)


def get_published_data_path(data_folder: Path) -> Path:
    """
    Helper function to get the path to the json file with all the published data. (Published data is show-based)

    Args:
        data_folder (Path): Path to the folder where the JSON published a data file stored
    Return:
        Path: published data JSON file path

    """
    return data_folder / "published_data.json"


def get_published_data(data_file: Path) -> dict:
    """
    Loads the published assets data from a JSON file.

    If the JSON file does not exist, it creates an empty one and returns an empty dictionary.

    Args:
        data_file (Path): JSON file path.

    Return:
        dict: loaded dictionary from the path.

    """
    data_file.mkdir(parents=True, exist_ok=True)
    published_data_path = get_published_data_path(data_file)

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
    published_data_path = get_published_data_path(data_folder)
    published_data_path.write_text(json.dumps(published_data, indent=4))


def read_publish_comment(node: hou.Node) -> str | None:
    """
    Reads the published comment from the published data file. Called from HDA parameter

    Args:
        node (hou.Node): A Houdini node TracePath HDA.

    Return:
        str: A comment from the published main shot manifest usd file

    """
    file_path = node.parm("shot_manifest_read").evalAsString()
    data_folder = get_data_folder()
    key = get_publish_key(node)
    published_data = get_published_data(data_folder)

    file_to_comment = published_data.get(key, {})
    for f, comment in file_to_comment.items():
        if f == file_path:
            return comment

    return None


# =================================================================
# Save HIP file

def get_current_file_name():
    hip_name = hou.getenv("HIPNAME")
    hip_name = "_".join(hip_name.split("_")[:-1])
    return hip_name


def is_fresh_scene() -> bool:
    """
    Check if the current Houdini session is a new scene
    (not yet saved to disk) or an existing saved scene.

    Return:
        bool: True if the houdini session is a new scene False if it is a previously saved hip file.

    """
    path = hou.hipFile.name()
    path = os.path.exists(path)
    if path:
        return False
    return True


def hip_ext_from_session() -> str:
    """
    Check the license category of the current houdini session.
    Map the license category to the corresponding expedition of the hip file.

    Return:
        str: the .hip* extension for the current Houdini session.

    """
    if not hasattr(hou, "licenseCategory"):
        raise RuntimeError(
            "No valid Houdini license detected"
        )

    mapping = {
        hou.licenseCategoryType.Commercial: ".hip",
        hou.licenseCategoryType.Indie: ".hiplc",
        hou.licenseCategoryType.Apprentice: ".hipnc",
        hou.licenseCategoryType.Education: ".hipnc"
    }

    cat = hou.licenseCategory()
    try:
        return mapping[cat]
    except KeyError:
        raise RuntimeError(f"Unsupported/unknown license category: {cat!r}")


def make_scene_path(dcc, scene_name) -> str | None:
    """
    Create a scene file path based on the DCC application and the scene file name.

    Args:
        dcc (str):
            Name of the current DCC application. Used to determine the appropriate
            folder where the scene file should be stored.
        scene_name (str):
            The base name of the scene file.

    Return:
        str | None:
            - The resolved file path for a scene based on the 'scene_file' template
              and the given DCC.
            - None if the scene path could not be created (for example, if no scene
              name is provided).

    """
    ext = hip_ext_from_session()
    if scene_name != "":
        _require_env(["PR_PROJECTS_PATH", "PR_SHOW", "PR_ITEM", "PR_GROUP", "PR_TASK"])
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


def save_scene(scene_path):
    """
    Saves the scene to the given path.

    """
    if not os.path.isdir(os.path.dirname(scene_path)):
        os.makedirs(os.path.dirname(scene_path))
    hou.hipFile.save(scene_path)


# ==================================================================
# Open HIP file

def get_task_context() -> str:
    """
    Solve a task context path based on an environment variables.

    Return:
        str: A context path.

    """
    _require_env(["PR_PROJECTS_PATH", "PR_SHOW", "PR_ITEM", "PR_GROUP", "PR_TASK"])
    context = os.path.join(os.environ.get("PR_PROJECTS_PATH"), os.environ.get("PR_SHOW"),
                           os.environ.get("PR_GROUP"),
                           os.environ.get("PR_ITEM"), os.getenv("PR_TASK"))
    context = os.path.normpath(context)
    return context


def _require_env(keys):
    """
    Helper function to ensure that all required environment variables are set.

    """
    miss = [k for k in keys if not os.getenv(k)]
    if miss:
        raise RuntimeError("Missing environment variables: " + ", ".join(miss))
