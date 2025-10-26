import re
from collections import defaultdict

from pxr import UsdUtils, Usd


def fetch_usd_layers(usd_file: str) -> list:
    """
    Fetch all USD dependency layers referenced by the given USD file.
    """
    stage = Usd.Stage.Open(usd_file)
    usd_layer = stage.GetRootLayer()
    layers, _, _ = UsdUtils.ComputeAllDependencies(usd_layer.identifier)
    return layers if layers else []


def group_collections(usd_layers: list) -> list:
    """
    Group USD layers into collections of multi-frame sequences.

    Files that share the same base name but have a different frame number
    are grouped together into lists. Single files — either non-framed or
    single-frame caches — remain as individual items.
    """
    final_list = []

    buckets = defaultdict(list)
    singles = []

    for layer in usd_layers:
        name = getattr(layer, "identifier", str(layer))
        if re.search(r"\.\d+\.(usda|usdc)$", name, re.IGNORECASE):
            # base = everything before digits and extension.
            # First a file filtered based on digits in a path and then grouped based on the name"
            base = re.sub(r"\.\d+\.(usda|usdc)$", "", name, flags=re.IGNORECASE)
            buckets[base].append(layer)
        else:
            singles.append(layer)
    # Groups sorting, final list creation:
    for base, items in buckets.items():
        # Buckets with 2 or more files (true multi-frame sequences):
        if len(items) >= 2:
            final_list.append(items)
            # Buckets with only one file that was cached with a frame number (a single frame, not a true sequence)
            # Still included in the sequence filter in the previous step because of the frame number
        else:
            final_list.extend(items)

        # Add regular single USD files
    final_list.extend(singles)
    return final_list


def create_preview_list(grouped_usd_files: list) -> list:
    """
    Creates a single string path from multi-frame USD sequences,
    where the numeric frame value is represented by '####'
    """
    display_items_list = []
    for i in grouped_usd_files:
        if isinstance(i, list):
            usd_path = getattr(i[0], "identifier", str(i[0]))
            new_path = re.sub(r"\.\d{4}\.(usda|usdc)$", r".####.\1", usd_path)
            display_items_list.append(new_path)
        else:
            usd_path = getattr(i, "identifier", str(i))
            display_items_list.append(usd_path)

    return display_items_list


def get_usd_file_dependencies_preview(usd_file: str) -> list:
    """
    Executes the full USD dependency processing logic and returns a clean,
    formatted list of file paths.
    This function combines fetching all USD dependencies, grouping multi-frame
    sequences, and formatting the output paths for preview display.
    """
    layers = fetch_usd_layers(usd_file)
    grouped_list = group_collections(layers)
    prev_list = create_preview_list(grouped_list)
    return prev_list
