import tkinter 
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip

class SourcesView():
    """Manages the view for the list of matched sources.

    The text view:
      The first row is the column annotation.  It is non-selectable
        with a gray background.
      The remaining rows are Sectors, alternating colors.
      Sector columns are tab-spaced and contain:
        Sector ID, %match, #match, file size, repository name, filename.
      Mouse motion events change the Source row background color.
      Mouse click events toggle sector filtering for that sector ID.
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
#        FILTERED = "#99cc00"
        FILTERED = "#006633"
        UNFILTERED = "#990000"
        ID_FOREGROUND = "white"

        # variables
        self._identified_data = identified_data
        self._filters = filters

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the title
        tkinter.Label(self.frame, text='Matched Sources') \
                                            .pack(side=tkinter.TOP)

        # add the color legend
        f = tkinter.Frame(self.frame)
        f.pack(side=tkinter.TOP)
        tkinter.Label(f,text="   ",background=FILTERED).pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background=UNFILTERED).pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Not filtered      ").pack(side=tkinter.LEFT)

        # add the select all and clear all buttons
        select_clear_frame = tkinter.Frame(self.frame)
        select_clear_frame.pack(pady=8)

        # select button
        self._select_all_icon = tkinter.PhotoImage(file=icon_path("select_all"))
        select_all_button = tkinter.Button(select_clear_frame,
                       image=self._select_all_icon,
                       command=self._handle_set_all_sources)
        select_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(select_all_button, "Filter all sources")

        # clear button
        self._clear_all_icon = tkinter.PhotoImage(file=icon_path("clear_all"))
        clear_all_button = tkinter.Button(select_clear_frame,
                       image=self._clear_all_icon,
                       command=self._handle_clear_all_sources)
        clear_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(clear_all_button, "Do not filter any sources")

        # scrolled frame for sources
        scrolled_text = ScrolledText(self.frame, width=60, height=16)
        scrolled_text.scroll_frame.pack(side=tkinter.TOP)

        # the text widget for the source view
        self._source_text = scrolled_text.text

        # text widget tab and tag settings
        self._source_text.config(tabs=('1.0c', '1.6c', tkinter.NUMERIC, '2.9c',
                                                '4.5c', '6.8c', '11c'))
        self._source_text.tag_config("title", background="gray90")
        self._source_text.tag_config("even", background="white")
        self._source_text.tag_config("odd", background="light blue")
        self._source_text.tag_config("hovered", background="cornflower blue")
        self._source_text.tag_config("unfiltered", background=UNFILTERED, foreground=ID_FOREGROUND)
        self._source_text.tag_config("filtered", background=FILTERED, foreground=ID_FOREGROUND)
#        self._source_text.tag_config("unfiltered", background="red")
#        self._source_text.tag_config("filtered", background="green")
#        self._source_text.tag_config("unfiltered", background="#660000", foreground="white")
#        self._source_text.tag_config("filtered", background="#004400", foreground="white")

        # set initial state
        self._fill_source_view()

        # register to receive identified data change events
        filters.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

    def _fill_source_view(self):

        # optimization: make local references to filter variables
        max_hashes = self._filters.max_hashes
        filter_flagged_blocks = self._filters.filter_flagged_blocks
        filtered_sources = self._filters.filtered_sources
        filtered_hashes = self._filters.filtered_hashes

        # sources_offsets = dict<source ID, set<source offset int>>
        sources_offsets = defaultdict(set)

        # find each offset of each sector that is not filtered out
        for block_hash, sources in self._identified_data.hashes.items():

            # count exceeds max_hashes
            if max_hashes != 0 and len(sources) > max_hashes:
                continue

            # hash is filtered
            if block_hash in filtered_hashes:
                filter_count = len(sources)
                continue

            # a source is flagged or a source is marked
            for source in sources:
                if filter_flagged_blocks and "label" in source:
                    # source has a label flag
                    continue
                if source["source_id"] in filtered_sources:
                    # the source itself is filtered
                    continue

                # set the offset for the source
                sources_offsets[source["source_id"]].add(source["file_offset"])

        # set editable
        self._source_text.config(state=tkinter.NORMAL)

        # clear any existing text
        self._source_text.delete(1.0, tkinter.END)

        # put in the first row containing the column titles
        self._source_text.insert(tkinter.END,
                                 "ID\t\t%Match\t#Match\tSize\t"
                                 "Repository Name\tFilename\n",
                                 "title")

        # put in source rows
        row = 0
        for source_id, source in self._identified_data.source_details.items():

             # get the filter tag name based on source ID
             if source["source_id"] in filtered_sources:
                 filter_tag = "filtered"
             else:
                 filter_tag = "unfiltered"

             # put in the source ID
             self._source_text.insert(tkinter.END, "%s\t"%source_id, filter_tag)

             # get the row tag name based on row placement
             if row % 2 == 0:
                 row_tag = "even"
             else:
                 row_tag = "odd"
             row += 1

             # change row tag to hovered if hovering
             #zzzzzzzzzzzz

             # handle missing fields, which can happen if an image was
             # imported instead of a directory of files
             if "filesize" in source:

                 # calculate percent of this source file found
                 percent_found = len(sources_offsets[source_id]) / \
                                 (int(source["filesize"] / 
                                 self._identified_data.sector_size)) * \
                                 100

#        Sector ID, %match, #match, file size, repository name, filename.
                 source_attributes = '\t%.2f%%\t%d\t%d\t%s\t%s\n' \
                                    %(percent_found,
                                      len(sources_offsets[source_id]),
                                      source["filesize"],
                                      source["repository_name"],
                                      source["filename"])

             else:
                 source_attributes = '\t%.2f%%\t?%d\t?\t%s\t%s\n' \
                                    %(len(sources_offsets[source_id]),
                                      source["repository_name"],
                                      source["filename"])
             self._source_text.insert(tkinter.END, source_attributes, row_tag)
 
        # set not editable
        self._source_text.config(state=tkinter.DISABLED)

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

    def _handle_text_selection(self, *args):
        # adjust filter for sources
        # zzzzzzzzz

        # signal change
        self._filters.fire_change()

    def _handle_identified_data_change(self, *args):
        self._fill_source_view()

    def _handle_filter_change(self, *args):
        self._fill_source_view()

