import logging
import sys

import trimesh
import numpy as np

logging.getLogger("trimesh").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def trimesh_load_clean(mesh_path):
    from trimesh import constants
    m = trimesh.load(
            mesh_path,
            process=True,
            validate=True
            )
    m.remove_degenerate_faces(constants.tol.merge)
    return m

def union(mesh_path):
    my_mesh = trimesh_load_clean(mesh_path)
    meshes = my_mesh.split(only_watertight=False)

    number_of_meshes = len(meshes)

    if number_of_meshes <= 1:
        raise ValueError("number_of_meshes is {}, No need for union".format(number_of_meshes))

    if not all([i.is_watertight for i in meshes]):
        raise ValueError("dont do union since not all parts are watertight".format(number_of_meshes))

    logger.debug("start doing union, all watertight")

    union_mesh = meshes[0]
    count = 0

    never_intersect = True

    for i in range(1, len(meshes)):
        before_num_faces = len(union_mesh.faces)
        num_to_union_mesh_faces = len(meshes[i].faces)

        union_mesh = union_mesh.union(meshes[i], engine="blender")

        after_num_faces = len(union_mesh.faces)


        logger.debug("before num faces {}".format(before_num_faces))
        logger.debug("after num faces {}".format(after_num_faces))

        assert after_num_faces > before_num_faces, \
            "after faces number {} must be bigger than before faces number {}".format(after_num_faces, before_num_faces)

        if (after_num_faces - before_num_faces) != num_to_union_mesh_faces:
            never_intersect = False

    logger.debug("never_intersect {}".format(never_intersect))

    return my_mesh, union_mesh

def check_union_mesh(my_mesh, union_mesh):

    number_of_meshes = len(my_mesh.split())
    union_mesh_length = len(union_mesh.split())

    is_same_bounding_box = np.all(
        my_mesh.bounding_box.triangles == union_mesh.bounding_box.triangles)

    if not is_same_bounding_box:
        return False
        # raise ValueError("bounding_box is different to before")

    if union_mesh_length == 1:
        logger.debug(
            "!Successful union! same bbox {} result length {} original length {} is_watertight {}".format(
            is_same_bounding_box,
            union_mesh_length,
            number_of_meshes,
            union_mesh.is_watertight
            )
        )
    else:
        logger.debug(
            "!Successful union! same bbox {} result length {} original length {} is_watertight {}".format(
            is_same_bounding_box,
            union_mesh_length,
            number_of_meshes,
            union_mesh.is_watertight
            )
        )

    return True

def union_and_check(mesh_path, export_path):
    my_mesh, union_mesh = union(mesh_path)
    check_union_mesh(my_mesh, union_mesh)
    union_mesh.export(export_path)


if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        logger.debug("path to file not provided")
        logger.debug("use default file")
        mesh_path = "../unittest/meshes/twoCubes.stl"
    else:
        mesh_path = sys.argv[1]

    if len(sys.argv) < 3:
        logger.debug("path to export not provided")
        logger.debug("use default export path")
        export_path = "unioned.stl"
    else:
        export_path = sys.argv[2]

    union_and_check(mesh_path, export_path)


