import os
import sys

def _absolute_path(filename):
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    return os.path.join(base_dir, "icons", filename)

def icon_path(name):
    if name == "open":
        return _absolute_path("document-open-2.gif")
    if name == "scan":
        return _absolute_path("database-gear.gif")
    if name == "import":
        return _absolute_path("database-add.gif")
    if name == "select_all":
        return _absolute_path("plus_blue.gif")
    if name == "clear_all":
        return _absolute_path("minus_blue.gif")
    if name == "add_hash":
        return _absolute_path("plus_blue.gif")
    if name == "remove_hash":
        return _absolute_path("minus_blue.gif")
    if name == "pan":
#        return _absolute_path("draw-arrow-forward.gif")
        return _absolute_path("arrow_plain_blue_E_W.gif")
    if name == "fit_range":
        return _absolute_path("zoom-in-3.gif")
    if name == "fit_image":
        return _absolute_path("zoom-original-2.gif")
    if name == "filter_range":
        return _absolute_path("bullet-green.gif")
    if name == "filter_all_but_range":
        return _absolute_path("bullet-red.gif")
    if name == "deselect_range":
        return _absolute_path("list-remove-3.gif")

