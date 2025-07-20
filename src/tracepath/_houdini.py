import json
import os
import re
from importlib import reload
from pathlib import Path
from tracepath import _usd

reload(_usd)

import hou


# Load HDA
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
    """
    env_vars = get_env()
    node_vars = get_node_env_data(node)
    all_node_data = {**env_vars, **node_vars}

    templ_folder, _ = get_path_structure_templ(templ)
    context = templ_folder.format(**all_node_data)

    return context


def set_latest_version(node: hou.Node, context: str):
    """
    Set the node's version parameter to the latest version found in the context folder (Run on node creation).
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


def find_matching_files(base_path: str, version: int) -> str:
    """
    Find a version folder and a file inside a version folder that contains the version string in its name.
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


# Write HDA:

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

    # Resolving template
    templ = get_path_structure_templ(template)
    # Getting the first part of the output path string
    output_path = templ.format(**all_node_data)

    return output_path


def get_first_frame_cache(node: hou.Node)->float:
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
    Versions up the main shot manifest path.
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
    version_up= int(version) + (1 if hou.frame() == node.parm("f1").eval() else 0)

    new_version = str(version_up).zfill(len(version))

    new_folder_name = parent_folder.name.replace(version, new_version)
    new_folder = parent_folder.parent / new_folder_name

    new_file_name = file_name.replace(version, new_version)

    new_output_path = new_folder / new_file_name
    return str(new_output_path)
