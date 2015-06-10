from tkinter import *

class ImageOverviewPlot():
    """Provides tkinter PhotoImage overview of the media image.
 given an
    IdentifiedData data structure.

    Attributes:
      photo_image (tkinter.PhotoImage): The photo image containng the view.
    """

    def __init__(self):
        # light to dark blue
        self.colors = ["#99ffff","#66ffff","#33ffff",
                       "#00ffff","#00ccff","#0099ff","#0066ff","#0033ff",
                       "#0000ff","#0000cc","#000099","#000066"]
        # white through blue to black, 0 is white, not used, and 15 is black
        #self.colors = ["#ffffff","#ccffff","#99ffff","#66ffff","#33ffff",
        #               "#00ffff","#00ccff","#0099ff","#0066ff","#0033ff",
        #               "#0000ff","#0000cc","#000099","#000066","#000033",
        #               "#000000"]

        # size of 2D data grid
        self.GRID_SIZE = 100

        # pixels per data point
        self.POINT_SIZE = 4

        # pixel size of plot
        self.PIXEL_SIZE = self.GRID_SIZE * self.POINT_SIZE

        self.photo_image = PhotoImage(width=self.PIXEL_SIZE,
                                      height=self.PIXEL_SIZE)
        self.clear()

    def clear(self):
        self.photo_image.put("#ffffff",
                             to=(0, 0, self.PIXEL_SIZE, self.PIXEL_SIZE))


    def set(self, identified_data):
        """Attributes:
          identified_data (IdentifiedData): All the identified data about
            the scan.
        """

        # calculate rescaler for going from media image offset to data index
        rescaler = self.GRID_SIZE*self.GRID_SIZE / identified_data.image_size

        # allocate empty data array
        data = [0] * (self.GRID_SIZE*self.GRID_SIZE)

        # set data points
        for key in identified_data.forensic_paths:
            subscript = int(int(key) * rescaler)
            data[subscript] = data[subscript]+1 if data[subscript] < 11 \
                                                     else data[subscript]

        # plot the data points
        for i in range(self.GRID_SIZE*self.GRID_SIZE):
            if (data[i] > 0):
                point_color = self.colors[data[i]]
                x=(i%self.GRID_SIZE) * self.POINT_SIZE
                y=(i//self.GRID_SIZE) * self.POINT_SIZE
                self.photo_image.put(point_color,
                            to=(x, y, x+self.POINT_SIZE, y+self.POINT_SIZE))
 
