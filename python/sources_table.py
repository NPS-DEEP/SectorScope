from sys import platform
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip
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
      The background color for the Source ID depends on the filtering mode:
        "normal":      gray
        "ignored":     red
        "highlighted": green
        "ignored_and_highlighted": teal
      The background shade is further modified by line index or cursor over:
        even index: lighter
        odd index:  darker
        hover:      much darker, with white foreground

    Attributes:
      frame(Frame): the containing frame for this sources table.
      _source_text(Text): The Text widget to render sources in.
    """

    def __init__(self, master, identified_data, filters, offset_selection,
                 range_selection, width=40, height=12):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
          width, height(int): size in characters of table.
        """

        # RGB colors
        self.TITLE = "gray90"

        self.EVEN_NORMAL = "#f8f8f8"
        self.ODD_NORMAL = "#eeeeee"
        self.HOVERED_NORMAL = "#aaaaaa"

        self.EVEN_IGNORED = "#ffdddd"
        self.ODD_IGNORED = "#ffcccc"
        self.HOVERED_IGNORED = "#990000"

        self.EVEN_HIGHLIGHTED = "#ccffcc"
        self.ODD_HIGHLIGHTED = "#aaffaa"
        self.HOVERED_HIGHLIGHTED = "#006633"

        self.EVEN_IGNORED_AND_HIGHLIGHTED = "#bbffff"
        self.ODD_IGNORED_AND_HIGHLIGHTED = "#99ffff"
        self.HOVERED_IGNORED_AND_HIGHLIGHTED = "#008888"

        # variables
        self._identified_data = identified_data
        self._filters = filters

        # state
        self._line_to_id = {}
        self._id_to_line = {}

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
                     '0.5c', tkinter.CENTER,      # range indicator
                     '1.0c', tkinter.CENTER,      # selection indicator
                     '2.0c', tkinter.RIGHT,       # ID
                     '2.8c', tkinter.NUMERIC,     # %match
                     '5.0c', tkinter.RIGHT,       # #match
                     '7.1c', tkinter.RIGHT,       # filesize
                     '7.6c',                      # repository name
                     '11.6c'))                    # filename

        # text widget cursor setting
        self._source_text.config(cursor="arrow")

        # text widget mouse events
        self._source_text.bind('<Any-Motion>', self._handle_mouse_move,
                                                                    add='+')
        self._source_text.bind('<Button-1>', self._handle_b1_mouse_press,
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

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_offset_selection_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set initial state
        self._set_data()

    def _set_data(self):
        """Set the view to show the sources in identified_dta.source_details"""

        # initialize the line and ID lookup dictionaries
        self._line_to_id.clear()
        self._id_to_line.clear()

        # set editable
        self._source_text.config(state=tkinter.NORMAL)

        # clear any existing text
        self._source_text.delete(1.0, tkinter.END)

        # delete any existing tags
        self._source_text.tag_delete(self._source_text.tag_names())

        # put in the title tag
        self._source_text.tag_config("title", background=self.TITLE)

        # put in the first line containing the column titles
        self._source_text.insert(tkinter.END,
                                 "\tR\u2713\tO\u2714\tID\t"
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

            # set the tag for the source text
            self._set_tag(line, source_id)

            # compose the source text
            # handle missing fields, which can happen if an image was
            # imported, instead of a directory of files
            if "filesize" in source:

                # calculate percent of this source file found
                percent_found = len(sources_offsets[source_id]) / \
                               (int(source["filesize"] / sector_size)) * 100

                source_text = '\t \t \t%s\t%.2f%%\t%d\t%d\t%s\t%s\n' \
                                    %(source_id,
                                      percent_found,
                                      len(sources_offsets[source_id]),
                                      source["filesize"],
                                      source["repository_name"],
                                      source["filename"])

            else:
                source_text = '\t \t \t%s\t%.2f%%\t?%d\t?\t%s\t%s\n' \
                                    %(source_id,
                                      len(sources_offsets[source_id]),
                                      source["repository_name"],
                                      source["filename"])

            # add the source text
            tag_name = "line_%s" % line
            self._source_text.insert(tkinter.END, source_text, tag_name)

            # record the line and ID lookups
            self._line_to_id[line] = source_id
            self._id_to_line[source_id] = line

            # next line
            line += 1
 
        # set not editable
        self._source_text.config(state=tkinter.DISABLED)

    def _set_tag(self, line, source_id):
        # create the tag name for the line
        tag_name = "line_%s" % line

        # determine the background color
        if source_id in self._filters.ignored_sources and \
                    source_id in self._filters.highlighted_sources:
            # use IGNORED_AND_HIGHLIGHTED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = self.HOVERED_IGNORED_AND_HIGHLIGHTED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = self.EVEN_IGNORED_AND_HIGHLIGHTED
                else:
                    background = self.ODD_IGNORED_AND_HIGHLIGHTED
        elif source_id in self._filters.ignored_sources:
            # use IGNORED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = self.HOVERED_IGNORED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = self.EVEN_IGNORED
                else:
                    background = self.ODD_IGNORED
        elif source_id in self._filters.highlighted_sources:
            # use HIGHLIGHTED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = self.HOVERED_HIGHLIGHTED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = self.EVEN_HIGHLIGHTED
                else:
                    background = self.ODD_HIGHLIGHTED
        else:
            # use NORMAL color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = self.HOVERED_NORMAL
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = self.EVEN_NORMAL
                else:
                    background = self.ODD_NORMAL

        # create or modify the tag
        self._source_text.tag_config(tag_name, background=background,
                                               foreground=foreground)

    def _set_tags(self):
        for line, source_id in self._line_to_id.items():
            self._set_tag(line, source_id)

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
            self._set_tag(old_cursor_line, self._line_to_id[old_cursor_line])

        # set new cursor line if the line is in bounds
        if line in self._line_to_id:
            self._cursor_line = line
            self._set_tag(line, self._line_to_id[line])

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
            self._set_tag(old_cursor_line, self._line_to_id[old_cursor_line])

    def _handle_identified_data_change(self, *args):
        self._set_data()

    def _handle_filter_change(self, *args):
        self._set_tags()

    def _handle_offset_selection_change(self, *args):
        print("offset selection")

    def _handle_range_selection_change(self, *args):
        print("range selection")

    def _handle_fit_range_selection_change(self, *args):
        print("fit range selection")

