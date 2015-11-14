import colors
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class AnnotationWindow():
    _checkbuttons = list() # (checkbutton, annotation_type, int_var)
    """Provides a window to show opened project attributes.
    """
    def __init__(self, master, data_manager, annotation_filter):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages project data and filters.
          annotation_filter(AnnotationFilter): The annotation filter that
            selections modify.
        """
        # variables
        self._data_manager = data_manager
        self._annotation_filter = annotation_filter

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Manage Annotations")
        self._root_window.transient(master)
        self._root_window.protocol('WM_DELETE_WINDOW', self._hide)

        # make the containing frame
        self._frame = tkinter.Frame(self._root_window, padx=8, pady=8,
                                                       bg=colors.BACKGROUND)
        self._frame.pack()

        # title
        tkinter.Label(self._frame, text="Annotations",
                                             bg=colors.BACKGROUND).pack(
                                             side=tkinter.TOP, padx=100,
                                                               pady=(0,4))

        # register to receive data manager change events
        data_manager.set_callback(self._handle_data_manager_change)

        # start with window hidden
        self._root_window.withdraw()

    # this function is registered to and called by IdentifiedData
    def _handle_data_manager_change(self, *args):

        # clear existing checkbuttons
        for checkbutton, _, _ in self._checkbuttons:
            checkbutton.destroy()
        self._checkbuttons.clear()

        # initial ignored_types
        ignored_types = set()

        # process each annotation type
        for annotation_type, description, is_active in \
                               self._data_manager.annotation_types:

            # mark ignored types
            if not is_active:
                ignored_types.add(annotation_type)

            # create checkbutton for the annotation type
            int_var = tkinter.IntVar()
            int_var.set(is_active)
            checkbutton = tkinter.Checkbutton(self._frame, text=description,
                               variable=int_var,
                               command=self._handle_checkbutton_press,
                               bd=0, bg=colors.BACKGROUND,
                               activebackground=colors.ACTIVEBACKGROUND,
                               pady=4, highlightthickness=0)
            checkbutton.pack(side=tkinter.TOP, anchor="w")
            self._checkbuttons.append((checkbutton, annotation_type, int_var))

        # set annotation filter with initial state
        self._annotation_filter.set(ignored_types)

    def _handle_checkbutton_press(self, *args):
        ignored_types = set()
        for _, annotation_type, int_var in self._checkbuttons:
            if not int_var.get():
                ignored_types.add(annotation_type)
        self._annotation_filter.set(ignored_types)

    def show(self):
        self._root_window.deiconify()
        self._root_window.lift()

    def _hide(self):
        self._root_window.withdraw()

