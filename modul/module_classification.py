#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      s6anloew
#
# Created:     16.09.2014
# Copyright:   (c) s6anloew 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys
from osgeo import gdal
from gdalconst import *
import numpy as np

class Reclassification():
    def __init__(self, inFile, outFolder, no_data= -9999):
        self.infile =  inFile
        self.outfile= outFolder
        self.no_data = no_data
        if os.path.exists(self.infile)==False:
            self.message =  'File ' + self.infile + ' does not exist'
        else:
            self.inFile_knwlgd = gdal.Open(self.infile, GA_ReadOnly)
            #self.FileOutput= os.path.join(outFolder, "reclassed_" + os.path.split(self.infile)[1] )


        if self.inFile_knwlgd is None:
            self.message =  'Could not open ' + self.infile
        else:
            self.driver = self.inFile_knwlgd.GetDriver()
            self.driver.Register()


    def Reclassify(self):
        self.cols = self.inFile_knwlgd.RasterXSize
        self.rows = self.inFile_knwlgd.RasterYSize

        dst_ds = self.driver.Create(self.outfile , self.cols, self.rows, 1, GDT_Int16)
        dst_ds.SetGeoTransform(self.inFile_knwlgd.GetGeoTransform())
        dst_ds.SetProjection(self.inFile_knwlgd.GetProjection())
        self.band =  self.inFile_knwlgd.GetRasterBand(1)

        blockSize = 1500
        for i in range(0, self.rows, blockSize):
            if i + blockSize < self.rows:
                numRows = blockSize
            else:
                numRows = self.rows - i

            for j in range(0, self.cols, blockSize):
                if j + blockSize < self.cols:
                    numCols = blockSize
                else:
                    numCols = self.cols - j

                self.data = self.band.ReadAsArray(j, i, numCols,numRows).astype(np.float32)
                self.data[self.data != self.no_data ] = 1
                self.data[self.data == self.no_data ] = 0

                dst_ds.GetRasterBand(1).WriteArray(self.data, j, i)
        dst_ds = None
        self.data = None
        #return self.FileOutput

##
##Reclassification("H:\\Laser\\Testings\\test\\altstadt\\results\\filtered_altstadt_1.tif", "H:\\Laser\\Testings\\test\\altstadt\\results\\reclass_altstadt_1.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\altstadt\\results\\filtered_altstadt_2.tif", "H:\\Laser\\Testings\\test\\altstadt\\results\\reclass_altstadt_2.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\altstadt\\results\\filtered_altstadt_3.tif", "H:\\Laser\\Testings\\test\\altstadt\\results\\reclass_altstadt_3.tif").Reclassify()
##
##
##Reclassification("H:\\Laser\\Testings\\test\\feyen\\results\\filtered_feyen_1.tif", "H:\\Laser\\Testings\\test\\feyen\\results\\reclass_feyen_1.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\feyen\\results\\filtered_feyen_2.tif", "H:\\Laser\\Testings\\test\\feyen\\results\\reclass_feyen_2.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\feyen\\results\\filtered_feyen_3.tif", "H:\\Laser\\Testings\\test\\feyen\\results\\reclass_feyen_3.tif").Reclassify()
##
##
##Reclassification("H:\\Laser\\Testings\\test\\gartenfeld\\results\\filtered_gartenfeld_1.tif", "H:\\Laser\\Testings\\test\\gartenfeld\\results\\reclass_gartenfeld_1.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\gartenfeld\\results\\filtered_gartenfeld_2.tif", "H:\\Laser\\Testings\\test\\gartenfeld\\results\\reclass_gartenfeld_2.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\gartenfeld\\results\\filtered_gartenfeld_3.tif", "H:\\Laser\\Testings\\test\\gartenfeld\\results\\reclass_gartenfeld_3.tif").Reclassify()
##
##
##Reclassification("H:\\Laser\\Testings\\test\\maximin\\results\\filtered_maximin_1.tif", "H:\\Laser\\Testings\\test\\maximin\\results\\reclass_maximin_1.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\maximin\\results\\filtered_maximin_2.tif", "H:\\Laser\\Testings\\test\\maximin\\results\\reclass_maximin_2.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\maximin\\results\\filtered_maximin_3.tif", "H:\\Laser\\Testings\\test\\maximin\\results\\reclass_maximin_3.tif").Reclassify()
##
##
##Reclassification("H:\\Laser\\Testings\\test\\pallien\\results\\filtered_pallien_1.tif", "H:\\Laser\\Testings\\test\\pallien\\results\\reclass_pallien_1.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\pallien\\results\\filtered_pallien_2.tif", "H:\\Laser\\Testings\\test\\pallien\\results\\reclass_pallien_2.tif").Reclassify()
Reclassification("H:\\Laser\\Testings\\test\\pallien\\results\\filtered_pallien_3.tif", "H:\\Laser\\Testings\\test\\pallien\\results\\reclass_pallient_3.tif").Reclassify()
##
##
##Reclassification("H:\\Laser\\Testings\\test\\trier_west\\results\\filtered_trier_west_1.tif", "H:\\Laser\\Testings\\test\\trier_west\\results\\reclass_trier_west_1.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\trier_west\\results\\filtered_trier_west_2.tif", "H:\\Laser\\Testings\\test\\trier_west\\results\\reclass_trier_west_2.tif").Reclassify()
##Reclassification("H:\\Laser\\Testings\\test\\trier_west\\results\\filtered_trier_west_3.tif", "H:\\Laser\\Testings\\test\\trier_west\\results\\reclass_trier_west_3.tif").Reclassify()