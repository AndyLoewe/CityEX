#-------------------------------------------------------------------------------
# Name:        module_filter
# Purpose:
#
# Author:      s6anloew
#
# Created:     03.09.2014
# Copyright:   (c) s6anloew 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#import matplotlib.pyplot as plt
from scipy import ndimage
import scipy
import os
import numpy as np
import gdal

from osgeo import gdal_array


class Filter_ndem():
    def __init__(self, inFile_knowlegde, inFile_nDEM, outFolder,filter_lst, no_data = -9999):
        self.infile_knwlgd = inFile_knowlegde
        self.infile_ndem = inFile_nDEM
        self.outfile_name = os.path.split(self.infile_knwlgd)[1]
        self.outfile  = outFolder
        self.filterlst = filter_lst
        #self.outfile = os.path.join(self.outfolder, "filterd_" + self.outfile_name )
        self.nodata = no_data

    def filter_application(self):
        ### the filter lst beinhaltet die namen, der funktionen, so dass auf die variable immer die neue
        ### funktion angewendet wird bsp. lst = [("value", (3,3))] -> lst[0][0] _>  lst[0][1] _>
        ### lst[0][1][0] -> lst[0][1][1]
        In_File_filler = gdal.Open(self.infile_ndem)
        In_file = gdal.Open(self.infile_knwlgd)
        driver = In_file.GetDriver()

        band_filler = In_File_filler.GetRasterBand(1)
        band_buildup  = In_file.GetRasterBand(1)
        rows = In_file.RasterYSize
        cols = In_file.RasterXSize

        self.outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
        self.outDS.SetGeoTransform(In_file.GetGeoTransform())
        self.outDS.SetProjection(In_file.GetProjection())

        #numpyBandType = gdal_array.GDALTypeCodeToNumericTypeCode(gdal.GDT_CFloat32)

        blockSize = 5000
        band_filtert = self.outDS.GetRasterBand(1)

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
                fil_start = band_filler.ReadAsArray(j,i,numCols,numRows)
                filter_ndem = band_buildup.ReadAsArray(j,i,numCols,numRows)
                start_mask = filter_ndem > 0
                mask = None
                for ii in range(len(self.filterlst)):


                    mask_func = self.filterlst[ii][0]
                    if mask == None:
                        mask = mask_func(start_mask, structure=np.ones((self.filterlst[ii][1][0],self.filterlst[ii][1][1])))
                    else:
                        mask = mask_func(mask, structure=np.ones((self.filterlst[ii][1][0],self.filterlst[ii][1][1])))
                buildup_filtert = np.choose(mask,(self.nodata,fil_start))
                mask = None
                band_filtert.WriteArray(buildup_filtert, j,i)
                band_filtert.SetNoDataValue(self.nodata)
                self.message = "The filtering worked as planed"

        self.outDS = None
        return [self.outfile_name, self.message]


dic_lst = [(ndimage.binary_fill_holes,[4, 4]),(ndimage.binary_closing, [3, 3]), (ndimage.binary_opening , [5, 6])]


##
##Filter_ndem("H:\\Laser\\Testings\\test\\pallien\\results\\knwldg_pallien_05m_1.tif", "H:\\Laser\\Testings\\test\\pallien\\ndem_05m_pallien.tif",
##"H:\\Laser\\Testings\\test\\pallien\\results\\filtered_pallien_1.tif", dic_lst).filter_application()
##Filter_ndem("H:\\Laser\\Testings\\test\\pallien\\results\\knwldg_pallien_05m_2.tif", "H:\\Laser\\Testings\\test\\pallien\\ndem_05m_pallien.tif",
##"H:\\Laser\\Testings\\test\\pallien\\results\\filtered_pallien_2.tif", dic_lst).filter_application()
Filter_ndem("H:\\Laser\\Testings\\test\\pallien\\results\\knwldg_pallien_05m_3.tif", "H:\\Laser\\Testings\\test\\pallien\\ndem_05m_pallien.tif",
"H:\\Laser\\Testings\\test\\pallien\\results\\filtered_pallien_3.tif", dic_lst).filter_application()

##Filter_ndem("H:\\Laser\\Testings\\test\\trier_west\\results\\knwldg_trier_west_05m_1.tif", "H:\\Laser\\Testings\\test\\trier_west\\ndem_05m_trier_west.tif",
##"H:\\Laser\\Testings\\test\\trier_west\\results\\filtered_trier_west_1.tif", dic_lst).filter_application()
##Filter_ndem("H:\\Laser\\Testings\\test\\trier_west\\results\\knwldg_trier_west_05m_2.tif", "H:\\Laser\\Testings\\test\\trier_west\\ndem_05m_trier_west.tif",
##"H:\\Laser\\Testings\\test\\trier_west\\results\\filtered_trier_west_2.tif", dic_lst).filter_application()
##Filter_ndem("H:\\Laser\\Testings\\test\\trier_west\\results\\knwldg_trier_west_05m_3.tif", "H:\\Laser\\Testings\\test\\trier_west\\ndem_05m_trier_west.tif",
##"H:\\Laser\\Testings\\test\\trier_west\\results\\filtered_trier_west_3.tif", dic_lst).filter_application()