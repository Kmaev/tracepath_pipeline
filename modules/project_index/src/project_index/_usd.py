import json
from collections import defaultdict
from typing import Any

from pxr import Usd, UsdGeom, Sdf, Ar


# USD Scene Initialization From Template
def configure_xform(prim: Usd.Prim, kind: str | None = None):
    xform = UsdGeom.Xform(prim)
    if kind:
        model_api = Usd.ModelAPI(xform)
        model_api.SetKind(kind)
        model_api.SetAssetName(prim.GetName())

    return xform


def create_prim(stage: Usd.Stage, parent_path: str, prim: dict[str, Any]):
    path = f"{parent_path}/{prim['name']}"
    prim_type = prim["type"]
    prim_kind = prim.get("kind")

    usd_prim = stage.DefinePrim(path, prim_type)

    if usd_prim.IsA(UsdGeom.Xform):
        configure_xform(usd_prim, prim_kind)

    for child in prim.get("children", []):
        create_prim(stage, path, child)


def create_scene_from_json(template_path: str, stage_output_path: str):
    with open(template_path, "r") as f:
        root_prim = json.load(f)

    stage = Usd.Stage.CreateNew(stage_output_path)
    create_prim(stage, "", root_prim)
    stage.GetRootLayer().Save()


# TraceReset Helper Function to preview USD stage layer composition
def walk_layer_stack(layer, visited=None, tree=None):
    if visited is None:
        visited = set()

    if tree is None:
        tree = defaultdict(list)

    if isinstance(layer, str):
        layer_id = layer
        layer = Sdf.Layer.FindOrOpen(layer_id)
    else:
        layer_id = layer.identifier

    if layer_id in visited:
        return tree

    visited.add(layer_id)

    resolver = Ar.GetResolver()
    ctx = resolver.CreateDefaultContextForAsset(layer.resolvedPath)

    with Ar.ResolverContextBinder(ctx):
        for sublayer_path in layer.subLayerPaths:
            identifier = resolver.CreateIdentifier(
                sublayer_path,
                layer.resolvedPath
            )
            resolved = resolver.Resolve(identifier)

            if not resolved:
                continue

            sublayer = Sdf.Layer.FindOrOpen(resolved)
            if not sublayer:
                continue

            tree[layer_id].append(sublayer.identifier)

            walk_layer_stack(sublayer, visited, tree)
    return tree
