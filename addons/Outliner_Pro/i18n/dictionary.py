from ....common.i18n.dictionary import preprocess_dictionary

dictionary = {
    "zh_CN": {
        #AddonPreferences
        ("*", "Set Default Options:"): "设置默认选项:",
        ("*", "Create and Move to Collection:"): "创建并移动到集合:",
        ("*", "Move Only Selected Objects (if ON parents and childrens are ignored)"): "仅移动所选对象（如果开启，则忽略父级与子级）",
        ("*", "Moves selected objects only"): "仅移动所选对象",
        ("*", "Move Parents and Siblings?"): "移动父级和兄弟对象?",
        ("*", "If the selected objets have parents an siblings then all of them will be moved"): "如果所选对象有兄弟和父级对象，那么所有这些对象都将被移动",
        ("*", "Nest new collection into the active one?"): "将新集合嵌套到活动集合中?",
        ("*", "Whether the collection should be nested in the active collection"): "是否应该将此集合嵌套到活动集合中",
        ("*", "Default name for newly created collections:"): "新创建集合的默认名称:",
        ("*", "Collection Name"): "集合名称",
        ("*", "Sync Show Active:"): "同步显示活动:",
        ("*", "Auto Expand / Collapse Hierachy"): "自动展开/折叠层级",
        ("*", "After centering the Outliner it will collapse all hierachy and show the active object only"): "在居中大纲视图后，将折叠所有层级，仅显示活动对象",
        ("*", "Show Object's Children"): "显示对象的子级对象",
        ("*", "This option hides children objects so they don't get centered in the outliner's view"): "此选项隐藏子级对象，以便让它们不在大纲视图中居中",
        ("*", "Always Active"): "始终处于活动状态",
        ("*", "The sync outliner will be always turned on"): "同步大纲视图将始终开启",
        ("*", "Frame Selected on Double Click"): "双击选择框架",

        #AddonOperators
        ("Operator", "Toggle Children Visibility"): "切换子级对象可见性",
        ("Operator", "Add to Active Collection"): "添加到活动集合",
        ("*", "Add selected objects or last selection to active collection. "
              "\n\n \u2022 SHIFT:    Only Selected (won't move children). "
              "\n \u2022 CTRL:    Move Parents and Siblings Too"): "将当前所选或最后所选的对象添加到活动集合."
                                                                   "\n\n \u2022 SHIFT     仅所选（不会移动子级对象）."
                                                                   "\n \u2022 CTRL      也会移动父级和同级对象",

        ("*", "No active collection found."): "未找到活动集合.",
        ("*", "No objects or collections to move."): "没有可移动的对象或集合.",
        ("*", "Objects linked to active collection."): "对象已链接到活动集合.",

        ("Operator", "Create and Add Objects to New Collection"): "创建新集合并将对象添加到其中",
        ("*", "Add a new nested collection and move selected objects inside. "
              "\n \n \u2022 SHIFT:    Only Selected (won't move children). "
              "\n \u2022 CTRL:    Move Parents and Siblings Too. "
              "\n \u2022 ALT  :    Add a custom name + Options"): "添加一个新的嵌套集合并将所选对象移动到其中."
                                                                  "\n \n \u2022 SHIFT     仅所选（不会移动子级对象）."
                                                                  "\n \u2022 CTRL      也会移动父级和同级对象."
                                                                  "\n \u2022 ALT         添加自定义的名称和选项",

        ("*", "No selected collection found."): "未找到选中的集合.",
        ("*", "No collections to move."): "没有可移动的集合.",

        ("Operator", "Rename by Collection"): "按照集合重命名",
        ("*", "Renames all objects in the selected collection with the collection's name and a number"): "使用集合的名称和编号重命名所选集合中的所有对象",
        ("Operator", "Sync Collection's Color"): "同步集合颜色",
        ("*", "Set the color of all objects in the selected collection to the collection color"): "将所选集合中所有对象的颜色设置为集合的颜色",
        ("*", "Sync Collection's Color"): "同步集合颜色",
        ("*", "Sync Active Selection"): "同步活动选择",
        ("*", "Use Collection's Color"): "使用集合的颜色",
        ("Operator", "Sync Active"): "同步活动项",
        ("*", "Sync Active"): "同步活动项",
        ("*", "Keeps the Outliner focused on the active object"): "让大纲视图落在活动对象的位置上",
        ("*", "Use the collection color to shade objects in the viewport"): "在视图中使用集合颜色对对象进行着色",
        ("*", "Sync Show Active"): "同步显示活动项",
        ("*", "Centers the outliner view to the active object"): "将大纲视图置于活动对象的中心",
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
