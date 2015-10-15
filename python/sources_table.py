from sys import platform
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip
from selection_tools import sources_in_range
import colors
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class SourcesTable():
    """Provides the table view of the sources.

    The text view:
      The first line contains the column annotation.  It is non-selectable
        with a gray background.
      The remaining lines are sources, alternating colors.
      Source columns are tab-spaced and contain:
        range selection indicator,
        offset selection indicator,
        Source ID,
        %match, #match, file size, repository name, filename.
      Mouse motion events change the Source line background hover color.
      Mouse left click events toggle source highlighting for that source ID.
      Mouse right click events toggle source ignoring for that source ID.
      The color for the Source data depends on the filtering mode:
        "normal":      gray
        "ignored":     red
        "highlighted": green
        "ignored_and_highlighted": teal
      This color is further modified by line index or cursor over:
        even index: lighter
        odd index:  darker
        hover:      much darker, with white foreground
      The color for the source ID depends on the range selection.
        If the source is selected, the source ID is shown as blue.
        If the source is not selected, the source ID color is the same
        as the color for the source data.

    Attributes:
      frame(Frame): the containing frame for this sources table.
      _source_text(Text): The Text widget to render sources in.
    """

    def __init__(self, master, identified_data, filters, range_selection,
                                                       width=40, height=12):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): Filters that impact the view.
          range_selection(RangeSelection): The selected range.
          width, height(int): size in characters of table.
        """

        # variables
        self._identified_data = identified_data
        self._filters = filters
        self._range_selection = range_selection

        # state
        self._line_to_id = {}
        self._selected_source_ids = set()

        # cursor line or -1
        self._cursor_line = -1

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # scrolled frame for sources
        scrolled_text = ScrolledText(self.frame, width=width, height=height)
        scrolled_text.scroll_frame.pack(side=tkinter.TOP)

        # the source text to contain the table
        self._source_text = scrolled_text.text

        # text widget tab settng
        self._source_text.config(tabs=(
                     '1.1c', tkinter.RIGHT,       # ID
                     '1.9c', tkinter.NUMERIC,     # %match
                     '4.1c', tkinter.RIGHT,       # #match
                     '6.2c', tkinter.RIGHT,       # filesize
                     '6.7c',                      # repository name
                     '10.7c'))                    # filename

        # text widget cursor setting
        self._source_text.config(cursor="arrow")

        # text widget mouse events
        self._source_text.bind('<Any-Motion>', self._handle_mouse_move,
                                                                    add='+')
        self._source_text.bind('<Button-1>', self._handle_b1_mouse_press,
                                                                    add='+')
        self._source_text.bind('<Enter>', self._handle_enter, add='+')
        self._source_text.bind('<Leave>', self._handle_leave, add='+')
        if platform == 'darwin':
            # mac right-click is Button-2
            self._source_text.bind('<Button-2>', self._handle_b3_mouse_press,
                                                                    add='+')
        else:
            # Linux, Win right-click is Button-3
            self._source_text.bind('<Button-3>', self._handle_b3_mouse_press,
                                                                    add='+')

        # register to receive identified data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set initial state data
        self._set_data()

    def _set_data(self):
        """Set the view to show the sources in identified_dta.source_details"""

        # initialize the line and ID lookup dictionaries
        self._line_to_id.clear()

        # set editable
        self._source_text.config(state=tkinter.NORMAL)

        # clear any existing text
        self._source_text.delete(1.0, tkinter.END)

        # delete any existing tags
        self._source_text.tag_delete(self._source_text.tag_names())

        # create the title tag
        self._source_text.tag_config("title", background=colors.TITLE)

        # put in the first line containing the column titles
        self._source_text.insert(tkinter.END,
                                 "\tID\t"
                                 "%Match\t#Match\tSize\t"
                                 "Repository Name\tFilename\n",
                                 "title")

        # local references to identified_data
        source_details = self._identified_data.source_details
        sector_size = self._identified_data.sector_size
        sources_offsets = self._identified_data.sources_offsets

        # put in source lines
        line = 2
        for source_id, source in source_details.items():

            # compose the source text
            # handle missing fields, which can happen if an image was
            # imported, instead of a directory of files
            if "filesize" in source:

                # calculate percent of this source file found
                percent_found = len(sources_offsets[source_id]) / \
                               (int(source["filesize"] / sector_size)) * 100

                source_text = '\t%.2f%%\t%d\t%d\t%s\t%s\n' \
                                    %(percent_found,
                                      len(sources_offsets[source_id]),
                                      source["filesize"],
                                      source["repository_name"],
                                      source["filename"])

            else:
                source_text = '\t?\t%d\t?\t%s\t%s\n' \
                                    %(len(sources_offsets[source_id]),
                                      source["repository_name"],
                                      source["filename"])

            # compose the tag names
            id_tag_name = "id_line_%s" % line
            data_tag_name = "data_line_%s" % line

            # add the source ID and data text
            self._source_text.insert(tkinter.END, "\t%s" % source_id,
                                                                 id_tag_name)
            self._source_text.insert(tkinter.END, source_text, data_tag_name)

            # record the line to ID lookup
            self._line_to_id[line] = source_id

            # next line
            line += 1
 
        # set not editable
        self._source_text.config(state=tkinter.DISABLED)

        # set colors for the source lines
        self._set_colors()

    def _set_colors(self):
        # set the color for each source line
        for line in range(2, 2+len(self._identified_data.source_details)):
            self._set_line_color(line)

    def _set_line_color(self, line):
        # compose the tag names
        id_tag_name = "id_line_%s" % line
        data_tag_name = "data_line_%s" % line

        # get the source ID
        source_id = self._line_to_id[line]

        # get the source color
        (foreground, background) = self._source_color(line, source_id)

        # set the id tag color
        self._source_text.tag_config(id_tag_name, background=background,
                                                  foreground=foreground)

        # set the data tag color
        if source_id in self._selected_source_ids and line != self._cursor_line:
            # use range selection color for the data portion
            self._source_text.tag_config(data_tag_name,
                                        background=colors.IN_RANGE_BACKGROUND,
                                        foreground=colors.IN_RANGE_FOREGROUND)

        else:
            # use id colors for the data color
            self._source_text.tag_config(data_tag_name,
                                 background=background, foreground=foreground)


    def _source_color(self, line, source_id):
        # return foreground, background tuple depending on filtering
        # and alternating line coloration
        if source_id in self._filters.ignored_sources and \
                    source_id in self._filters.highlighted_sources:
            # use IGNORED_AND_HIGHLIGHTED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = colors.HOVERED_IGNORED_AND_HIGHLIGHTED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = colors.EVEN_IGNORED_AND_HIGHLIGHTED
                else:
                    background = colors.ODD_IGNORED_AND_HIGHLIGHTED
        elif source_id in self._filters.ignored_sources:
            # use IGNORED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = colors.HOVERED_IGNORED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = colors.EVEN_IGNORED
                else:
                    background = colors.ODD_IGNORED
        elif source_id in self._filters.highlighted_sources:
            # use HIGHLIGHTED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = colors.HOVERED_HIGHLIGHTED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = colors.EVEN_HIGHLIGHTED
                else:
                    background = colors.ODD_HIGHLIGHTED
        else:
            # use NORMAL color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = colors.HOVERED_NORMAL
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = colors.EVEN_NORMAL
                else:
                    background = colors.ODD_NORMAL

        # return color
        return (foreground, background)

    def _mouse_to_line(self, e):
        index = self._source_text.index("@%s,%s" % (e.x, e.y))
        line,_ = index.split('.')
        return int(line)

    def _handle_mouse_move(self, e):
        line = self._mouse_to_line(e)

        # no action
        if line == self._cursor_line:
            return

        # restore old cursor line
        old_cursor_line = self._cursor_line
        if old_cursor_line != -1:
            self._cursor_line = -1
            self._set_line_color(old_cursor_line)

        # set new cursor line if the line is in bounds
        if line in self._line_to_id:
            self._cursor_line = line
            self._set_line_color(line)

    # highlight this source
    def _handle_b1_mouse_press(self, e):
        line = self._mouse_to_line(e)

        # line must be in bounds
        if line not in self._line_to_id:
            return

        # toggle filter state for source
        source_id = self._line_to_id[line]
        if source_id in self._filters.highlighted_sources:
            self._filters.highlighted_sources.remove(source_id)
        else:
            self._filters.highlighted_sources.add(source_id)

        # fire change
        self._filters.fire_change()

    # ignore this source
    def _handle_b3_mouse_press(self, e):
        line = self._mouse_to_line(e)

        # line must be in bounds
        if line not in self._line_to_id:
            return

        # toggle filter state for source
        source_id = self._line_to_id[line]
        if source_id in self._filters.ignored_sources:
            self._filters.ignored_sources.remove(source_id)
        else:
            self._filters.ignored_sources.add(source_id)

        # fire change
        self._filters.fire_change()

    def _handle_enter(self, e):
        self._handle_mouse_move(e)

    def _handle_leave(self, e):
        # restore old cursor line
        if self._cursor_line != -1:
            old_cursor_line = self._cursor_line
            self._cursor_line = -1
            self._set_line_color(old_cursor_line)

    def _handle_identified_data_change(self, *args):
        self._set_data()

    def _handle_filter_change(self, *args):
        self._set_colors()

    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            # get source IDs in range
            self._selected_source_ids = sources_in_range(self._identified_data,
                                          self._range_selection.start_offset,
                                          self._range_selection.stop_offset)

        else:
            # unmark source IDs
            self._selected_source_ids = set()

        # set source ID colors
        self._set_colors()

