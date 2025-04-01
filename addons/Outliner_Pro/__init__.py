import os

import bpy

from .config import __addon_name__
from .i18n.dictionary import dictionary
from .operators.AddonOperators import draw_link_button, log_selection, \
    menu_rightclick_operators, agregar_botones_en_rightclick_object, draw_outliner_toggle, draw_shading_toggle, \
    update_set_color_to_collection, iniciar_sync_outliner, ICONS_PATH, preview_collections
from .properties.AddonProperties import OutlinerProPG
from ...common.class_loader import auto_load
from ...common.class_loader.auto_load import add_properties, remove_properties
from ...common.i18n.dictionary import common_dictionary
from ...common.i18n.i18n import load_dictionary

# Add-on info
bl_info = {
    "name": "Outliner Pro bl3.0+",
    "author": "Arsides Mendez, 诸葛不太亮",
    "blender": (2, 93, 0),
    "version": (1, 0),
    "description": "A plugin that helps you quickly manage outline views.",
    "warning": "",
    "wiki_url": "https://github.com/chikichikibangbang/OutLiner_Pro",
    "tracker_url": "https://github.com/chikichikibangbang/OutLiner_Pro/issues",
    "support": "COMMUNITY",
    "category": "3D View"
}

_addon_properties = {}



# You may declare properties like following, framework will automatically add and remove them.
# Do not define your own property group class in the __init__.py file. Define it in a separate file and import it here.
# 注意不要在__init__.py文件中自定义PropertyGroup类。请在单独的文件中定义它们并在此处导入。
# _addon_properties = {
#     bpy.types.Scene: {
#         "property_name": bpy.props.StringProperty(name="property_name"),
#     },
# }
#


def register():
    # Register classes
    auto_load.init()
    # cargar_iconos_personalizados()
    global preview_collections
    auto_load.register()

    icon_names = ["bilibili", "blendermarket", "ADD_TO_COLLECTION", "CREATE_AND_ADD_TO_COLLECTION", "SYNC_OUTLINER", "SYNC_VIEWPORT_AND_RENDER", "USE_COLLECTION_COLOR"]
    pcoll = bpy.utils.previews.new()
    for icon_name in icon_names:
        pcoll.load(icon_name, os.path.join(ICONS_PATH, icon_name + ".png"), 'IMAGE')
    if preview_collections.get('icons'):
        bpy.utils.previews.remove(preview_collections['icons'])
    preview_collections['icons'] = pcoll

    add_properties(_addon_properties)

    # Internationalization
    load_dictionary(dictionary)
    bpy.app.translations.register(__addon_name__, common_dictionary)

    bpy.types.OUTLINER_HT_header.append(draw_link_button)
    bpy.app.handlers.depsgraph_update_post.append(log_selection)
    bpy.types.OUTLINER_MT_collection.prepend(menu_rightclick_operators)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(agregar_botones_en_rightclick_object)
    bpy.types.OUTLINER_PT_filter.append(draw_outliner_toggle)
    bpy.types.VIEW3D_PT_shading.append(draw_shading_toggle)
    bpy.types.WindowManager.set_color_to_collection_toggle = bpy.props.BoolProperty(
        name="Sync Collection's Color",
        description="Use the collection color to shade objects in the viewport",
        default=False,
        update=update_set_color_to_collection
    )
    bpy.types.WindowManager.set_sync_show_active_toggle = bpy.props.BoolProperty(
        name="Sync Show Active",
        description="Centers the outliner view to the active object",
        default=False,
        update=iniciar_sync_outliner
    )
    bpy.types.Scene.outlinerpropg = bpy.props.PointerProperty(type=OutlinerProPG)

    print("{} addon is installed.".format(__addon_name__))


def unregister():
    # Internationalization
    # quitar_iconos_personalizados()
    global preview_collections
    bpy.app.translations.unregister(__addon_name__)

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    # unRegister classes
    auto_load.unregister()
    remove_properties(_addon_properties)
    bpy.types.OUTLINER_HT_header.remove(draw_link_button)
    bpy.types.OUTLINER_MT_collection.remove(menu_rightclick_operators)
    bpy.types.VIEW3D_MT_object_context_menu.remove(agregar_botones_en_rightclick_object)
    bpy.types.OUTLINER_PT_filter.remove(draw_outliner_toggle)
    bpy.types.VIEW3D_PT_shading.remove(draw_shading_toggle)
    del bpy.types.WindowManager.set_color_to_collection_toggle
    del bpy.types.WindowManager.set_sync_show_active_toggle
    if log_selection in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(log_selection)

    print("{} addon is uninstalled.".format(__addon_name__))





