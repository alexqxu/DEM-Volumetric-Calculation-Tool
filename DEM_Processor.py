import numpy as np
from osgeo import gdal

CUT_FILE_PREFIX = "temp/cut_to_shape_"
TIFF_EXTENSION = ".tiff"


class DEMProcessor:
    def __init__(self, dataHandler):
        gdal.UseExceptions()
        self.DEMList = dataHandler.getDEMs()
        self.shapeFile = dataHandler.getShape()
        self.dataDict = {}
        self.resultDict = {}
        self.queue = None

    def perform_calculation(self, queue):   # TODO: Move queue passing to the constructor instead
        # Pass in the Queue
        self.queue = queue

        # Step 1 is to Cut the DEMs to conform to the Shape File
        self.cut_to_shape()

        # Step 2 is to extract the dataset from each cut DEM image. Here it is put into a dictionary.
        self.extract_dataset()

        # Step 3 is to perform calculation over integration, over every pair of DEM files.
        pairs = self.generatePairs()
        for n in range(self.nC2()):
            fn1 = pairs[n][0]
            fn2 = pairs[n][1]
            result = self.calculate(fn1, fn2)
            # Put into the results dictionary. Key is pair (tuple). The value is a tuple with the result and the unit.
            self.resultDict[pairs[n]] = result

        # Print to console and signal to the main thread that work is finished
        print("CALCULATION FINISHED")
        self.queue.put("CALCULATION FINISHED")
        return

    def get_results(self):
        return self.resultDict

    # Returns map of filenames and their data/length unit
    def get_dataDict(self):
        return self.dataDict

    def cut_to_shape(self):
        for i in range(len(self.DEMList)):
            destinationName = CUT_FILE_PREFIX + str(i) + TIFF_EXTENSION
            fn = self.DEMList[i]
            gdal.Warp(destinationName, fn, cutlineDSName=self.shapeFile)
        return

    # Make a dictionary, where the key are the filenames and the values are tuples with the datasets and their Length
    # Unit
    def extract_dataset(self):
        for i in range(len(self.DEMList)):
            fn = self.DEMList[i]
            cutFile = CUT_FILE_PREFIX + str(i) + TIFF_EXTENSION
            ds = gdal.Open(cutFile)
            unit = self.get_length_unit(ds)
            value = (ds, unit)
            self.dataDict[fn] = value
        return

    def calculate(self, fn1, fn2):
        # Select the datasets and units to work with
        ds1 = self.dataDict[fn1][0]
        ds2 = self.dataDict[fn2][0]

        unit1 = self.dataDict[fn1][1] # Length Unit

        # PRINT INFORMATION TO PYTHON CONSOLE (For Testing Purposes)
        # print("Layer 1: ", ds1.RasterXSize, " by ", ds1.RasterYSize)
        # print("Layer 2: ", ds2.RasterXSize, " by ", ds2.RasterYSize)
        # print(ds1.GetProjection())
        # print(ds1.GetGeoTransform())

        # Extract band data from datasets
        band1 = ds1.GetRasterBand(1).ReadAsArray()
        band2 = ds2.GetRasterBand(1).ReadAsArray()

        # Extract pixel dimensions
        pixel_width1 = np.abs(ds1.GetGeoTransform()[1])
        pixel_height1 = np.abs(ds1.GetGeoTransform()[5])

        pixel_width2 = np.abs(ds2.GetGeoTransform()[1])
        pixel_height2 = np.abs(ds2.GetGeoTransform()[5])

        # Remove No Data Values
        ndv1 = ds1.GetRasterBand(1).GetNoDataValue()
        ndv2 = ds2.GetRasterBand(1).GetNoDataValue()
        band1[band1 == ndv1] = 0
        band2[band2 == ndv2] = 0

        # Subtract both layers with respect to the zero horizon
        subzero1 = self.sub_with_zero(band1, pixel_width1, pixel_height1)
        subzero2 = self.sub_with_zero(band2, pixel_width2, pixel_height2)

        # Perform final calculation
        total = round(subzero1 - subzero2, 4)
        result = (str(total), unit1)
        return result

    def nC2(self):
        size = len(self.DEMList)
        result = (size * (size - 1)) / 2
        return int(result)

    # Returns a list of pairs.

    def generatePairs(self):
        size = len(self.DEMList)
        pairs = []
        for i in range(size - 1):
            fn1 = self.DEMList[i]
            for j in range(i + 1, size):
                fn2 = self.DEMList[j]
                pair = (fn1, fn2)
                pairs.append(pair)
        return pairs

    # subtracts the band data with the ZERO plane.
    def sub_with_zero(self, band, pixelwidth, pixelheight):
        result = np.sum(band) * pixelwidth * pixelheight
        return result

    # Get unit for Length
    def get_length_unit(self, ds1):
        unit1 = gdal.Info(ds1)
        index1 = unit1.index("LENGTHUNIT")
        unit1 = unit1[index1 + 12:index1 + 17]
        return unit1
