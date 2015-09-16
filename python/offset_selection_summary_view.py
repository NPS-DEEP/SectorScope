import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection
from histogram_bar import HistogramBar
from image_hex_window import ImageHexWindow

class OffsetSelectionSummaryView():
    """Provides a summary and controls for the selected offset.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters, offset_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
        """

        # data variables
        self._identified_data = identified_data
        self._filters = filters
        self._offset_selection = offset_selection

        # make the containing frame
        self.frame = tkinter.Frame(master)

#        # add the title
#        tkinter.Label(self.frame, text="Selected Offset:").pack(
#                                                 side=tkinter.LEFT, padx=20)

        # add the selection frame
        selection_frame = tkinter.Frame(self.frame)
        selection_frame.pack(side=tkinter.LEFT, anchor="w")

        # add the selected image byte offset label
        self._selected_image_offset_label = tkinter.Label(selection_frame,
                                    anchor=tkinter.W)
        self._selected_image_offset_label.pack(side=tkinter.TOP, anchor="w",
                                                             fill=tkinter.X)

        # add the selected image byte offset hash label
        self._selected_image_offset_hash_label = tkinter.Label(selection_frame,
                                                    anchor="w", width=55)
        self._selected_image_offset_hash_label.pack(side=tkinter.TOP,
                                                    anchor="w", fill=tkinter.X)

        # add the controls frame
        controls_frame = tkinter.Frame(self.frame)
        controls_frame.pack(side=tkinter.LEFT)

        # button to add hash
        self._add_hash_icon = tkinter.PhotoImage(file=icon_path("add_hash"))
        self._add_hash_button = tkinter.Button(controls_frame,
                                image=self._add_hash_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_add_hash_to_filter)
        self._add_hash_button.pack(side=tkinter.LEFT, padx=(0,0))
        Tooltip(self._add_hash_button, "Filter the selected hash")

        # button to remove hash
        self._remove_hash_icon = tkinter.PhotoImage(file=icon_path(
                                                              "remove_hash"))
        self._remove_hash_button = tkinter.Button(controls_frame,
                                image=self._remove_hash_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_remove_hash_from_filter)
        self._remove_hash_button.pack(side=tkinter.LEFT)
        Tooltip(self._remove_hash_button, "Stop filtering the selected hash")

        # button to show hex view
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        self._show_hex_view_button = tkinter.Button(controls_frame,
                                image=self._show_hex_view_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_show_hex_view)
        self._show_hex_view_button.pack(side=tkinter.LEFT, padx=8)
        Tooltip(self._show_hex_view_button, "Show hex view of selection")

        # button to deselect offset selection
        self._deselect_offset_selection_icon = tkinter.PhotoImage(
                                file=icon_path( "deselect_offset_selection"))
        self._deselect_offset_selection_button = tkinter.Button(controls_frame,
                                image=self._deselect_offset_selection_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_deselect_offset_selection)
        self._deselect_offset_selection_button.pack(side=tkinter.LEFT)
        Tooltip(self._deselect_offset_selection_button,
                                             "Deselect the selection")

        # create the image hex window that the show hex view button can show
        self._image_hex_window = ImageHexWindow(self.frame, identified_data,
                                                filters, offset_selection)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_offset_selection_change)

    def _handle_filter_change(self, *args):
        self._set_add_and_remove_button_states()

    def _handle_offset_selection_change(self, *args):
        self._set_add_and_remove_button_states()

        # set the selected image offset and its associated hash value
        if self._offset_selection.offset == -1:
            # clear
            self._selected_image_offset_label['text'] = \
                               "Selected offset: Not selected"
            self._selected_image_offset_hash_label['text'] = \
                               "MD5 at offset: Not selected"

        else:
            # set to selection
            self._selected_image_offset_label["text"] = \
                                       "Selected offset: %s" % offset_string(
                                       self._offset_selection.offset)
            self._selected_image_offset_hash_label["text"] = \
                 "MD5 at offset: %s" % self._offset_selection.block_hash

        # enable or disable buttons that use an offset selection
        if self._offset_selection.offset == -1:
            self._show_hex_view_button.config(state=tkinter.DISABLED)
            self._deselect_offset_selection_button.config(
                                              state=tkinter.DISABLED)
        else:
            self._show_hex_view_button.config(state=tkinter.NORMAL)
            self._deselect_offset_selection_button.config(
                                              state=tkinter.NORMAL)

    def _set_add_and_remove_button_states(self):
        # disable both if there is no active selection
        if self._offset_selection.offset == -1:
            self._add_hash_button.config(state=tkinter.DISABLED)
            self._remove_hash_button.config(state=tkinter.DISABLED)
            return

        # reference to selected hash
        selected_hash = self._offset_selection.block_hash

        # set enabled state of the add hash button
        if selected_hash not in self._filters.filtered_hashes and \
                           selected_hash in self._identified_data.hashes:
            self._add_hash_button.config(state=tkinter.NORMAL)
        else:
            self._add_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the remove hash button
        if selected_hash in self._filters.filtered_hashes:
            self._remove_hash_button.config(state=tkinter.NORMAL)
        else:
            self._remove_hash_button.config(state=tkinter.DISABLED)

    # button changes filter
    def _handle_add_hash_to_filter(self):
        self._filters.filtered_hashes.add(self._offset_selection.block_hash)
        self._filters.fire_change()

    # button changes filter
    def _handle_remove_hash_from_filter(self):
        self._filters.filtered_hashes.remove(self._offset_selection.block_hash)
        self._filters.fire_change()

    # button shows hex view
    def _handle_show_hex_view(self):
        self._image_hex_window.show()

    # button deselects the current offset selection
    def _handle_deselect_offset_selection(self):
        self._offset_selection.clear()

