from __future__ import print_function
import pkgutil
import importlib

def load_plugin_widgets(pkg_path):
    p_widgets = [] 
    widg_mods = pkgutil.iter_modules(pkg_path)
    widg_mods = [mod for mod in widg_mods if mod[1] not in ['__init__','PluginWidget']]
    for modloader, modname, ispkg in widg_mods:
        p_widgets.append(modname)
    return p_widgets

plugin_widget_list = load_plugin_widgets(__path__)

def get_widget(plugin_widget_name):
    # assume plugin widget class has same name as module 
    impmod = importlib.import_module('.'+plugin_widget_name,__name__)
    widg = getattr(impmod,plugin_widget_name)
    return widg()

def default_plugin_widget(plugin_type):
    w = QtGui.QTextEdit()
    w.setText('default plugin widget: '\
    'plugin {} does not have a graphical widget '\
    'associated with it.'.format(plugin_type))
    return w


