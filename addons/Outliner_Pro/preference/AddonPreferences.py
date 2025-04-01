import os

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import AddonPreferences

from ..config import __addon_name__
from ..operators.AddonOperators import ICONS_PATH, preview_collections


class PreferenciasOutlinerPro(bpy.types.AddonPreferences):
    bl_idname = __addon_name__
    default_collection_name_OP: bpy.props.StringProperty(name="Collection Name", default="New Collection")
    is_nested: bpy.props.BoolProperty(
        name="Nested?",
        description="Whether the collection should be nested in the active collection",
        default=True
    )
    is_move_selected_only: bpy.props.BoolProperty(
        name="Move Selected Only?",
        description="Moves selected objects only",
        default=False
    )
    is_move_with_parents_and_siblings: bpy.props.BoolProperty(
        name="Move Parents and Siblings?",
        description="If the selected objets have parents an siblings then all of them will be moved",
        default=False
    )
    is_ignore_children: bpy.props.BoolProperty(
        name="Show Object's Children",
        description="This option hides children objects so they don't get centered in the outliner's view",
        default=False
    )
    is_auto_expand: bpy.props.BoolProperty(
        name="Auto Expand / Collapse Hierachy",
        description="After centering the Outliner it will collapse all hierachy and show the active object only",
        default=False
    )
    is_sync_outliner_on_start: bpy.props.BoolProperty(
        name="Always Active",
        description="The sync outliner will be always turned on",
        default=True
    )
    is_frame_selected: bpy.props.BoolProperty(
        name="Frame Selected on Double Click",
        description="The sync outliner will be always turned on",
        default=True
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.1
        op = row.operator(
            'wm.url_open',
            text='Blender Market',
            icon_value=preview_collections["icons"]['blendermarket'].icon_id
        )
        op.url = 'https://blendermarket.com/products/outliner-pro'
        op1 = row.operator(
            'wm.url_open',
            text='Bilibili',
            icon_value=preview_collections["icons"]['bilibili'].icon_id
        )
        op1.url = 'https://space.bilibili.com/84161516?spm_id_from=333.1007.0.0'


        layout.label(text="Set Default Options:", icon='PREFERENCES')
        box = layout.box()
        row = box.row()
        row.label(text="", icon_value=preview_collections["icons"]['ADD_TO_COLLECTION'].icon_id)
        row.label(text="Create and Move to Collection:", icon_value=preview_collections["icons"]['CREATE_AND_ADD_TO_COLLECTION'].icon_id)
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "is_move_selected_only",
                 text="Move Only Selected Objects (if ON parents and childrens are ignored)")
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "is_move_with_parents_and_siblings")
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "is_nested", text="Nest new collection into the active one?")
        row = box.row(align=True)
        row.separator(factor=3)
        row.label(text="Default name for newly created collections:")
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "default_collection_name_OP", text="Collection Name")
        box = layout.box()
        box.label(text="Sync Show Active:", icon_value=preview_collections["icons"]['SYNC_OUTLINER'].icon_id)
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "is_auto_expand")
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "is_ignore_children")
        row = box.row(align=True)
        row.separator(factor=3)
        row.prop(self, "is_sync_outliner_on_start")
