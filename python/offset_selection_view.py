import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection
from histogram_bar import HistogramBar
from image_hex_window import ImageHexWindow

class OffsetSelectionView():
    """The selection view including title, offset, MD5, and button controls.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, highlights, offset_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          highlights(Highlights): Highlights that impact the view.
          offset_selection(OffsetSelection): The selected offset.
        """

        # data variables
        self._identified_data = identified_data
        self._highlights = highlights
        self._offset_selection = offset_selection

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # title
        tkinter.Label(self.frame, text="Offset Selection").pack(
                                                side=tkinter.TOP, anchor="w")

        # offset label
        self._offset_label = tkinter.Label(self.frame, anchor="w")
        self._offset_label.pack(side=tkinter.TOP, anchor="w", fill=tkinter.X)

        # MD5 label
        self._md5_label = tkinter.Label(self.frame, anchor="w", width=50)
        self._md5_label.pack(side=tkinter.TOP, anchor="w", fill=tkinter.X)

        # button frame
        button_frame = tkinter.Frame(self.frame)
        button_frame.pack(side=tkinter.LEFT)

        # button to add selected hash
        self._add_hash_icon = tkinter.PhotoImage(file=icon_path("add_hash"))
        self._add_hash_button = tkinter.Button(button_frame,
                                image=self._add_hash_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_add_hash_to_highlight)
        self._add_hash_button.pack(side=tkinter.LEFT, padx=(0,0))
        Tooltip(self._add_hash_button, "Highlight the selected hash")

        # button to remove selected hash
        self._remove_hash_icon = tkinter.PhotoImage(file=icon_path(
                                                              "remove_hash"))
        self._remove_hash_button = tkinter.Button(button_frame,
                              image=self._remove_hash_icon,
                              state=tkinter.DISABLED,
                              command=self._handle_remove_hash_from_highlight)
        self._remove_hash_button.pack(side=tkinter.LEFT)
        Tooltip(self._remove_hash_button, "Stop highlighting the selected hash")

        # button to show hex view for selection
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        self._show_hex_view_button = tkinter.Button(button_frame,
                                image=self._show_hex_view_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_show_hex_view)
        self._show_hex_view_button.pack(side=tkinter.LEFT, padx=8)
        Tooltip(self._show_hex_view_button, "Show hex view of selection")

        # button to clear the offset selection
        self._clear_offset_selection_icon = tkinter.PhotoImage(
                                file=icon_path( "clear_offset_selection"))
        self._clear_offset_selection_button = tkinter.Button(button_frame,
                                image=self._clear_offset_selection_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_clear_offset_selection)
        self._clear_offset_selection_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_offset_selection_button,
                                             "Clear the selected range")

        # create the image hex window that the show hex view button can show
        self._image_hex_window = ImageHexWindow(self.frame, identified_data,
                                                highlights, offset_selection)

        # register to receive highlight change events
        highlights.set_callback(self._handle_highlight_change)

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_offset_selection_change)

        # set initial state
        self._handle_highlight_change()
        self._handle_offset_selection_change()

    def _handle_highlight_change(self, *args):
        # disable both if there is no active selection
        if self._offset_selection.offset == -1:
            self._add_hash_button.config(state=tkinter.DISABLED)
            self._remove_hash_button.config(state=tkinter.DISABLED)
            return

        # reference to selected hash
        selected_hash = self._offset_selection.block_hash

        # set enabled state of the add hash button
        if selected_hash not in self._highlights.highlighted_hashes and \
                           selected_hash in self._identified_data.hashes:
            self._add_hash_button.config(state=tkinter.NORMAL)
        else:
            self._add_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the remove hash button
        if selected_hash in self._highlights.highlighted_hashes:
            self._remove_hash_button.config(state=tkinter.NORMAL)
        else:
            self._remove_hash_button.config(state=tkinter.DISABLED)


    def _handle_offset_selection_change(self, *args):

        # set the selected image offset and its associated hash value
        if self._offset_selection.offset == -1:
            # clear
            self._offset_label['text'] = "Selected offset: Not selected"
            self._md5_label['text'] = "MD5 at offset: Not selected"

            self._show_hex_view_button.config(state=tkinter.DISABLED)
            self._clear_offset_selection_button.config(
                                              state=tkinter.DISABLED)

        else:
            # set to selection
            self._offset_label["text"] = "Selected offset: %s" % offset_string(
                                       self._offset_selection.offset)
            self._md5_label["text"] = \
                 "MD5 at offset: %s" % self._offset_selection.block_hash

            self._show_hex_view_button.config(state=tkinter.NORMAL)
            self._clear_offset_selection_button.config(
                                              state=tkinter.NORMAL)

    # button changes highlight state
    def _handle_add_hash_to_highlight(self):
        self._highlights.highlighted_hashes.add(
                                           self._offset_selection.block_hash)
        self._highlights.fire_change()

    # button changes highlight state
    def _handle_remove_hash_from_highlight(self):
        self._highlights.highlighted_hashes.remove(
                                           self._offset_selection.block_hash)
        self._highlights.fire_change()

    # button shows hex view
    def _handle_show_hex_view(self):
        self._image_hex_window.show()

    # button clears the current offset selection
    def _handle_clear_offset_selection(self):
        self._offset_selection.clear()

