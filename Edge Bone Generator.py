bl_info = {
    "name": "Edge Recessed Bone Generator",
    "author": "Leon/LONDURGERUS",
    "version": (1, 4),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Rig Edge Tab",
    "description": "Generates recessed bones along selected mesh edges oriented to vertex normals.",
    "category": "Rigging",
}

import bpy
import bmesh
import mathutils

# --- Add-on Preferences (Saves your default numbers permanently) ---
class EDGEBONE_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    default_bone_length: bpy.props.FloatProperty(
        name="Default Bone Length", default=0.003, precision=4, min=0.0001
    )
    default_bbone_scale: bpy.props.FloatProperty(
        name="Default BBone Scale", default=0.000979, precision=6, min=0.00001
    )
    default_inside_offset: bpy.props.FloatProperty(
        name="Default Inside Offset", default=0.0005, precision=4
    )
    default_segments: bpy.props.IntProperty(
        name="Default B-Bone Segments", default=1, min=1, max=32
    )
    default_prefix: bpy.props.StringProperty(
        name="Bone Name Prefix", default="E_Bone"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set your default startup numbers here:")
        layout.prop(self, "default_bone_length")
        layout.prop(self, "default_bbone_scale")
        layout.prop(self, "default_inside_offset")
        layout.prop(self, "default_segments")
        layout.prop(self, "default_prefix")


# --- Operator ---
class RIG_OT_create_edge_bones(bpy.types.Operator):
    """Generate recessed bones along selected edges"""
    bl_idname = "rig.create_edge_bones"
    bl_label = "Create Edge Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        prefs = context.preferences.addons[__name__].preferences

        # Pull settings from N-panel (falls back to scene or preferences)
        bone_length = scene.edge_bone_length
        bbone_scale = scene.edge_bbone_scale
        inside_offset = scene.edge_inside_offset
        segments = scene.edge_segments
        armature_name = scene.edge_armature_name
        prefix = prefs.default_prefix

        mesh_obj = context.active_object
        if not mesh_obj or mesh_obj.type != 'MESH' or mesh_obj.mode != 'EDIT':
            self.report({'ERROR'}, "Please select a mesh and enter Edit Mode.")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(mesh_obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        selected_edges = [e for e in bm.edges if e.select]
        if not selected_edges:
            self.report({'ERROR'}, "No edges selected in Edit Mode.")
            return {'CANCELLED'}

        active_vert = bm.select_history.active if isinstance(bm.select_history.active, bmesh.types.BMVert) else None

        matrix_world = mesh_obj.matrix_world
        normal_matrix = matrix_world.to_3x3().inverted().transposed()

        edge_data = []

        for e in selected_edges:
            v1, v2 = e.verts[0], e.verts[1]

            if active_vert and active_vert in (v1, v2):
                head_v = active_vert
                tail_v = v2 if active_vert == v1 else v1
            else:
                v1_z = (matrix_world @ v1.co).z
                v2_z = (matrix_world @ v2.co).z
                if v1_z <= v2_z:
                    head_v, tail_v = v1, v2
                else:
                    head_v, tail_v = v2, v1

            w_head_pos = matrix_world @ head_v.co
            w_tail_pos = matrix_world @ tail_v.co
            w_normal = (normal_matrix @ head_v.normal).normalized()

            edge_vec = w_tail_pos - w_head_pos
            edge_dir = edge_vec.normalized() if edge_vec.length > 0.00001 else mathutils.Vector((0, 0, 1))

            edge_data.append((w_head_pos, w_normal, edge_dir))

        bmesh.update_edit_mesh(mesh_obj.data)

        armature_obj = bpy.data.objects.get(armature_name)
        if not armature_obj:
            arm_data = bpy.data.armatures.new(f"{armature_name}_Data")
            armature_obj = bpy.data.objects.new(armature_name, arm_data)
            context.collection.objects.link(armature_obj)

        armature_obj.data.display_type = 'BBONE'

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature_obj.select_set(True)
        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        existing_indices = []
        for b in armature_obj.data.edit_bones:
            if b.name.startswith(f"{prefix}_"):
                try:
                    existing_indices.append(int(b.name.split("_")[-1]))
                except ValueError:
                    pass
        start_index = max(existing_indices) + 1 if existing_indices else 0

        for i, (pos, normal, edge_dir) in enumerate(edge_data):
            bone_idx = start_index + i
            bone = armature_obj.data.edit_bones.new(name=f"{prefix}_{bone_idx:03d}")

            head_pos = pos - (normal * inside_offset)
            tail_pos = head_pos + (edge_dir * bone_length)

            bone.head = head_pos
            bone.tail = tail_pos

            bone.align_roll(normal)

            # B-Bone properties
            bone.bbone_x = bbone_scale
            bone.bbone_z = bbone_scale
            bone.bbone_scalein = mathutils.Vector((1.0, 1.0, 1.0))
            bone.bbone_scaleout = mathutils.Vector((1.0, 1.0, 1.0))
            bone.bbone_segments = segments

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, f"Added {len(edge_data)} bone(s) to '{armature_obj.name}'.")
        return {'FINISHED'}


# --- Sidebar UI Panel ---
class RIG_PT_edge_bones_panel(bpy.types.Panel):
    bl_label = "Edge Bone Generator"
    bl_idname = "RIG_PT_edge_bones_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B-Edge'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.prop(scene, "edge_bone_length")
        col.prop(scene, "edge_bbone_scale")
        col.prop(scene, "edge_inside_offset")
        col.prop(scene, "edge_segments")
        col.prop(scene, "edge_armature_name")

        layout.separator()
        layout.operator("rig.create_edge_bones", icon='BONE_DATA')


classes = (
    EDGEBONE_AddonPreferences,
    RIG_OT_create_edge_bones,
    RIG_PT_edge_bones_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Dynamic properties initialized from Add-on preferences
    prefs = bpy.context.preferences.addons[__name__].preferences if __name__ in bpy.context.preferences.addons else None
    
    bpy.types.Scene.edge_bone_length = bpy.props.FloatProperty(
        name="Bone Length", default=0.003, precision=4, min=0.0001
    )
    bpy.types.Scene.edge_bbone_scale = bpy.props.FloatProperty(
        name="BBone Scale", default=0.001, precision=6, min=0.00001
    )
    bpy.types.Scene.edge_inside_offset = bpy.props.FloatProperty(
        name="Inside Offset", default=0.0005, precision=4
    )
    bpy.types.Scene.edge_segments = bpy.props.IntProperty(
        name="B-Bone Segments", default=1, min=1, max=32
    )
    bpy.types.Scene.edge_armature_name = bpy.props.StringProperty(
        name="Armature", default="EdgeBones"
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.edge_bone_length
    del bpy.types.Scene.edge_bbone_scale
    del bpy.types.Scene.edge_inside_offset
    del bpy.types.Scene.edge_segments
    del bpy.types.Scene.edge_armature_name

if __name__ == "__main__":
    register()
