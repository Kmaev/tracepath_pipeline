import json
import os
import re
from importlib import reload
from pathlib import Path

from tracepath import _usd

reload(_usd)

import hou


# Generic functions for Load and Write USD HDAs in houdini
def get_env() -> dict:
    """
    Gets environment variables for path resolution.
    """
    env_data = {
        "pr_root": os.getenv("PR_ROOT"),
        "pr_show": os.getenv("PR_SHOW")
    }
    return env_data


def get_node_env_data(node: hou.Node) -> dict:
    """
    Retrieve environment variables from HDA parameters.
    """
    node_data = {
        "pr_group": node.parm("grp").evalAsString(),
        "pr_item": node.parm("item").evalAsString(),
        "pr_task": node.parm("task").evalAsString()
    }
    return node_data


def get_path_structure_templ(template: str) -> str | None:
    """
    Load a path template from the folder_structure.json file.
    """
    json_path = Path(__file__).parent / "folder_structure.json"
    with open(json_path) as f:
        folder_structure = json.load(f)
    templ = folder_structure[template]
    return templ


def get_manifest_context(node: hou.Node, templ) -> str:
    """
    Resolve the full context path for the USD shot manifest using template and environment values.
    This function is also used in houdini HDA
    """
    env_vars = get_env()
    node_vars = get_node_env_data(node)
    all_node_data = {**env_vars, **node_vars}

    templ_folder, _ = get_path_structure_templ(templ)
    context = templ_folder.format(**all_node_data)

    return context


def find_matching_files(base_path: str, version: int) -> str:
    """
    Find a version folder and a file inside a version folder that contains the version string in its name.
    Shot manifest context is sources from the template, but the actual file is sources by listing folders.
    """
    node_version = str(version).zfill(3)
    base = Path(base_path)
    results = []
    for subfolder in base.iterdir():
        if subfolder.is_dir() and node_version in subfolder.name:
            for file in subfolder.iterdir():

                if node_version in file.name:
                    results.append(file)
    if not results[0]:
        raise IndexError(f"No matching file found for version '{node_version}' in: {base_path}")
    return results[0]


def get_latest_version_number(context: str) -> int | None:
    """
    Gets the highest version number from versioned subfolders in a given context.
    """
    context_path = Path(context)
    if context_path.exists():
        versioned_dirs = []
        for d in context_path.iterdir():
            match = re.search(r'\d+', d.name)
            if match:
                versioned_dirs.append(int(match.group()))
        version = sorted(versioned_dirs, reverse=True)[0]
        return version
    return None


# Load USD Stage HDA

def set_latest_version(node: hou.Node, context: str):
    """
    Set the node's version parameter to the latest version found in the context folder (Run from HDA on node creation).
    """
    version = get_latest_version_number(str(context))
    node.parm("version").set(version)


def load_shot_manifest(node: hou.Node) -> str:
    """
    Load the path to the main shot manifest file based on the version selected in the HDA.
    Used in HDA parameter
    """
    context = get_manifest_context(node, "usd_shot_manifest_output")
    node_version = node.parm("version").evalAsString()
    file = find_matching_files(str(context), node_version)

    if not file or not Path(file).exists():
        raise RuntimeError(f"No matching file found for version '{node_version}' in: {context}")
    return str(file)


# Write USD HDA:

def get_usd_output_path(node: hou.Node, template) -> str:
    """
    Solves the usd output file path using environment variables and the selected template.
    """
    env_vars = get_env()
    node_vars = get_node_env_data(node)

    node_vars["name"] = node.parm("name").eval()
    node_vars["version"] = str(node.parm("version").eval()).zfill(3)
    node_vars["file_format"] = node.parm("format").evalAsString()
    node_vars["padding"] = ".$F4" if node.evalParm("trange") else ""
    all_node_data = {**env_vars, **node_vars}

    templ = get_path_structure_templ(template)
    output_path = templ.format(**all_node_data)
    return output_path


def get_first_frame_cache(node: hou.Node) -> float:
    """
    Gets first frame cache for a given node.
    """
    first_frame = node.parm("f1").eval()
    cache_parm = node.parm("lopoutput").evalAtFrame(first_frame)
    return cache_parm


def apply_autoversion(node: hou.Node):
    """
    This function called from HDA to version up the file
    """
    if node.parm("autoversion").eval() == 1:
        context = Path(node.parm("lopoutput").evalAsString()).parent.parent
        latest_version = get_latest_version_number(str(context))
        if not latest_version:
            latest_version = 1
        later_version = str(latest_version + 1).zfill(3)
        node.parm("version").set(later_version)


def version_up_main_shot_manifest(node: hou.Node) -> str | None:
    """
    Versions up main shot manifest path. Creates an output path, using re extracts the version number.
    """
    context = get_manifest_context(node, "usd_shot_manifest_output")
    latest_version = get_latest_version_number(str(context))

    output_path = find_matching_files(str(context), latest_version)
    path = Path(output_path)
    parent_folder = path.parent
    file_name = path.name

    match = re.search(r"(\d+)$", parent_folder.name)

    if not match:
        return None

    version = match.group(1)
    version_up = int(version) + (1 if hou.frame() == node.parm("f1").eval() or node.parm("trange").eval() == 0 else 0)

    new_version = str(version_up).zfill(len(version))
    new_folder_name = parent_folder.name.replace(version, new_version)
    new_folder = parent_folder.parent / new_folder_name
    new_file_name = file_name.replace(version, new_version)

    new_output_path = new_folder / new_file_name
    return str(new_output_path)


# Publishing

def get_data_folder() -> Path:
    """
    Helper function to get the data folder.
    """
    env_vars = get_env()
    return Path(env_vars["pr_root"]) / env_vars["pr_show"] / "show_data"


def get_publish_key(node: hou.Node) -> str:
    """
    Helper function to get the publish key, publish key consist of group and item what in classic vfx pipeline would be
    sequence and shot.
    """
    node_data = get_node_env_data(node)
    return f"{node_data['pr_group']}_{node_data['pr_item']}"


def write_publish_comment(node: hou.Node) -> None:
    """
    Writes a publish comment to the published data file.
    """
    comment = node.parm("comment").eval()
    file = node.parm("lopoutput2").evalAsString()

    data_folder = get_data_folder()
    key = get_publish_key(node)

    published_data = get_published_data(data_folder)
    published_data.setdefault(key, {})
    published_data[key][file] = comment

    write_published_data(data_folder, published_data)


def get_published_data_path(data_folder: Path) -> Path:
    """
    Helper function to get the path to the json file with all the published data. (Published data is show-based)
    """
    return data_folder / "published_data.json"


def get_published_data(data_folder: Path) -> dict:
    """
    Loads the published assets data from a JSON file.

    If the JSON file does not exist, it creates an empty one and returns an empty dictionary.
    """
    data_folder.mkdir(parents=True, exist_ok=True)
    published_data_path = get_published_data_path(data_folder)

    if not published_data_path.exists():
        published_data_path.write_text('{}')

    return json.loads(published_data_path.read_text())


def write_published_data(data_folder: Path, published_data: dict) -> None:
    """
    Writes the published assets data to a JSON file.
    """
    published_data_path = get_published_data_path(data_folder)
    published_data_path.write_text(json.dumps(published_data, indent=4))


def read_publish_comment(node: hou.Node) -> str:
    """
    Reads the published comment from the published data file. Called from HDA parameter
    """
    file_path = node.parm("shot_manifest_read").evalAsString()
    data_folder = get_data_folder()
    key = get_publish_key(node)
    published_data = get_published_data(data_folder)

    file_to_comment = published_data.get(key, {})
    print(f"File to comment: {file_to_comment}")
    for f, comment in file_to_comment.items():
        print(f, comment)
        if f == file_path:
            return comment

    return "Version doesn't exist."
