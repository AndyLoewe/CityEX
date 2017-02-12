# -*- coding: utf-8 -*-
"""
Created on Tue Sep 02 21:17:50 2014

@author: Andreas
"""

import numpy as np
import gdal
#from osgeo import gdal_array

class NDEM():
    def __init__(self, model_dem, model_dom,outFile, noData):
        self.model_dem = str(model_dem)
        self.model_dom = str(model_dom)
        self.outfile = str(outFile)
        self.no_data = noData

        self.InputDS_DEM = gdal.Open(self.model_dem, gdal.GA_ReadOnly)
        self.InputDS_DOM = gdal.Open(self.model_dom, gdal.GA_ReadOnly)
        if self.InputDS_DEM == None or self.InputDS_DOM == None:
            self.message = "Either DEM or DOM missing"

        else:
            self.message = "everything worked"

    def calc_ndem(self):
        self.band_DEM = self.InputDS_DEM.GetRasterBand(1)
        self.band_DOM = self.InputDS_DOM.GetRasterBand(1)
        self.driverout_DEM = self.InputDS_DEM.GetDriver()

        self.rows_DEM = self.InputDS_DEM.RasterYSize
        self.cols_DEM = self.InputDS_DEM.RasterXSize
        self.rows_DOM = self.InputDS_DEM.RasterYSize
        self.cols_DOM = self.InputDS_DEM.RasterXSize
        if self.rows_DEM == self.rows_DOM and self.cols_DEM == self.cols_DOM:
            self.outDS = self.driverout_DEM.Create(self.outfile, self.cols_DOM, self.rows_DOM ,1, gdal.GDT_Float32)
            self.outDS.SetGeoTransform(self.InputDS_DEM.GetGeoTransform())
            self.outDS.SetProjection(self.InputDS_DEM.GetProjection())

            nDEM_band = self.outDS.GetRasterBand(1)
            #numpyBandType = gdal_array.GDALTypeCodeToNumericTypeCode(gdal.GDT_CFloat32)
            blockSize = 500

            for i in range(0, self.rows_DOM, blockSize):
                if i + blockSize < self.rows_DOM:
                    numRows = blockSize
                else:
                    numRows = self.rows_DOM - i

                for j in range(0, self.cols_DOM, blockSize):
                    if j + blockSize < self.cols_DOM:
                        numCols = blockSize
                    else:
                            numCols = self.cols_DOM - j
                    self.DEM = self.band_DEM .ReadAsArray(j, i, numCols, numRows)
                    self.DOM = self.band_DOM .ReadAsArray(j, i, numCols, numRows)


                    mask = np.greater_equal(self.DOM - self.DEM, 0)
                    nDEM = np.choose(mask, (self.no_data, self.DOM - self.DEM ))

                    nDEM_band.WriteArray(nDEM, j, i)
                    nDEM_band.SetNoDataValue(self.no_data)
            self.message = "Finished the computing of the nDEM!"
        else:
            self.message = "the data didnt fit"
        mask = None
        nDEM = None
        self.InputDS_DOM = None
        self.InputDS_DEM = None
        self.outDS  = None
        return [self.message, self.outfile]
