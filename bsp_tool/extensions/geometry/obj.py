import collections
from typing import List

from ...utils import geometry


class Obj:
    """Y+ forward; Z+ up"""
    models: List[geometry.Model]
    # TODO: named models

    def __init__(self, models=list()):
        self.models = models

    # TODO: @classmethod from_file(cls, filename) -> Obj:

    def save_as(self, filename: str):
        # TODO: assert filename is a valid path
        out = ["# generated by bsp_tool.extensions.geometry"]

        def indices(polygon: geometry.Polygon) -> List[int]:
            """rexx magic obj indexing; works for Blender, might break elsewhere"""
            # NOTE: inverts winding order; which is desired
            return range(-1, -(len(polygon.vertices) + 1), -1)

        for model_number, model in enumerate(self.models):
            out.append(f"o model_{model_number:03d}")
            polygons = collections.defaultdict(list)
            # ^ {Material: [Polygon]}
            for mesh in model.meshes:
                polygons[mesh.material].extend(mesh.polygons)
            for material in polygons:
                out.append(f"usemtl {material.name}")
                # TODO: generate .mtl files & include w/ "mtllib {material.name}.mtl"
                for polygon in polygons[material]:
                    vertices = [*map(model.apply_transforms, polygon.vertices)]
                    if all(len(v.uv) > 0 for v in vertices):
                        for v in vertices:
                            out.extend([
                                f"v {v.position.x} {v.position.y} {v.position.z}",
                                f"vn {v.normal.x} {v.normal.y} {v.normal.z}",
                                f"vt {v.uv[0].x} {v.uv[0].y}"])
                        out.append("f " + " ".join([f"{i}/{i}/{i}" for i in indices(polygon)]))
                    else:  # no uv
                        for v in vertices:
                            out.extend([
                                f"v {v.position.x} {v.position.y} {v.position.z}",
                                f"vn {v.normal.x} {v.normal.y} {v.normal.z}"])
                        out.append("f " + " ".join([f"{i}//{i}" for i in indices(polygon)]))
        with open(filename, "w") as obj_file:
            obj_file.write("\n".join(out))
