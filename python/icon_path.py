import os
import sys

def _absolute_path(filename):
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    return os.path.join(base_dir, "icons", filename)

def icon_path(name):
    # menu icons
    if name == "open":
        return _absolute_path("document-open-2.gif")
    if name == "scan":
        return _absolute_path("database-gear.gif")
    if name == "import":
        return _absolute_path("database-add.gif")
    if name == "select_all":
        return _absolute_path("plus_blue.gif")

    # ignore filters
    if name == "ignore_hashes_in_range":
        return _absolute_path("plus_blue.gif")
    if name == "ignore_selected_hash":
        return _absolute_path("plus_blue.gif")
    if name == "ignore_sources_with_hashes_in_range":
        return _absolute_path("plus_blue.gif")
    if name == "ignore_sources_with_selected_hash":
        return _absolute_path("plus_blue.gif")
    if name == "clear_ignored_hashes":
        return _absolute_path("minus_blue.gif")
    if name == "clear_ignored_sources":
        return _absolute_path("minus_blue.gif")

    # highlight filters
    if name == "highlight_hashes_in_range":
        return _absolute_path("plus_blue.gif")
    if name == "highlight_selected_hash":
        return _absolute_path("plus_blue.gif")
    if name == "highlight_sources_with_hashes_in_range":
        return _absolute_path("plus_blue.gif")
    if name == "highlight_sources_with_selected_hash":
        return _absolute_path("plus_blue.gif")
    if name == "clear_highlighted_hashes":
        return _absolute_path("minus_blue.gif")
    if name == "clear_highlighted_sources":
        return _absolute_path("minus_blue.gif")

    # histogram bar control
    if name == "fit_image":
        return _absolute_path("zoom-original-2.gif")
    if name == "fit_range":
        return _absolute_path("zoom-in-3.gif")
    if name == "show_hex_view":
        return _absolute_path("text-x-hex.gif")
    if name == "view_annotations":
        return _absolute_path("table-go.gif")

    # histogram y view control
    if name == "y_plus":
        return _absolute_path("plus_blue.gif")
    if name == "y_minus":
        return _absolute_path("minus_blue.gif")

