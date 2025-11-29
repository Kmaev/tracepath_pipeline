import logging

import hou
from pxr import Sdf

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", force=True)


def find_original_usd_filepath(node: hou.node) -> str | None:
    """
    Find the original USD file from which the current edit session began.

    Inspect the root layer of the LOP node's USD stage and
    check its composition dependencies to locate the first non-anonymous
    layer, the first non-anonymous layer is treated as the original source layer.

    Args:
        node: A LOP context node providing access to a USD stage.

    Returns:
        str | None: The resolved file path of the original USD layer if found,
            or ``None``.

    """
    stage = node.stage()
    layer = stage.GetRootLayer()
    layer_dependencies = layer.GetCompositionAssetDependencies()
    for layer in layer_dependencies:
        if not Sdf.Layer.IsAnonymousLayerIdentifier(layer):
            logging.info(f"USD edit session started from layer: {layer}")
            return layer
    return None
