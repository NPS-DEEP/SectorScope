import os
import sys

def _absolute_path(filename):
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    return os.path.join(base_dir, "icons", filename)

def icon_path(name):
    if name == "open":
        return _absolute_path("document-open-2.gif")
    if name == "scan":
        return _absolute_path("database-go.gif")
    if name == "import":
        return _absolute_path("db_add.gif")
    if name == "select_all":
        return _absolute_path("plus_blue.gif")
    if name == "clear_all":
        return _absolute_path("minus_blue.gif")
    if name == "add_hash":
        return _absolute_path("plus_blue.gif")
    if name == "remove_hash":
        return _absolute_path("minus_blue.gif")

