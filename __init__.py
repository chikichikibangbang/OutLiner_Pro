from .addons.Outliner_Pro import register as addon_register, unregister as addon_unregister

bl_info = {
    "name": 'Outliner Pro bl3.0+',
    "author": 'Arsides Mendez, 诸葛不太亮',
    "blender": (2, 93, 0),
    "version": (1, 0),
    "description": 'A plugin that helps you quickly manage outline views.',
    "warning": '',
    "wiki_url": 'https://github.com/chikichikibangbang/OutLiner_Pro',
    "tracker_url": 'https://github.com/chikichikibangbang/OutLiner_Pro/issues',
    "support": 'COMMUNITY',
    "category": '3D View'
}

def register():
    addon_register()

def unregister():
    addon_unregister()

    