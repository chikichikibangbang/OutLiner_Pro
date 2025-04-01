import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty
from ..config import __addon_name__

def actualizar_props(self, context):
    if self.should_update:
        preferences = bpy.context.preferences.addons[__addon_name__].preferences
        if self.is_nested != preferences.is_nested:
            self.is_nested = preferences.is_nested
        if self.is_move_selected_only != preferences.is_move_selected_only:
            self.is_move_selected_only = preferences.is_move_selected_only
        if self.is_move_with_parents_and_siblings != preferences.is_move_with_parents_and_siblings:
            self.is_move_with_parents_and_siblings = preferences.is_move_with_parents_and_siblings

class OutlinerProPG(bpy.types.PropertyGroup):
    is_nested: BoolProperty(
        name="Nested?",
        description="Whether the collection should be nested in the active collection",
        default=True,
        update=actualizar_props
    )
    is_move_selected_only: BoolProperty(
        name="Move Selected Only?",
        description="Moves selected objects only",
        default=False,
        update= actualizar_props
    )
    is_move_with_parents_and_siblings: BoolProperty(
        name="Move Parents and Siblings?",
        description="if the selected objets have parents an siblings then all of them will be moved",
        default=False,
        update= actualizar_props
    )
    should_update: BoolProperty(default=True)