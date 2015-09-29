from colors import background, activebackground
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection
from histogram_bar import HistogramBar
from image_hex_window import ImageHexWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

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
        self.frame = tkinter.Frame(master, bg=background)

        # title
        tkinter.Label(self.frame, text="Offset Selection", bg=background).pack(
                                        side=tkinter.TOP, pady=(0,4))

        # offset selection label
        self._offset_selection_label = tkinter.Label(self.frame, anchor="w",
                                                           bg=background)
        self._offset_selection_label.pack(side=tkinter.TOP, anchor="w",
                                                           fill=tkinter.X)

        # MD5 label
        self._md5_label = tkinter.Label(self.frame, anchor="w", width=40,
                                                           bg=background)
        self._md5_label.pack(side=tkinter.TOP, anchor="w", fill=tkinter.X)

        # button frame
        button_frame = tkinter.Frame(self.frame)
        button_frame.pack(side=tkinter.TOP)

        # button to add selected hash
        self._add_hash_icon = tkinter.PhotoImage(file=icon_path("add_hash"))
        self._add_hash_button = tkinter.Button(button_frame,
                              image=self._add_hash_icon,
                              command=self._handle_add_hash_to_highlight,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
 
        self._add_hash_button.pack(side=tkinter.LEFT)
        Tooltip(self._add_hash_button, "Highlight the selected hash")

        # button to remove selected hash
        self._remove_hash_icon = tkinter.PhotoImage(file=icon_path(
                                                              "remove_hash"))
        self._remove_hash_button = tkinter.Button(button_frame,
                              image=self._remove_hash_icon,
                              command=self._handle_remove_hash_from_highlight,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._remove_hash_button.pack(side=tkinter.LEFT)
        Tooltip(self._remove_hash_button, "Stop highlighting the selected hash")

        # button to show hex view for selection
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        self._show_hex_view_button = tkinter.Button(button_frame,
                              image=self._show_hex_view_icon,
                              command=self._handle_show_hex_view,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._show_hex_view_button.pack(side=tkinter.LEFT)
        Tooltip(self._show_hex_view_button, "Show hex view of selection")

        # button to clear the offset selection
        self._clear_offset_selection_icon = tkinter.PhotoImage(
                                file=icon_path( "clear_offset_selection"))
        self._clear_offset_selection_button = tkinter.Button(button_frame,
                              image=self._clear_offset_selection_icon,
                              state=tkinter.DISABLED,
                              command=self._handle_clear_offset_selection,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._clear_offset_selection_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_offset_selection_button,
                                             "Deselect the selection")

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

    def _set_highlight_button_states(self):
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

    def _handle_highlight_change(self, *args):
        self._set_highlight_button_states()

    def _handle_offset_selection_change(self, *args):

        # set selection labels and button states
        if self._offset_selection.offset == -1:
            # clear
            self._offset_selection_label['text'] = "Selection: Not selected"
            self._md5_label['text'] = "MD5: Not selected"

            self._show_hex_view_button.config(state=tkinter.DISABLED)
            self._clear_offset_selection_button.config(
                                              state=tkinter.DISABLED)

        else:
            # set to selection
            self._offset_selection_label["text"] = "Selection: %s" % \
                                 offset_string(self._offset_selection.offset)
            self._md5_label["text"] = \
                 "MD5: %s" % self._offset_selection.block_hash

            self._show_hex_view_button.config(state=tkinter.NORMAL)
            self._clear_offset_selection_button.config(
                                              state=tkinter.NORMAL)

        # set highlight button states
        self._set_highlight_button_states()

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

