import tkinter 

class ImageOverviewPlot():
    """Prints a banner and plots an image overview of matched blocks
    given an IdentifiedData data structure.

    Plot points with a higher match density are shown darker than points
    with a lower match density.

    Clicking on a plot point sets the image offset in the IntVar variable
    provided.
    """

    def __init__(self, master, identified_data, selected_offset):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All the identified data about
            the scan.
          selected_offset(IntVar): Variable notified upon mouse click.
        """

        f = tkinter.Frame(master)
        tkinter.Label(f, text='Image Overview').pack(side=tkinter.TOP)
        tkinter.Label(f, text='Image: %s'%identified_data.image_filename) \
                      .pack(side=tkinter.TOP)
        tkinter.Label(f, text='selected offset value TBD').pack(side=tkinter.TOP)

        self._make_image(identified_data)
        tkinter.Label(f, image=self.photo_image, relief=tkinter.SUNKEN).pack(side=tkinter.TOP, padx=5,pady=5)
        f.pack()

    def _make_image(self, identified_data):
        """Args:
          identified_data (IdentifiedData): All the identified data about
            the scan.
        """

        # light to dark blue
        colors = ["#99ffff","#66ffff","#33ffff",
                  "#00ffff","#00ccff","#0099ff","#0066ff","#0033ff",
                  "#0000ff","#0000cc","#000099","#000066"]
        # white through blue to black, 0 is white, not used, and 15 is black
        #colors = ["#ffffff","#ccffff","#99ffff","#66ffff","#33ffff",
        #          "#00ffff","#00ccff","#0099ff","#0066ff","#0033ff",
        #          "#0000ff","#0000cc","#000099","#000066","#000033",
        #          "#000000"]

        # order of the 2D square matrix
        MATRIX_ORDER = 100

        # pixels per data point
        POINT_SIZE = 4

        # plot size
        PLOT_SIZE = MATRIX_ORDER * POINT_SIZE

        # create the photo_image
        self.photo_image = tkinter.PhotoImage(width=PLOT_SIZE, height=PLOT_SIZE)

        # start with white
        self.photo_image.put("white", to=(0, 0, PLOT_SIZE, PLOT_SIZE))

        # calculate rescaler for going from media image offset to data index
        rescaler = MATRIX_ORDER**2 / identified_data.image_size

        # if the matrix is larger than the image then clip the rescaler
        if rescaler > 1.0:
            rescaler = 1.0

        # allocate empty data array
        data = [0] * (MATRIX_ORDER**2)

        # set data points
        for key in identified_data.forensic_paths:
            subscript = int(int(key) * rescaler)
            if data[subscript] < 11:
                data[subscript] += 1

        # plot the data points
        for i in range(MATRIX_ORDER**2):
            if (data[i] > 0):
                point_color = colors[data[i]]
                x=(i%MATRIX_ORDER) * POINT_SIZE
                y=(i//MATRIX_ORDER) * POINT_SIZE
                self.photo_image.put(point_color,
                                     to=(x, y, x+POINT_SIZE, y+POINT_SIZE))

        # if plot is larger than file, paint bottom part gray
        if MATRIX_ORDER**2 > identified_data.image_size:
            for i in range(identified_data.image_size+1, MATRIX_ORDER**2):
                x=(i%MATRIX_ORDER) * POINT_SIZE
                y=(i//MATRIX_ORDER) * POINT_SIZE
                self.photo_image.put("gray",
                                     to=(x, y, x+POINT_SIZE, y+POINT_SIZE))

