# -*- coding: utf-8 -*-
"""
Created on Tue Sep 02 21:18:17 2014

@author: Andreas
"""
import numpy as np
import gdal
from osgeo import osr


class NDVI():
    def __init__(self, inFile, outFile, bandRed, bandIR):
        self.infile = str(inFile)
        self.outfile = str(outFile)
        self.band_red = int(bandRed)
        self.band_ir = int(bandIR)


    def calc_ndvi(self):
        self.inputDS_ndvi = gdal.Open(self.infile, gdal.GA_ReadOnly)
        if  self.inputDS_ndvi != None:
            bandlst = [ self.inputDS_ndvi.GetRasterBand(i+1) for i in range( self.inputDS_ndvi.RasterCount)]
            self.driverout = self.inputDS_ndvi.GetDriver()
            self.driverout.Register()
            rows = self.inputDS_ndvi.RasterYSize
            cols = self.inputDS_ndvi.RasterXSize

            self.outDS= self.driverout.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)

            if self.inputDS_ndvi.GetProjection() == "":
                srs = osr.SpatialReference()                 # Establish its coordinate encoding
                srs.ImportFromEPSG(32632)
                self.outDS.SetGeoTransform(self.inputDS_ndvi.GetGeoTransform())
                self.outDS.SetProjection(srs.ExportToWkt())
            else:
                self.outDS.SetGeoTransform(self.inputDS_ndvi.GetGeoTransform())
                self.outDS.SetProjection(self.inputDS_ndvi.GetProjection())

            ndviBand = self.outDS.GetRasterBand(1)

            bandNIR = bandlst[self.band_ir]
            bandRED = bandlst[self.band_red]
            blockSize = 500
            noDataValue = -999

            for i in range(0, rows, blockSize):
                if i + blockSize < rows:
                    numRows = blockSize
                else:
                    numRows = rows - i

                for j in range(0, cols, blockSize):
                    if j + blockSize < cols:
                        numCols = blockSize
                    else:
                        numCols = cols - j
                    """get the data"""
                    RED = bandRED.ReadAsArray(j, i, numCols, numRows)
                    NIR = bandNIR.ReadAsArray(j, i, numCols, numRows)

                    RED_int32 = np.array(RED, dtype= np.float32)
                    NIR_int32 = np.array(NIR, dtype= np.float32)

                    """calculation"""
                    mask = np.greater(NIR_int32 + RED_int32, 0)
                    ndvi = np.choose(mask, (noDataValue, (NIR_int32 - RED_int32) / (NIR_int32 + RED_int32)))

                    """write the data"""
                    ndviBand.WriteArray(ndvi, j, i)
                    ndviBand.SetNoDataValue(noDataValue)
            #print "wrote %s in %s seconds" %(OutFile, time.time() - intertime)
            mask = None
            ndvi = None
            self.inputDS_ndvi = None
            self.outDS = None
            message = "The NDVI was calculated succesfully!"
            return [self.outfile,message]

        else:
            message = "The ndvi could not be calculated!"
            return message