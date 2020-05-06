import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from osgeo import gdal
import matplotlib.pyplot as plt

TEMP_DEST = "temp/temp_reprojected_"
TIFF_EXTENSION = ".tiff"


class GraphProcessor:
    def __init__(self, fn1, fn2, data_dict):
        self.fn1 = fn1
        self.fn2 = fn2
        self.dataDict = data_dict
        self.queue = None
        self.X = None
        self.Y = None
        self.band1 = None
        self.band2 = None

    def preprocess(self, queue):
        # Pass in the Queue
        self.queue = queue

        # Load in the Datasets
        ds1 = self.dataDict[self.fn1][0]
        ds2 = self.dataDict[self.fn2][0]

        # print(self.fn1)
        # print(self.fn2)
        # print("original coordinates:")
        # print(ds1.RasterXSize)
        # print(ds1.RasterYSize)
        # print(ds2.RasterXSize)
        # print(ds2.RasterYSize)

        # Re-project both layers to be of the same dimensions
        # minX, minY = self.find_min_dim(ds1, ds2)
        # gdal.Warp(TEMP_DEST + str(1) + TIFF_EXTENSION, ds1, width=minX, height=minY)
        # gdal.Warp(TEMP_DEST + str(2) + TIFF_EXTENSION, ds2, width=minX, height=minY)

        gdal.Warp(TEMP_DEST + str(1) + TIFF_EXTENSION, ds1, width=1000, height=1000)    # FIXME: Temporary fix to eliminate performance issues.
        gdal.Warp(TEMP_DEST + str(2) + TIFF_EXTENSION, ds2, width=1000, height=1000)

        ds1Translated = gdal.Open(TEMP_DEST + str(1) + TIFF_EXTENSION)
        ds2Translated = gdal.Open(TEMP_DEST + str(2) + TIFF_EXTENSION)

        self.band1 = ds1Translated.GetRasterBand(1).ReadAsArray()
        self.band2 = ds2Translated.GetRasterBand(1).ReadAsArray()

        # Remove No Data Values from the data
        ndv1 = ds1.GetRasterBand(1).GetNoDataValue()
        ndv2 = ds2.GetRasterBand(1).GetNoDataValue()
        self.band1[self.band1 == ndv1] = np.nan
        self.band2[self.band2 == ndv2] = np.nan

        # print("New coordinates:")
        # print(ds1Translated.RasterXSize)
        # print(ds1Translated.RasterYSize)
        # print(ds2Translated.RasterXSize)
        # print(ds2Translated.RasterYSize)

        xSize = ds1Translated.RasterXSize
        ySize = ds1Translated.RasterYSize

        # Generate 2D arrays of X and Y for graphing
        x = range(xSize)
        y = range(ySize)
        self.X, self.Y = np.meshgrid(x, y)

        print("PREPROCESS FINISHED")
        self.queue.put("PREPROCESS FINISHED")
        return

    def graph(self):
        fig = plt.figure(figsize=(5, 4), dpi=200)
        ax = fig.add_subplot(111, projection='3d')

        ax.plot_surface(self.X, self.Y, self.band1, label="Layer 1", color="blue")
        ax.plot_surface(self.X, self.Y, self.band2, label="Layer 2", color="orange")

        # Customize the Popup Window
        fig.canvas.set_window_title("DEM 3D Visualization")
        plt.show()
        return

    def find_min_dim(self, ds1, ds2):
        x1 = ds1.RasterXSize
        x2 = ds2.RasterXSize
        if (x1 < x2):
            resultx = x1
        else:
            resultx = x2

        y1 = ds1.RasterYSize
        y2 = ds2.RasterYSize

        if (y1 < y2):
            resulty = y1
        else:
            resulty = y2

        return resultx, resulty
