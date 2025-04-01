import time
import os
import bpy
from ..config import __addon_name__
from bpy.types import Operator
from bpy.app.handlers import persistent
from bpy.utils import previews


language_code = bpy.context.preferences.view.language
DIR_PATH = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])
ICONS_PATH = os.path.join(DIR_PATH, "icons")
PCOLL = None
preview_collections = {}

last_selection = []

os.system("color")#Enable console colors
class textColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def raiseWarning(warning):
    print(textColors.WARNING + "WARNING: " + warning + textColors.ENDC)

def get_all_children(obj):
    """递归获取对象的所有子级对象"""
    children = []

    # 获取当前对象的所有直接子对象
    for child in obj.children:
        children.append(child)  # 添加直接子对象到列表
        # 递归调用以获取子对象的子对象
        children.extend(get_all_children(child))

    return children

def ignore_children(context):
    prefs = context.preferences.addons[__addon_name__].preferences

@persistent
def log_selection(scene, depsgraph):
    global last_selection
    global puede_centrar_la_view3d
    current_selection = [obj.name for obj in bpy.context.selected_objects]
    if current_selection:
        last_selection = current_selection
    global puede_llamar_centrar_outliner
    global puede_ignorar_encima_de_outliner
    if puede_llamar_centrar_outliner or puede_ignorar_encima_de_outliner:
        # print("centrando outliner")
        centrar_outliner(bpy.context)


ha_iniciado_sync_active_on_load = False


@persistent
def al_cargar_iniciar_syncs(dummy):
    global ha_iniciado_sync_active_on_load
    # print(f"ha iniciado: {ha_iniciado_sync_active_on_load}")
    if not ha_iniciado_sync_active_on_load:
        # print("SE INICIO AL CARGAR NUEVA ESCENA")
        prefs = bpy.context.preferences.addons[__addon_name__].preferences
        if prefs.is_sync_outliner_on_start:
            bpy.context.window_manager.set_sync_show_active_toggle = True
        ha_iniciado_sync_active_on_load = True


if al_cargar_iniciar_syncs not in bpy.app.handlers.load_post:
    bpy.app.handlers.load_post.append(al_cargar_iniciar_syncs)


@persistent
def reset_sync_active_on_load(dummy):
    global ha_iniciado_sync_active_on_load
    ha_iniciado_sync_active_on_load = False


if reset_sync_active_on_load not in bpy.app.handlers.load_pre:
    bpy.app.handlers.load_pre.append(reset_sync_active_on_load)
last_active_collection = None




class OUTLINER_OT_toggle_children_visibility(Operator):
    bl_idname = "outliner.toggle_children_visibility"
    bl_label = "Toggle Children Visibility"

    def execute(self, context):
        prefs = context.preferences.addons[__addon_name__].preferences
        is_ignore = prefs.is_ignore_children
        # print(f"areas: {bpy.context.screen.areas.keys()}")
        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                for space in area.spaces:
                    if space.type == 'OUTLINER':
                        # print(f"space type: {space.type}")
                        space.use_filter_children = is_ignore
                        break
        return {'FINISHED'}



class OBJECT_OT_link_to_active_collection(Operator):
    bl_idname = "object.link_to_active_collection"
    bl_label = "Add to Active Collection"
    bl_description = "Add selected objects or last selection to active collection. \n\n \u2022 SHIFT:    Only Selected (won't move children). \n \u2022 CTRL:    Move Parents and Siblings Too"
    bl_options = {'REGISTER', 'UNDO'}
    # is_move_selected_only: bpy.props.BoolProperty(
    #     name="Move Selected Only?",
    #     description="Moves selected objects only",
    #     default=False,
    #     update=lambda self, context: self.actualizar_props()
    # )
    # is_move_with_parents_and_siblings: bpy.props.BoolProperty(
    #     name="Move Parents and Siblings?",
    #     description="if the selected objets have parents an siblings then all of them will be moved",
    #     default=False,
    #     update=lambda self, context: self.actualizar_props()
    # )

    # def actualizar_props(self):
    #     preferences = bpy.context.preferences.addons[__addon_name__].preferences
    #     outlinerpropg.is_nested = preferences.is_nested
    #     outlinerpropg.is_move_selected_only = preferences.is_move_selected_only
    #     outlinerpropg.is_move_with_parents_and_siblings = preferences.is_move_with_parents_and_siblings


    def execute(self, context):
        hide_select_viewport_render_list = []

        preferences = bpy.context.preferences.addons[__addon_name__].preferences
        outlinerpropg = bpy.context.scene.outlinerpropg
        if not outlinerpropg.is_move_selected_only:
            outlinerpropg.is_move_selected_only = preferences.is_move_selected_only
        if not outlinerpropg.is_move_with_parents_and_siblings:
            outlinerpropg.is_move_with_parents_and_siblings = preferences.is_move_with_parents_and_siblings
        objects_to_link = []
        active_collection = context.view_layer.active_layer_collection.collection
        if not active_collection:
            self.report({'WARNING'}, "No active collection found.")
            return {'CANCELLED'}
        if bpy.context.selected_objects:
            objects_to_link = bpy.context.selected_objects
        moved_collections = move_selected_collections_to_active()
        # print(f"COL TO MOVE: {moved_collections}")
        if not objects_to_link and not moved_collections:
            self.report({'WARNING'}, "No objects or collections to move.")
            return {'CANCELLED'}
        if moved_collections:
            for collection in moved_collections:
                for obj in collection.all_objects:
                    obj.select_set(False)
                    if obj in objects_to_link:
                        objects_to_link.remove(obj)
                    context.view_layer.objects.active = obj
            moved_collections
        if objects_to_link:
            if not outlinerpropg.is_move_selected_only:
                for obj in objects_to_link:
                    # print("buscando!!")

                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    if obj.children:
                        all_children = get_all_children(obj)

                        #获取所有子级对象的视图可见性
                        for child in all_children:
                            # print(child.name)
                            #将每个子级对象的可见性存于列表中
                            hide_select_viewport_render_list.append([child, child.hide_select, child.hide_viewport, child.hide_render])
                            #暂时将对象的可见性全部置为可见
                            child.hide_select = False
                            child.hide_viewport = False
                            child.hide_render = False

                        # print("TIene hijos")
                        # print(hide_select_viewport_render_list)
                        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
                        # print("seleccionó recursivo hijos")



                    if obj.parent and outlinerpropg.is_move_with_parents_and_siblings:
                        obj.parent.select_set(True)
                        # print("tiene parents")
                        bpy.ops.object.select_grouped(extend=True, type='SIBLINGS')
                        # print("seleccionó Parents y siblings")
                objects_to_link = bpy.context.selected_objects
            for obj in objects_to_link:
                if obj and obj.name not in active_collection.objects:
                    active_collection.objects.link(obj)
                    #还原子级对象的可见性
                    for list in hide_select_viewport_render_list:
                        if list[0] == obj:
                            obj.hide_select = list[1]
                            obj.hide_viewport = list[2]
                            obj.hide_render = list[3]

                    for collection in obj.users_collection:
                        if collection != active_collection:
                            collection.objects.unlink(obj)
            if not bpy.context.active_object.library:
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects_to_link:
                if obj:
                    obj.select_set(True)
            context.view_layer.objects.active = objects_to_link[0]
        if context.view_layer.objects.active:
            context.view_layer.objects.active.select_set(True)
            bpy.app.timers.register(llamar_centrar_outliner_con_retraso, first_interval=0.4)
            self.report({'INFO'}, "Objects linked to active collection.")
        la_layer_collection = encontrar_layer_collection(active_collection.name, context.view_layer.layer_collection)
        context.view_layer.active_layer_collection = la_layer_collection
        outlinerpropg.should_update = True
        return {'FINISHED'}

    def invoke(self, context, event):
        outlinerpropg = bpy.context.scene.outlinerpropg
        outlinerpropg.should_update = False
        outlinerpropg.is_move_selected_only = event.shift
        outlinerpropg.is_move_with_parents_and_siblings = event.ctrl
        return self.execute(context)

def llamar_centrar_outliner_con_retraso():
    global puede_ignorar_encima_de_outliner
    puede_ignorar_encima_de_outliner = True
    centrar_outliner(bpy.context)
    # print("outliner centrado despues de un tiempo")
    return None


def encontrar_layer_collection(name, the_layer_collection=None):
    if the_layer_collection is None:
        the_layer_collection = bpy.context.view_layer.layer_collection
    if the_layer_collection.name == name:
        return the_layer_collection
    else:
        for una_col in the_layer_collection.children:
            if lc_encontrada := encontrar_layer_collection(name=name, the_layer_collection=una_col):
                return lc_encontrada




class OBJECT_OT_create_and_link_to_new_collection(Operator):
    bl_idname = "object.create_and_link_to_new_collection"
    bl_label = "Create and Add Objects to New Collection"
    bl_description = (
        "Add a new nested collection and move selected objects inside. \n \n \u2022 SHIFT:    Only Selected (won't move children). \n \u2022 CTRL:    Move Parents and Siblings Too. \n \u2022 ALT  :    Add a custom name + Options"
    )
    bl_options = {'REGISTER', 'UNDO'}
    default_collection_name_OP: bpy.props.StringProperty(name="Collection Name", default="New Collection")
    # is_nested: bpy.props.BoolProperty(
    #     name="Nested?",
    #     description="Whether the collection should be nested in the active collection",
    #     default=True,
    #     update=lambda self, context: self.actualizar_props()
    # )
    # is_move_selected_only: bpy.props.BoolProperty(
    #     name="Move Selected Only?",
    #     description="Moves selected objects only",
    #     default=False,
    #     update=lambda self, context: self.actualizar_props()
    # )
    # is_move_with_parents_and_siblings: bpy.props.BoolProperty(
    #     name="Move Parents and Siblings?",
    #     description="if the selected objets have parents an siblings then all of them will be moved",
    #     default=False,
    #     update=lambda self, context: self.actualizar_props()
    # )

    # def actualizar_props(self):
    #     preferences = bpy.context.preferences.addons[__addon_name__].preferences
    #     outlinerpropg.is_nested = preferences.is_nested
    #     outlinerpropg.is_move_selected_only = preferences.is_move_selected_only
    #     outlinerpropg.is_move_with_parents_and_siblings = preferences.is_move_with_parents_and_siblings


    def execute(self, context):
        global last_active_collection
        new_collection = bpy.data.collections.new(self.default_collection_name_OP)
        outlinerpropg = bpy.context.scene.outlinerpropg
        preferences = bpy.context.preferences.addons[__addon_name__].preferences
        is_move_selected_temp = preferences.is_move_selected_only
        is_move_with_parents_and_siblings_temp = preferences.is_move_with_parents_and_siblings
        is_restore_properties = False
        if not outlinerpropg.is_move_selected_only:
            outlinerpropg.is_move_selected_only = preferences.is_move_selected_only
        else:
            preferences.is_move_selected_only = True
            is_restore_properties = True
        if not outlinerpropg.is_move_with_parents_and_siblings:
            outlinerpropg.is_move_with_parents_and_siblings = preferences.is_move_with_parents_and_siblings
        else:
            preferences.is_move_with_parents_and_siblings = True
            is_restore_properties = True
        preferences.is_nested = outlinerpropg.is_nested
        if outlinerpropg.is_nested:
            active_collection = context.view_layer.active_layer_collection.collection
            if active_collection:
                active_collection.children.link(new_collection)
            else:
                context.scene.collection.children.link(new_collection)
        else:
            active_collection = context.view_layer.active_layer_collection.collection
            context.scene.collection.children.link(new_collection)
        last_active_collection = bpy.context.collection.name
        current_active_collection = last_active_collection
        la_layer_collection = encontrar_layer_collection(new_collection.name, context.view_layer.layer_collection)
        context.view_layer.active_layer_collection = la_layer_collection
        state = bpy.ops.object.link_to_active_collection()
        # if state == {'CANCELLED'}:
        #     self.report({'WARNING'}, "No objects or collections to move.")
        #     return {'CANCELLED'}
        if bpy.context.selected_objects is not None:
            self.report({'WARNING'}, "No objects or collections to move.")
            return {'FINISHED'}
        else:
            # print(f"pref is move selected: {preferences.is_move_selected_only}")
            # print(f"pref move with siblings and parents: {preferences.is_move_with_parents_and_siblings}")
            la_layer_collection = encontrar_layer_collection(current_active_collection, context.view_layer.layer_collection)
            context.view_layer.active_layer_collection = la_layer_collection
            if is_restore_properties:
                preferences.is_move_selected_only = is_move_selected_temp
                preferences.is_move_with_parents_and_siblings = is_move_with_parents_and_siblings_temp
                # print("despues de restauracion:")
                # print(f"pref is move selected: {preferences.is_move_selected_only}")
                # print(f"pref move with lzy siblings and parents: {preferences.is_move_with_parents_and_siblings}")
            outlinerpropg.should_update = True

            # self.report({'INFO'}, f"Objects linked to new collection: {self.default_collection_name_OP}")
            if language_code in ["zh_CN", "zh_TW", "zh_HANS"]:
                self.report({'INFO'}, f"对象已链接到新集合 -  {self.default_collection_name_OP}")
            else:
                self.report({'INFO'}, f"Objects linked to new collection - {self.default_collection_name_OP}")
            return {'FINISHED'}

    def invoke(self, context, event):
        active_collection = context.view_layer.active_layer_collection.collection
        outlinerpropg = bpy.context.scene.outlinerpropg
        outlinerpropg.should_update = False
        if not active_collection:
            self.report({'WARNING'}, "No active collection found.")
            return {'CANCELLED'}
        self.default_collection_name_OP = active_collection.name
        if self.default_collection_name_OP == bpy.context.view_layer.layer_collection.name:
            self.default_collection_name_OP += ".001"

        outlinerpropg.is_move_selected_only = event.shift
        # print(outlinerpropg.is_move_selected_only)
        outlinerpropg.is_move_with_parents_and_siblings = event.ctrl
        preferences = bpy.context.preferences.addons[__addon_name__].preferences
        # print("antes de entrar")
        if event.alt:
            # print("ALT PRESIONADA")
            outlinerpropg.is_nested = preferences.is_nested
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


def get_outliner_context_override():
    override = None
    for area in bpy.context.screen.areas:
        if area.type == 'OUTLINER':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    break
            break
    if not override:
        return []
    return override

# def get_selected_collections():
#     """Obtiene las colecciones seleccionadas en el Outliner."""
#     selected_collections = []
#     override = None
#     for area in bpy.context.screen.areas:
#         if area.type == 'OUTLINER':
#             for region in area.regions:
#                 if region.type == 'WINDOW':
#                     override = {'area': area, 'region': region}
#                     break
#             break
#     if not override:
#         return []
#     with bpy.context.temp_override(area=override['area'], region=override['region']):
#         selection = bpy.context.selected_ids
#         selected_collections = [sel for sel in selection if sel.rna_type.name == 'Collection']
#     return selected_collections


def get_selected_collections():
    """获取在 Outliner 中选择的集合。"""
    selected_collections = []

    if bpy.app.version >= (4, 0, 0):
        override = None
        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region}
                        break
                break
        if not override:
            return []
        with bpy.context.temp_override(area=override['area'], region=override['region']):
            selection = bpy.context.selected_ids
            selected_collections = [sel for sel in selection if sel.rna_type.name == 'Collection']

    else:
        # 遍历所有区域，查找 Outliner 区域
        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                # 获取选中的 ID
                selection = bpy.context.selected_ids
                selected_collections = [sel for sel in selection if sel.rna_type.name == 'Collection']
                break

    return selected_collections


def get_collections_to_move(selected_collections):
    provisional_to_move = []
    sub_kids = []
    collections_to_move = []
    active_collection = bpy.context.collection
    for sel_collection in selected_collections:
        if sel_collection.children and active_collection.name != sel_collection.name:
            for kid in sel_collection.children_recursive:
                if active_collection.name == kid.name:
                    # print("No se puede mover al padre de una coleccion activa dentro de la coleccion activa")
                    return None
                sub_kids.append(kid)
            # print(f"lista kids: {sub_kids}")
    for collection in selected_collections:
        # print(f"coleccion sel: {collection.name} la activa es: {active_collection.name}")
        if collection not in sub_kids:
            # print(f"esta {collection.name} no esta en subkids!!")
            if collection.name != active_collection.name:
                if collection.name not in active_collection.children.keys():
                    # print("son diferentes!!")
                    collections_to_move.append(collection)
    # print(f"to move: {collections_to_move}")
    return collections_to_move


def move_selected_collections_to_active():
    active_collection = bpy.context.collection
    if not active_collection:
        # raiseWarning("No active collection found.")
        return
    preferences = bpy.context.preferences.addons[__addon_name__].preferences
    selected_collections = get_selected_collections()
    # print(f"Colecciones Seleccionadas: {selected_collections}")
    if not selected_collections:
        # raiseWarning("No objects or collections to move.")
        return
    global last_active_collection
    # print(f"last active: {last_active_collection}")
    if last_active_collection and preferences.is_nested:
        # print("ELIMINAR ACTIVE")
        for collection in selected_collections:
            if collection.name == last_active_collection:
                selected_collections.remove(collection)
        last_active_collection = ""
    collections_to_move = get_collections_to_move(selected_collections)
    # print(f"lo que tiene ahorita: {collections_to_move}")
    if not collections_to_move:
        # raiseWarning("No collections to move.")
        return
    for collection in collections_to_move:
        if collection.name != active_collection.name and collection.name not in active_collection.children.keys():
            # print("buscar el padre")
            for parent_collection in bpy.context.scene.collection.children_recursive:
                # print("buscando")
                if collection.name in parent_collection.children.keys():
                    parent_collection.children.unlink(collection)
                    # print("desvincular coleccion!!!!")
                    break
            if collection.name in bpy.context.scene.collection.children.keys():
                bpy.context.scene.collection.children.unlink(collection)
            active_collection.children.link(collection)
        else:
            # if language_code in ["zh_CN", "zh_TW", "zh_HANS"]:
            #     raiseWarning(
            #         f"警告：集合 '{collection.name}' 已在 '{active_collection.name}' 中或是活动集合.")
            # else:
            raiseWarning(
                f"Warning: The collection '{collection.name}' is already in '{active_collection.name}' or is the active collection.")
    # print("Colecciones seleccionadas movidas a la colección activa.")
    return collections_to_move




class OBJECT_OT_rename_objects_in_collection(Operator):
    bl_idname = "object.rename_objects_in_collection"
    bl_label = "Rename by Collection"
    bl_description = "Renames all objects in the selected collection with the collection's name and a number"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.active_layer_collection is not None

    def execute(self, context):
        active_collection = context.view_layer.active_layer_collection.collection
        collection_name = active_collection.name
        for i, obj in enumerate(active_collection.objects, start=1):
            new_name = f"{collection_name}_{i:02d}"
            obj.name = new_name
        if language_code in ["zh_CN", "zh_TW", "zh_HANS"]:
            self.report({'INFO'}, f"在集合 '{collection_name}' 中重命名了 {len(active_collection.objects)} 个对象")
        else:
            self.report({'INFO'}, f"Renamed {len(active_collection.objects)} objects in collection '{collection_name}'")
        return {'FINISHED'}


def menu_rightclick_operators(self, context):
    layout = self.layout
    layout.operator("object.link_to_active_collection", icon_value=preview_collections["icons"]['ADD_TO_COLLECTION'].icon_id)
    layout.operator(OBJECT_OT_create_and_link_to_new_collection.bl_idname,
                    icon_value=preview_collections["icons"]['CREATE_AND_ADD_TO_COLLECTION'].icon_id)
    self.layout.operator(OBJECT_OT_rename_objects_in_collection.bl_idname)
    layout.separator()


def draw_link_button(self, context):
    layout = self.layout
    layout.operator("object.link_to_active_collection", text="", icon_value=preview_collections["icons"]['ADD_TO_COLLECTION'].icon_id)
    layout.operator("object.create_and_link_to_new_collection", text="",
                    icon_value=preview_collections["icons"]['CREATE_AND_ADD_TO_COLLECTION'].icon_id)
    layout.prop(context.window_manager, "set_color_to_collection_toggle", text="",
                icon_value=preview_collections["icons"]['USE_COLLECTION_COLOR'].icon_id)
    layout.prop(context.window_manager, "set_sync_show_active_toggle", text="",
                icon_value=preview_collections["icons"]['SYNC_OUTLINER'].icon_id)
    # layout.operator("object.sync_visibility_operator", text="",
    #                 icon_value=mis_iconos['SYNC_VIEWPORT_AND_RENDER'].icon_id)


def agregar_botones_en_rightclick_object(self, context):
    layout = self.layout
    layout.operator("object.link_to_active_collection", icon_value=preview_collections["icons"]['ADD_TO_COLLECTION'].icon_id)
    layout.operator(OBJECT_OT_create_and_link_to_new_collection.bl_idname,
                    icon_value=preview_collections["icons"]['CREATE_AND_ADD_TO_COLLECTION'].icon_id)
    layout.separator()


def get_collection_theme_color(color_tag):
    tag_to_index = {
        'COLOR_01': 0,
        'COLOR_02': 1,
        'COLOR_03': 2,
        'COLOR_04': 3,
        'COLOR_05': 4,
        'COLOR_06': 5,
        'COLOR_07': 6,
        'COLOR_08': 7,
    }
    index = tag_to_index.get(color_tag, None)
    if index is not None:
        color_rgb = bpy.context.preferences.themes[0].collection_color[index].color
        return (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
    else:
        return (1.0, 1.0, 1.0, 1.0)


es_update_object_colors = False
last_workspace = ""




class OBJECT_OT_SetColorToCollection(Operator):
    bl_idname = "object.set_color_to_collection"
    bl_label = "Sync Collection's Color"
    bl_description = "Set the color of all objects in the selected collection to the collection color"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        global es_update_object_colors
        global es_puede_cambiar_el_shading_type
        global puede_usar_mousemove
        global collection_color_tags
        global collection_obj_count
        global object_colors
        global last_workspace
        if not context.window_manager.set_color_to_collection_toggle:
            es_puede_cambiar_el_shading_type = False
            cambiar_color_type_del_viewshading(cambiar_color_type=False)
            return {'CANCELLED'}
        if last_workspace != bpy.context.window.workspace.name:
            last_workspace = bpy.context.window.workspace.name
            cambiar_color_type_del_viewshading(cambiar_color_type=True)
        if event.type == 'LEFTMOUSE':
            es_update_object_colors = True
        if event.type in {'MOUSEMOVE'}:
            if es_update_object_colors or puede_usar_mousemove:
                puede_usar_mousemove = False
                es_update_object_colors = False
                if context.window_manager.set_color_to_collection_toggle:
                    # print("updating colors")
                    if es_puede_cambiar_el_shading_type:
                        cambiar_color_type_del_viewshading(cambiar_color_type=True)
                    update_object_colors()
                    return {'PASS_THROUGH'}
                else:
                    return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        cambiar_color_type_del_viewshading()
        update_object_colors()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


es_update_object_colors = False
collection_color_tags = {}
collection_obj_count = {}
object_colors = {}


def update_object_colors():
    global collection_color_tags
    global object_colors
    procesa_collection_colors(bpy.context.scene.collection)
    current_collections = {collection.name: collection for collection in bpy.data.collections}
    for collection_name in list(collection_color_tags.keys()):
        if collection_name not in current_collections:
            del collection_color_tags[collection_name]
            del collection_obj_count[collection_name]
            # print(f"count: {collection_obj_count}")
            # print(f"Colección '{collection_name}' eliminada de la lista.")
    current_objects = {obj.name: obj for obj in bpy.data.objects}
    for obj_name in list(object_colors.keys()):
        if obj_name not in current_objects:
            del object_colors[obj_name]
            # print(f"Objeto '{obj_name}' eliminado de la lista.")


def procesa_collection_colors(the_collection):
    global collection_color_tags
    global collection_obj_count
    for collection in the_collection.children:
        if collection.name in collection_color_tags:
            if collection.color_tag != collection_color_tags[collection.name]:
                collection_color_tags[collection.name] = collection.color_tag
                agrega_o_cambia_object_colors(collection)
            cantidad_objetos_en_collection = len(collection.objects)
            if cantidad_objetos_en_collection != collection_obj_count[collection.name]:
                collection_obj_count[collection.name] = cantidad_objetos_en_collection
                agrega_o_cambia_object_colors(collection)
        else:
            collection_color_tags[collection.name] = collection.color_tag
            collection_obj_count[collection.name] = len(collection.objects)
            agrega_o_cambia_object_colors(collection)
        procesa_collection_colors(collection)


def agrega_o_cambia_object_colors(collection):
    global object_colors
    global collection_obj_count
    for obj in collection.objects:
        if obj.name in object_colors:
            if hasattr(obj, "color"):
                object_color_tag_actual = get_tag_from_color(obj.color)
                asignar_collection_color_to_object_color(obj, object_color_tag_actual, collection.color_tag)
        else:
            object_colors[obj.name] = get_color_from_tag(collection.color_tag)
            collection_obj_count[collection.name] = len(collection.objects)
            asignar_collection_color_to_object_color(obj, get_tag_from_color(obj.color), collection.color_tag)


def asignar_collection_color_to_object_color(the_object, its_tag, collection_tag):
    if its_tag != collection_tag:
        the_object.color = get_color_from_tag(collection_tag)
        object_colors[the_object.name] = get_color_from_tag(collection_tag)


def get_color_from_tag(color_tag):
    color_mapping = {
        'COLOR_01': bpy.context.preferences.themes[0].collection_color[0].color,
        'COLOR_02': bpy.context.preferences.themes[0].collection_color[1].color,
        'COLOR_03': bpy.context.preferences.themes[0].collection_color[2].color,
        'COLOR_04': bpy.context.preferences.themes[0].collection_color[3].color,
        'COLOR_05': bpy.context.preferences.themes[0].collection_color[4].color,
        'COLOR_06': bpy.context.preferences.themes[0].collection_color[5].color,
        'COLOR_07': bpy.context.preferences.themes[0].collection_color[6].color,
        'COLOR_08': bpy.context.preferences.themes[0].collection_color[7].color,
    }
    color = color_mapping.get(color_tag, (1.0, 1.0, 1.0, 1.0))
    if len(color) == 3:
        color = (*color, 1.0)
    return color


def get_tag_from_color(object_color):
    color_mapping = {
        'NONE': (1.0, 1.0, 1.0),
        'COLOR_01': bpy.context.preferences.themes[0].collection_color[0].color,
        'COLOR_02': bpy.context.preferences.themes[0].collection_color[1].color,
        'COLOR_03': bpy.context.preferences.themes[0].collection_color[2].color,
        'COLOR_04': bpy.context.preferences.themes[0].collection_color[3].color,
        'COLOR_05': bpy.context.preferences.themes[0].collection_color[4].color,
        'COLOR_06': bpy.context.preferences.themes[0].collection_color[5].color,
        'COLOR_07': bpy.context.preferences.themes[0].collection_color[6].color,
        'COLOR_08': bpy.context.preferences.themes[0].collection_color[7].color,
    }
    object_color_rounded = tuple(round(c, 4) for c in object_color[:3])
    for tag, color in color_mapping.items():
        color_rounded = tuple(round(c, 4) for c in color)
        if object_color_rounded == color_rounded:
            return tag
    return None


puede_usar_mousemove = False


def actualizar_puede_usar_mousemove():
    global puede_usar_mousemove
    eltoggle = False
    eltoggle = bpy.context.window_manager.set_color_to_collection_toggle
    if not eltoggle:
        bpy.app.timers.unregister(actualizar_puede_usar_mousemove)
        puede_usar_mousemove = False
        return 0.0
    else:
        puede_usar_mousemove = True
        return 1.0


es_puede_cambiar_el_shading_type = True


def cambiar_color_type_del_viewshading(cambiar_color_type=True):
    global es_puede_cambiar_el_shading_type
    es_puede_cambiar_el_shading_type = not cambiar_color_type
    scene = bpy.context.scene
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if cambiar_color_type:
                        space.shading.color_type = 'OBJECT'
                        space.shading.wireframe_color_type = 'OBJECT'
                        break
                    else:
                        space.shading.color_type = 'MATERIAL'
                        if bpy.app.version >= (4, 0, 0):
                            space.shading.wireframe_color_type = 'THEME'
                        else:
                            space.shading.wireframe_color_type = 'MATERIAL'


def draw_outliner_toggle(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.label(icon_value=preview_collections["icons"]['USE_COLLECTION_COLOR'].icon_id)
    row.separator(factor=1.25)
    row.prop(context.window_manager, "set_color_to_collection_toggle", text="Sync Collection's Color")
    row = layout.row(align=True)
    row.label(icon_value=preview_collections["icons"]['SYNC_OUTLINER'].icon_id)
    row.separator(factor=1.25)
    row.prop(context.window_manager, "set_sync_show_active_toggle", text="Sync Active Selection")
    # row = layout.row(align=True)
    # row.label(icon_value=mis_iconos['SYNC_VIEWPORT_AND_RENDER'].icon_id)
    # row.separator(factor=1.25)
    # row.operator("object.sync_visibility_operator", text="Sync Viewport/Render")


def draw_shading_toggle(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.label(icon_value=preview_collections["icons"]['USE_COLLECTION_COLOR'].icon_id)
    row.separator(factor=1.25)
    row.prop(context.window_manager, "set_color_to_collection_toggle", text="Use Collection's Color")




class SyncShowActive(Operator):
    bl_idname = "wm.sync_show_active"
    bl_label = "Sync Active"
    bl_description = "Keeps the Outliner focused on the active object"
    bl_options = {'REGISTER'}
    is_ignore_children: bpy.props.BoolProperty(
        name="Show Object's Children",
        description="This option hides children objects so they don't get centered in the outliner's view",
        default=False
    )
    is_auto_expand: bpy.props.BoolProperty(
        name="Auto Expand / Collapse Hierachy",
        description="After centering the Outliner it will collapse all hierachy and show the active object only",
        default=True
    )
    is_sync_outliner_on_start: bpy.props.BoolProperty(
        name="Always Active",
        description="The sync outliner will be always turned on",
        default=True
    )
    ha_usado_cuadro_de_dialogo = False

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__addon_name__].preferences
        if self.ha_usado_cuadro_de_dialogo:
            preferences.is_auto_expand = self.is_auto_expand
            preferences.is_ignore_children = self.is_ignore_children
            preferences.is_sync_outliner_on_start = self.is_sync_outliner_on_start
            bpy.ops.outliner.toggle_children_visibility('INVOKE_DEFAULT')
        else:
            self.is_ignore_children = preferences.is_ignore_children
        context.window_manager.modal_handler_add(self)
        centrar_outliner(context)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        preferences = bpy.context.preferences.addons[__addon_name__].preferences
        self.is_ignore_children = preferences.is_ignore_children
        if event.alt:
            self.ha_usado_cuadro_de_dialogo = True
            self.is_auto_expand = preferences.is_auto_expand
            self.is_ignore_children = preferences.is_ignore_children
            self.is_sync_outliner_on_start = preferences.is_sync_outliner_on_start
            return context.window_manager.invoke_props_dialog(self)
        else:
            self.ha_usado_cuadro_de_dialogo = False
            self.execute(context)
            return {'RUNNING_MODAL'}

    def check(self, context):
        return True

    def cancel(self, context):
        self.ha_usado_cuadro_de_dialogo = False
        bpy.context.window_manager.set_sync_show_active_toggle = False
        return {'CANCELLED'}

    first_click_time = 0.0
    double_click_threshold = 0.3

    def modal(self, context, event):
        if not bpy.context.window_manager.set_sync_show_active_toggle:
            self.first_click_time = 0.0
            return {'CANCELLED'}
        global puede_llamar_centrar_outliner
        global puede_ignorar_encima_de_outliner
        global puede_centrar_la_view3d
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                current_time = time.time()
                time_difference = current_time - self.first_click_time
                if time_difference < self.double_click_threshold:
                    self.first_click_time = 0.0
                    if is_mouse_over_outliner(event.mouse_x, event.mouse_y):
                        center_view3d_from_outliner(context)
                else:
                    self.first_click_time = current_time
            if event.value == 'RELEASE':
                if not is_mouse_over_outliner(event.mouse_x, event.mouse_y) or puede_ignorar_encima_de_outliner:
                    puede_llamar_centrar_outliner = True
                    puede_ignorar_encima_de_outliner = False
                return {'PASS_THROUGH'}
        return {'PASS_THROUGH'}


puede_centrar_la_view3d = False


# def center_view3d_from_outliner(context):
#     global puede_centrar_la_view3d
#     overrides = get_view3d_context_overrides()
#     for override in overrides:
#         # print(f"entro a center view, override es: {override}")
#         with context.temp_override(area=override['area'], region=override['region']):
#             if bpy.context.active_object is not None and bpy.context.active_object.select_get():
#                 # print("CENTER VIEW 3D")
#                 bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
#                 puede_centrar_la_view3d = False


def center_view3d_from_outliner(context):
    global puede_centrar_la_view3d
    overrides = get_view3d_context_overrides()

    if bpy.app.version >= (4, 0, 0):
        for override in overrides:
            # print(f"entro a center view, override es: {override}")
            with context.temp_override(area=override['area'], region=override['region']):
                if bpy.context.active_object is not None and bpy.context.active_object.select_get():
                    # print("CENTER VIEW 3D")
                    bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
                    puede_centrar_la_view3d = False
    else:
        for override in overrides:
            area = override['area']
            region = override['region']

            # 确保当前上下文是视图3D
            if area.type == 'VIEW_3D':
                # 检查是否有活动对象并且被选中
                if context.active_object is not None and context.active_object.select_get():
                    # 创建一个上下文覆盖
                    override_context = context.copy()
                    override_context['area'] = area
                    override_context['region'] = region

                    # 执行视图选择操作
                    bpy.ops.view3d.view_selected(override_context, 'INVOKE_DEFAULT')
                    puede_centrar_la_view3d = False
                    break  # 找到一个合适的区域后退出循环


def get_view3d_context_override():
    override = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    break
            break
    if not override:
        return []
    return override


def get_view3d_context_overrides():
    override = None
    override_list = []
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    override_list.append(override)
                    break
    if not override_list:
        return []
    return override_list


def iniciar_sync_outliner(self, context):
    if bpy.context.window_manager.set_sync_show_active_toggle:
        bpy.ops.wm.sync_show_active('INVOKE_DEFAULT')



puede_llamar_centrar_outliner = False
puede_ignorar_encima_de_outliner = False
last_execution_time = 0


# def centrar_outliner(context):
#     global puede_llamar_centrar_outliner
#     puede_llamar_centrar_outliner = False
#
#     global puede_ignorar_encima_de_outliner
#     puede_ignorar_encima_de_outliner = False
#
#     global last_execution_time
#     current_time = time.time()
#
#     preferences = bpy.context.preferences.addons[__addon_name__].preferences
#
#     last_execution_time = current_time
#
#     for window in bpy.context.window_manager.windows:
#         for area in window.screen.areas:
#             if area.type == 'OUTLINER':
#                 for region in area.regions:
#                     if region.type == 'WINDOW':
#
#                         with context.temp_override(window=window, area=area, region=region):
#
#                             if bpy.context.active_object is not None and bpy.context.active_object.select_get():
#
#                                 if preferences.is_auto_expand:
#                                     bpy.ops.outliner.show_one_level(open=False)
#                                 bpy.ops.outliner.show_active()


def centrar_outliner(context):
    global puede_llamar_centrar_outliner
    local_puede_llamar_centrar_outliner = puede_llamar_centrar_outliner
    puede_llamar_centrar_outliner = False

    global puede_ignorar_encima_de_outliner
    puede_ignorar_encima_de_outliner = False

    global last_execution_time
    current_time = time.time()

    preferences = bpy.context.preferences.addons[__addon_name__].preferences

    last_execution_time = current_time

    if bpy.app.version >= (4, 0, 0):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'OUTLINER':
                    for region in area.regions:
                        if region.type == 'WINDOW':

                            with context.temp_override(window=window, area=area, region=region):

                                if local_puede_llamar_centrar_outliner == True:
                                    # 确保上下文正确
                                    if bpy.context.active_object is not None and bpy.context.active_object.select_get():
                                        bpy.ops.outliner.show_one_level(open=False)
                                        bpy.ops.outliner.show_active()

                                    # break  # 找到目标区域后可以退出循环
                                else:
                                    # 确保上下文正确
                                    if bpy.context.active_object is not None and bpy.context.active_object.select_get():
                                        if preferences.is_auto_expand:
                                            bpy.ops.outliner.show_one_level(open=False)
                                        # bpy.ops.outliner.show_active(override)

                                    break  # 找到目标区域后可以退出循环

    else:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'OUTLINER':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # 创建上下文覆盖
                            override = context.copy()
                            override['window'] = window
                            override['area'] = area
                            override['region'] = region

                            if local_puede_llamar_centrar_outliner == True:
                                # 确保上下文正确
                                if bpy.context.active_object is not None and bpy.context.active_object.select_get():

                                    bpy.ops.outliner.show_one_level(override, open=False)
                                    bpy.ops.outliner.show_active(override)

                                # break  # 找到目标区域后可以退出循环
                            else:
                                # 确保上下文正确
                                if bpy.context.active_object is not None and bpy.context.active_object.select_get():
                                    if preferences.is_auto_expand:
                                        bpy.ops.outliner.show_one_level(override, open=False)
                                    # bpy.ops.outliner.show_active(override)

                                break  # 找到目标区域后可以退出循环




def is_mouse_over_outliner(x, y):
    mouse_x, mouse_y = x, y
    for area in bpy.context.window_manager.windows[0].screen.areas:
        if area.type == 'OUTLINER':
            if (area.x <= mouse_x <= area.x + area.width) and (area.y <= mouse_y <= area.y + area.height):
                return True
    return False


def update_set_color_to_collection(self, context):
    if context.window_manager.set_color_to_collection_toggle:
        bpy.ops.object.set_color_to_collection('INVOKE_DEFAULT')
        bpy.app.timers.register(actualizar_puede_usar_mousemove)
        # print("INICIAR COLOR COLLECTION")
    else:
        collection_color_tags.clear()
        collection_obj_count.clear()
        object_colors.clear()
        # print(f"no se borraron: \n {collection_color_tags} ")



class SyncVisibilityOperator(Operator):
    bl_idname = "object.sync_visibility_operator"
    bl_label = "Sync Viewport and Render Visibility"
    bl_description = "Copy viewport visibility to render visibility  \n\n \u2022 ALT  :    Invert (copy render to viewport visibility)"
    bl_options = {'UNDO'}
    is_render_to_viewport = False

    def execute(self, context):
        for layer in context.view_layer.layer_collection.children:
            self.sync_layer_collection(layer)
        if self.is_render_to_viewport:
            for obj in bpy.data.objects:
                if obj.hide_get() != obj.hide_render:
                    obj.hide_set(obj.hide_render)
        else:
            for obj in bpy.data.objects:
                if obj.hide_get() != obj.hide_render:
                    obj.hide_render = obj.hide_get()
        return {'FINISHED'}

    def invoke(self, context, event):
        self.is_render_to_viewport = event.alt
        return self.execute(context)

    def sync_layer_collection(self, layer_collection):
        if layer_collection.hide_viewport != bpy.data.collections[layer_collection.name].hide_render:
            if self.is_render_to_viewport:
                layer_collection.hide_viewport = bpy.data.collections[layer_collection.name].hide_render
            else:
                bpy.data.collections[layer_collection.name].hide_render = layer_collection.hide_viewport
        for child in layer_collection.children:
            self.sync_layer_collection(child)