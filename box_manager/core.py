from maya import cmds

def get_selection():
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        return None

    root = selection[0]
    return root

def get_scene_nodes(root_node):
    scene_nodes = cmds.listRelatives(
        root_node,
        allDescendents=True,
        fullPath=True,
        type="transform"
    )
    scene_nodes.insert(0, root_node)
    cmds.select(root_node, deselect=True)

    return scene_nodes


def get_node_parent(node):
    return cmds.listRelatives(node, parent=True)


def bboxes_exist_in_scene():
    bboxes = cmds.ls("*_BBOX")
    if bboxes:
        return True

    return False


def change_bbox_visibility(node_name, hide_object=False):
    bbox_node = cmds.ls("{0}_BBOX".format(node_name))

    if hide_object:
        cmds.hide(bbox_node)
    elif not hide_object:
        cmds.showHidden(bbox_node)


def create_node_bouding_box(node, bbox_name):
    """Create bounding box based on object position and scale."""
    x1, y1, z1, x2, y2, z2 = cmds.exactWorldBoundingBox(node)
    cube = cmds.polyCube()[0]

    # Get the centre point for each axis
    centre_points = [
        (x2 + x1) / 2.0,
        (y2 + y1) / 2.0,
        (z2 + z1) / 2.0
    ]

    # Scale up the cube to fit.
    bbox_scale = [
        x2 - x1,
        y2 - y1,
        z2 - z1
    ]

    cmds.move(centre_points[0], centre_points[1], centre_points[2], cube)
    cmds.scale(bbox_scale[0], bbox_scale[1], bbox_scale[2], cube)

    cube = cmds.ls(cube, long=True)
    bbox = cmds.rename(cube, bbox_name)

    return bbox


def setup_bbox(node, bbox_layer):
    bbox_name = "{0}_BBOX".format(node.split("|")[-1])
    bbox = create_node_bouding_box(node, bbox_name)
    cmds.editDisplayLayerMembers(bbox_layer, bbox)

    return bbox

def add_bbox_parent(node, bbox):
    """Gets the parent node of the given node, finds the corresponding
    BBOX node to it and adds that to the current BBOX node.
    """
    node_parent = cmds.listRelatives(node, parent=True)
    if not node_parent:
        return
    node_parent_name = node_parent[0]
    bbox_parent = cmds.ls("{0}_BBOX".format(node_parent_name))

    cmds.parent(bbox, bbox_parent, absolute=True)


def setup_bbox_hierarchy(scene_nodes):
    bbox_layer = cmds.ls("bbox_layer", type="displayLayer")
    if not bbox_layer:
        bbox_layer = [cmds.createDisplayLayer(name="bbox_layer")]

    for node in sorted(scene_nodes, key=len):
        bbox = setup_bbox(node, bbox_layer)
        add_bbox_parent(node, bbox)

    # Set levelOfDetail attr to "Bounding Box".
    cmds.setAttr("{0}.levelOfDetail".format(bbox_layer[0]), 1)

