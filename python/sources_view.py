import tkinter 
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip

class SourcesView():
    """Manages the view for the list of matched sources.

    The text view:
      The first line contains the column annotation.  It is non-selectable
        with a gray background.
      The remaining lines are sources, alternating colors.
      Source columns are tab-spaced and contain:
        Source ID, %match, #match, file size, repository name, filename.
      Mouse motion events change the Source line background color.
      Mouse click events toggle source filtering for that source ID.
      The background for the Source ID is red or green based on filter.

    Attributes:
      frame(Frame): the containing frame for this view.
      _source_text(Text): The Text widget to render sources in.
    """

    def __init__(self, master, identified_data, filters):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): The filters that controll the view.
        """

        # colors
        self.TITLE = "gray90"
        self.FILTERED = "#006633"
        self.UNFILTERED = "#990000"
        self.ID_FOREGROUND = "white"
        self.EVEN = "white"
        self.ODD = "light blue"
        self.HOVERED = "cornflower blue"

        # variables
        self._identified_data = identified_data
        self._filters = filters

        # cursor line or -1
        self._cursor_line = -1

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the title
        tkinter.Label(self.frame, text='Matched Sources') \
                                            .pack(side=tkinter.TOP)

        # add the color legend
        f = tkinter.Frame(self.frame)
        f.pack(side=tkinter.TOP)
        tkinter.Label(f,text="   ",background=self.UNFILTERED).pack(
                                                         side=tkinter.LEFT)
        tkinter.Label(f,text="Not filtered      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background=self.FILTERED).pack(
                                                         side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered      ").pack(side=tkinter.LEFT)

        # add the select all and clear all buttons
        select_clear_frame = tkinter.Frame(self.frame)
        select_clear_frame.pack(pady=8)

        # clear button
        self._clear_all_icon = tkinter.PhotoImage(file=icon_path("clear_all"))
        clear_all_button = tkinter.Button(select_clear_frame,
                       image=self._clear_all_icon,
                       command=self._handle_clear_all_sources)
        clear_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(clear_all_button, "Do not filter any sources")

        # select button
        self._select_all_icon = tkinter.PhotoImage(file=icon_path("select_all"))
        select_all_button = tkinter.Button(select_clear_frame,
                       image=self._select_all_icon,
                       command=self._handle_set_all_sources)
        select_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(select_all_button, "Filter all sources")

        # scrolled frame for sources
        scrolled_text = ScrolledText(self.frame, width=60, height=60)
        scrolled_text.scroll_frame.pack(side=tkinter.TOP)

        # the text widget for the source view
        self._source_text = scrolled_text.text

        # text widget tab settng
        self._source_text.config(tabs=('1.0c', tkinter.RIGHT,
                                       '1.8c', tkinter.NUMERIC,
                                       '4.0c', tkinter.RIGHT,
                                       '6.1c', tkinter.RIGHT,
                                       '6.6c',
                                       '10.6c'))

        # text widget cursor setting
        self._source_text.config(cursor="arrow")

        # text widget mouse events
        self._source_text.bind('<Any-Motion>', self._handle_mouse_move)
        self._source_text.bind('<Button-1>', self._handle_b1_mouse_press)
        self._source_text.bind('<Enter>', self._handle_enter)
        self._source_text.bind('<Leave>', self._handle_leave)

        # set initial state
        self._fill_source_view()

        # register to receive identified data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

    def _get_sources_offsets(self):
        # sources_offsets = dict<source ID, set<source offset int>>
        sources_offsets = defaultdict(set)

        # identify source offsets of every source of every matching hash
        for _, sources in self._identified_data.hashes.items():
            for source in sources:

                # set the offset for the source
                sources_offsets[source["source_id"]].add(source["file_offset"])

        return sources_offsets

    def _fill_source_view(self):

        # initialize the line and ID lookup dictionaries
        self._line_to_id = {}
        self._id_to_line = {}

        # set editable
        self._source_text.config(state=tkinter.NORMAL)

        # clear any existing text
        self._source_text.delete(1.0, tkinter.END)

        # delete any existing tags
        self._source_text.tag_delete(self._source_text.tag_names())

        # put in hardcoded tags
        self._source_text.tag_config("title", background=self.TITLE)
        self._source_text.tag_config("hovered", background="cornflower blue")

        # put in the first line containing the column titles
        self._source_text.insert(tkinter.END,
                                 "\tID\t%Match\t#Match\tSize\t"
                                 "Repository Name\tFilename\n",
                                 "title")

        # get offsets for sources
        sources_offsets = self._get_sources_offsets()

        # local reference to filtered sources
        filtered_sources = self._filters.filtered_sources

        # put in source lines
        line = 2
        for source_id, source in self._identified_data.source_details.items():

            # set the background for the source ID
            self._set_id_background(line, source_id)

            # add the source ID text
            id_tag_name = "id%s" % line
            self._source_text.insert(tkinter.END, "\t%s"%source_id,
                                     id_tag_name)

            # set the background for the source data
            self._set_data_background(line)

            # add the data text
            # handle missing fields, which can happen if an image was
            # imported instead of a directory of files
            if "filesize" in source:

                # calculate percent of this source file found
                percent_found = len(sources_offsets[source_id]) / \
                                 (int(source["filesize"] / 
                                 self._identified_data.sector_size)) * \
                                 100

                data = '\t%.2f%%\t%d\t%d\t%s\t%s\n' \
                                    %(percent_found,
                                      len(sources_offsets[source_id]),
                                      source["filesize"],
                                      source["repository_name"],
                                      source["filename"])

            else:
                data = '\t%.2f%%\t?%d\t?\t%s\t%s\n' \
                                    %(len(sources_offsets[source_id]),
                                      source["repository_name"],
                                      source["filename"])

            # add the source data text
            data_tag_name = "data%s" % line
            self._source_text.insert(tkinter.END, data, data_tag_name)

            # record the line and ID lookups
            self._line_to_id[line] = source_id
            self._id_to_line[source_id] = line

            # next line
            line += 1
 
        # set not editable
        self._source_text.config(state=tkinter.DISABLED)

    def _set_id_background(self, line, source_id):
        # create the ID tag name for the line
        id_tag_name = "id%s" % line

        # get the filter color
        if source_id in self._filters.filtered_sources:
            color = self.FILTERED
        else:
            color = self.UNFILTERED

        # set the color for the ID tag
        self._source_text.tag_config(id_tag_name, background=color,
                                     foreground=self.ID_FOREGROUND)

    def _set_data_background(self, line):
        # create the data tag name for the line
        data_tag_name = "data%s" % line

        # get the line color for the data
        if line % 2 == 0:
            color = self.EVEN
        else:
            color = self.ODD

        # set the color for the data tag
        self._source_text.tag_config(data_tag_name, background=color)

    def _set_hover_background(self, line):
        # create the data tag name for the line
        data_tag_name = "data%s" % line

        # set the color for the data tag
        self._source_text.tag_config(data_tag_name, background=self.HOVERED)


    def _set_id_tags(self):
        for line, source_id in self._line_to_id.items():
            self._set_id_background(line, source_id)

    def _mouse_to_line(self, e):
        index = self._source_text.index("@%s,%s" % (e.x, e.y))
        line,_ = index.split('.')
        return int(line)

    def _handle_clear_all_sources(self, *args):
        # clear filtered sources and signal change
        self._filters.filtered_sources.clear()
        self._filters.fire_change()

    def _handle_set_all_sources(self, *args):
        # set filtered sources and signal change
        self._filters.filtered_sources.clear()
        for source_id in self._identified_data.source_details:
            self._filters.filtered_sources.append(source_id)
        self._filters.fire_change()

    def _handle_identified_data_change(self, *args):
        self._fill_source_view()

    def _handle_filter_change(self, *args):
        self._set_id_tags()

    def _handle_mouse_move(self, e):
        line = self._mouse_to_line(e)

        # no action
        if line == self._cursor_line:
            return

        # restore old cursor line
        self._set_data_background(self._cursor_line)
        self._cursor_line = -1

        # set new cursor line
        if line != -1:
            self._set_hover_background(line)
            self._cursor_line = line

    def _handle_b1_mouse_press(self, e):
        line = self._mouse_to_line(e)
        if line == -1:
            return

        # toggle filter state for source
        source_id = self._line_to_id[line]
        if source_id in self._filters.filtered_sources:
            self._filters.filtered_sources.remove(source_id)
        else:
            self._filters.filtered_sources.append(source_id)

        # fire change
        self._filters.fire_change()

    def _handle_enter(self, e):
        self._handle_mouse_move(e)

    def _handle_leave(self, e):
        # restore old cursor line
        if self._cursor_line != -1:
            self._set_data_background(self._cursor_line)
            self._cursor_line = -1

