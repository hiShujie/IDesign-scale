import bpy
import json
import math
import os

# get paths from environment variables
scene_number = os.getenv('SCENE_NUMBER')
scene_graph_path = os.getenv('SCENE_GRAPH')
asset_dir = os.getenv('ASSET_DIR')
output_dir = os.getenv('OUTPUT_DIR')

if not all([scene_number, scene_graph_path, asset_dir, output_dir]):
    raise ValueError("Required environment variables are not set")

print(f"Processing scene {scene_number}")
print(f"Scene graph: {scene_graph_path}")
print(f"Asset directory: {asset_dir}")
print(f"Output directory: {output_dir}")

object_name = 'Cube'
object_to_delete = bpy.data.objects.get(object_name)

# Check if the object exists before trying to delete it
if object_to_delete is not None:
    bpy.data.objects.remove(object_to_delete, do_unlink=True)

def import_glb(file_path, object_name):
    bpy.ops.import_scene.gltf(filepath=file_path)
    imported_object = bpy.context.view_layer.objects.active
    if imported_object is not None:
        imported_object.name = object_name

def create_room(width, depth, height):
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))

    # Extrude to create walls
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height)})
    bpy.ops.object.mode_set(mode='OBJECT')

    # Scale the walls to the desired dimensions
    bpy.ops.transform.resize(value=(width, depth, 1))

    bpy.context.active_object.location.x += width / 2
    bpy.context.active_object.location.y += depth / 2

def find_glb_files(directory):
    glb_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".glb"):
                key = file.split(".")[0]
                if key not in glb_files:
                    glb_files[key] = os.path.join(root, file)
    return glb_files

def get_highest_parent_objects():
    highest_parent_objects = []

    for obj in bpy.data.objects:
        # Check if the object has no parent
        if obj.parent is None:
            highest_parent_objects.append(obj)
    return highest_parent_objects

def delete_empty_objects():
    # Iterate through all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object is empty (has no geometry)
        print(obj.name, obj.type)
        if obj.type == 'EMPTY':
            bpy.context.view_layer.objects.active = obj
            bpy.data.objects.remove(obj)

def select_meshes_under_empty(empty_object_name):
    # Get the empty object
    empty_object = bpy.data.objects.get(empty_object_name)
    print(empty_object is not None)
    if empty_object is not None and empty_object.type == 'EMPTY':
        # Iterate through the children of the empty object
        for child in empty_object.children:
            # Check if the child is a mesh
            if child.type == 'MESH':
                # Select the mesh
                child.select_set(True)
                bpy.context.view_layer.objects.active = child
            else:
                select_meshes_under_empty(child.name)

def rescale_object(obj, scale):
    # Ensure the object has a mesh data
    if obj.type == 'MESH':
        bbox_dimensions = obj.dimensions
        scale_factors = (
                         scale["length"] / bbox_dimensions.x, 
                         scale["width"] / bbox_dimensions.y, 
                         scale["height"] / bbox_dimensions.z
                        )
        obj.scale = scale_factors

# 读取场景图
objects_in_room = {}
with open(scene_graph_path, 'r') as file:
    data = json.load(file)
    for item in data:
        # 过滤掉墙壁、天花板等结构性元素
        if item["new_object_id"] not in ["south_wall", "north_wall", "east_wall", 
                                       "west_wall", "middle of the room", "ceiling", "floor", "wall"]:
            objects_in_room[item["new_object_id"]] = item

print(f"Found {len(objects_in_room)} objects to place in the scene")
for obj_id in objects_in_room:
    print(f"- {obj_id}")

directory_path = asset_dir
glb_file_paths = find_glb_files(directory_path)

for item_id, object_in_room in objects_in_room.items():
    glb_file_path = os.path.join(directory_path, glb_file_paths[item_id])
    print("glb_file_path: ", glb_file_path)
    import_glb(glb_file_path, item_id)

parents = get_highest_parent_objects()
empty_parents = [parent for parent in parents if parent.type == "EMPTY"]
print(empty_parents)

for empty_parent in empty_parents:
    bpy.ops.object.select_all(action='DESELECT')
    select_meshes_under_empty(empty_parent.name)
    
    bpy.ops.object.join()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    joined_object = bpy.context.view_layer.objects.active
    if joined_object is not None:
        joined_object.name = empty_parent.name + "-joined"

bpy.context.view_layer.objects.active = None

MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
for OBJS in MSH_OBJS:
    bpy.context.view_layer.objects.active = OBJS
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    OBJS.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active = OBJS
    OBJS.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
print("MSH_OBJS: ", MSH_OBJS)
for OBJS in MSH_OBJS:
    # 获取对象ID，保留原始名称中的连字符
    object_id = OBJS.name
    if object_id.endswith("-joined"):
        object_id = object_id[:-7]  # 只去掉-joined后缀
    
    if object_id not in objects_in_room:
        print(f"Warning: Object '{object_id}' not found in scene graph, skipping...")
        continue
        
    item = objects_in_room[object_id]
    if "position" not in item or "rotation" not in item:
        print(f"Warning: Object '{object_id}' missing position or rotation data, skipping...")
        continue
        
    object_position = (item["position"]["x"], item["position"]["y"], item["position"]["z"])  # X, Y, and Z coordinates
    object_rotation_z = (item["rotation"]["z_angle"] / 180.0) * math.pi + math.pi # Rotation angles in radians around the X, Y, and Z axes
    
    bpy.ops.object.select_all(action='DESELECT')
    OBJS.select_set(True)
    OBJS.location = object_position
    bpy.ops.transform.rotate(value=object_rotation_z,  orient_axis='Z')
    rescale_object(OBJS, item["size_in_meters"])

bpy.ops.object.select_all(action='DESELECT')
delete_empty_objects()

# TODO: Generate the room with the room dimensions
create_room(4.0, 4.0, 2.5)

# 保存.blend文件
blend_file = os.path.join(output_dir, f"scene_{scene_number}.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

# 导出.glb文件
glb_file = os.path.join(output_dir, f"scene_{scene_number}.glb")
bpy.ops.export_scene.gltf(filepath=glb_file)