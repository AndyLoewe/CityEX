###-------------------------------------------------------------------------------
### Name:        module1
### Purpose:
###
### Author:      s6anloew
###
### Created:     12.09.2014
### Copyright:   (c) s6anloew 2014
### Licence:     <your licence>
###-------------------------------------------------------------------------------
##import os, sys
##import numpy as np
##import gdal
##dirname = os.path.split(os.path.abspath(__file__))[0]
##os.chdir(dirname)
##try:
##    from modul.modul_math import Internal_Math
##except:
##    from modul_math import Internal_Math
##
##
##class Knowledge_Engineering():
##    def __init__(self, nDEM,  outfolder, knwldg_lst, support = None, no_Data = -9999):
##        self.infile_ndem = nDEM
##        self.outfolder = outfolder
##        self.knwldg_lst= knwldg_lst
##        self.no_data = no_Data
##        self.name_ndem  = os.path.split(str(self.infile_ndem))[1]
##        print self.name_ndem, self.outfolder
##        self.outfile = os.path.join(self.outfolder,"knwldg_" + self.name_ndem)
##
##        if support != None:
##             self.infile_support = support
##             self.name_support = os.path.split(self.infile_support)[1]
##        else:
##            self.infile_support = None
##
##
##
##    def calc_knowledge(self):
##        self.arrary_lst = []
##        try:
##
##            if self.infile_support != None:
##                IN_support = gdal.Open(self.infile_suppor)
##                IN_nDEM = gdal.Open(self.infile_ndem)
##
##                band_NDVI = IN_support.GetRasterBand(1)
##                band_nDEM = IN_nDEM.GetRasterBand(1)
##                driver = IN_nDEM.GetDriver()
##                if IN_support.RasterYSize ==  IN_nDEM.RasterYSize and  IN_support.RasterXSize ==  IN_nDEM.RasterXSize:
##                    rows = IN_nDEM.RasterYSize
##                    cols = IN_nDEM.RasterXSize
##
##                    outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
##                    outDS.SetGeoTransform(IN_nDEM.GetGeoTransform())
##                    outDS.SetProjection(IN_nDEM.GetProjection())
##
##                    blockSize = 1000
##                    band_building = outDS.GetRasterBand(1)
##                    for i in range(0, rows, blockSize):
##                        if i + blockSize < rows:
##                            numRows = blockSize
##                        else:
##                            numRows = rows - i
##
##                        for j in range(0, cols, blockSize):
##                            if j + blockSize < cols:
##                                numCols = blockSize
##                            else:
##                                numCols = cols - j
##                            """get the data"""
##                            test_support = band_NDVI.ReadAsArray(j,i,numCols,numRows)
##                            test_ndem = band_nDEM.ReadAsArray(j,i,numCols,numRows)
##
##                            for knw in range(len(self.knwldg_lst)):
##                                lst_ele = self.knwldg_lst[knw]
##                                if lst_ele[0] == self.name_ndem:
##                                    arr = lst_ele[1](test_ndem, lst_ele[2])
##                                elif lst_ele[0] == self.name_support:
##                                    arr = lst_ele[1](test_support, lst_ele[2])
##                                else:
##                                    self.message = "the data was inconstistant"
##                                self.arrary_lst.append(arr)
##
##                            mask = sum(self.arrary_lst) == len(self.arrary_lst)
##                            self.arrary_lst =[]
##                            buildup = np.choose(mask,(self.no_data, test_ndem))
##                            """write the data"""
##                            band_building.WriteArray(buildup, j,i)
##                            band_building.SetNoDataValue(self.no_data)
##                    outDS = None
##                    IN_nDEM = None
##                    IN_support = None
##                return [self.outfile, self.message]
##            else:
##                #IN_support = gdal.Open(self.infile_suppor)
##                IN_nDEM = gdal.Open(self.infile_ndem)
##
##                #band_NDVI = IN_support.GetRasterBand(1)
##                band_nDEM = IN_nDEM.GetRasterBand(1)
##                driver = IN_nDEM.GetDriver()
##
##
##                rows = IN_nDEM.RasterYSize
##                cols = IN_nDEM.RasterXSize
##
##                outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
##                outDS.SetGeoTransform(IN_nDEM.GetGeoTransform())
##                outDS.SetProjection(IN_nDEM.GetProjection())
##
##                blockSize = 1000
##                band_building = outDS.GetRasterBand(1)
##                for i in range(0, rows, blockSize):
##                    if i + blockSize < rows:
##                        numRows = blockSize
##                    else:
##                        numRows = rows - i
##
##                    for j in range(0, cols, blockSize):
##                        if j + blockSize < cols:
##                            numCols = blockSize
##                        else:
##                            numCols = cols - j
##                        """get the data"""
##                        #test_support = band_NDVI.ReadAsArray(j,i,numCols,numRows)
##                        test_ndem = band_nDEM.ReadAsArray(j,i,numCols,numRows)
##
##                        for knw in range(len(self.knwldg_lst)):
##                            lst_ele = self.knwldg_lst[knw]
##                            if lst_ele[0] == self.name_ndem:
##                                arr = lst_ele[1](test_ndem, lst_ele[2])
####                            elif lst_ele[0] == self.name_support:
####                                arr = lst_ele[1](test_support, lst_ele[2])
##                            else:
##                                self.message = "the data was inconstistant"
##                            self.arrary_lst.append(arr)
##
##                        mask = sum(self.arrary_lst) == len(self.arrary_lst)
##                        self.arrary_lst =[]
##                        buildup = np.choose(mask,(self.no_data, test_ndem))
##                        """write the data"""
##                        band_building.WriteArray(buildup, j,i)
##                        band_building.SetNoDataValue(self.no_data)
##                outDS = None
##                IN_nDEM = None
##                IN_support = None
##
##        except:
##            self.message = "The data cloudn't be opend!"
##        return [self.outfile, self.message]
#-------------------------------------------------------------------------------
# Name:        module_knwlgd
# Purpose:
#
# Author:      s6anloew
#
# Created:     12.09.2014
# Copyright:   (c) s6anloew 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys
import numpy as np
import gdal
dirname = os.path.split(os.path.abspath(__file__))[0]
os.chdir(dirname)
try:
    from modul.module_math import Internal_Math
except:
    from module_math import Internal_Math


class Knowledge_Engineering():
    def __init__(self, nDEM,  outfolder, knwldg_lst, support = None, no_Data = -9999, band = 0):
        Internal_Math()
        self.infile_ndem = nDEM
        self.infile_support = support
        self.outfile = outfolder
        self.knwldg_lst= knwldg_lst
        self.no_data = no_Data
        self.band = int(band) + 1
        self.name_ndem  = os.path.split(self.infile_ndem)[1]
        try:
            self.name_support = os.path.split(self.infile_support)[1]
        except:
            self.name_support = None
        #self.outfile = os.path.join(self.outfolder,"knwldg_" + self.name_ndem)

    def calc_knowledge(self):
        self.arrary_lst = []
        if self.infile_support != None:
            print "here"
            try:
                IN_support = gdal.Open(self.infile_support)
                IN_nDEM = gdal.Open(self.infile_ndem)

                band_NDVI = IN_support.GetRasterBand(self.band)
                band_nDEM = IN_nDEM.GetRasterBand(1)
                driver = IN_support.GetDriver()
                print "here 1"

            except:
                self.message = "The data cloudn't be opend!"

            if IN_support.RasterYSize ==  IN_nDEM.RasterYSize and  IN_support.RasterXSize ==  IN_nDEM.RasterXSize:
                rows = IN_support.RasterYSize
                cols = IN_support.RasterXSize
            else:
                self.message = "the rasters dont have the same extend!"
        else:
            try:
                IN_nDEM = gdal.Open(self.infile_ndem)
                band_nDEM = IN_nDEM.GetRasterBand(1)
                driver = IN_nDEM.GetDriver()
                print "here 2"
            except:
                self.message = "The data cloudn't be opend!"

            rows = IN_nDEM.RasterYSize
            cols = IN_nDEM.RasterXSize

            outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
            outDS.SetGeoTransform(IN_nDEM.GetGeoTransform())
            outDS.SetProjection(IN_nDEM.GetProjection())

            outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
            outDS.SetGeoTransform(IN_support.GetGeoTransform())
            outDS.SetProjection(IN_support.GetProjection())

            blockSize = 2000
            band_building = outDS.GetRasterBand(1)
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
                    if self.infile_support != None:
                        test_support = band_NDVI.ReadAsArray(j,i,numCols,numRows)
                        test_ndem = band_nDEM.ReadAsArray(j,i,numCols,numRows)
                    else:
                        test_ndem = band_nDEM.ReadAsArray(j,i,numCols,numRows)

                    for knw in range(len(self.knwldg_lst)):
                        lst_ele = self.knwldg_lst[knw]
                        if lst_ele[0] == self.name_ndem:
                            arr = lst_ele[1](test_ndem, lst_ele[2])
                        elif lst_ele[0] == self.name_support:
                            arr = lst_ele[1](test_support, lst_ele[2])
                        else:
                            self.message = "the data was inconstistant"
                        self.arrary_lst.append(arr)

                    mask = sum(self.arrary_lst) == len(self.arrary_lst)
                    self.arrary_lst =[]
                    buildup = np.choose(mask,(self.no_data, test_ndem))
                    """write the data"""
                    band_building.WriteArray(buildup, j,i)
                    band_building.SetNoDataValue(self.no_data)


            outDS = None
            IN_nDEM = None
            IN_support = None

            self.message = "everything worked"
        return [self.outfile, self.message]



knwldg_lst =   [["ndvi_05m_altstadt.tif", Internal_Math()._smaller_, 0.2],["ndvi_05m_altstadt.tif", Internal_Math()._bigger_, - 0.3],
["ndem_05m_altstadt.tif", Internal_Math()._bigger_, 5],["ndem_05m_altstadt.tif", Internal_Math()._smaller_,60]]

knwldg_lst_1 = [["ndvi_05m_altstadt.tif", Internal_Math()._smaller_, 0.3],["ndvi_05m_altstadt.tif", Internal_Math()._bigger_, - 0.4],
["ndem_05m_altstadt.tif", Internal_Math()._bigger_, 4],["ndem_05m_altstadt.tif", Internal_Math()._smaller_,60]]

knwldg_lst_2 = [["ndvi_05m_altstadt.tif", Internal_Math()._smaller_, 0.1],["ndvi_05m_altstadt.tif", Internal_Math()._bigger_, -0.5],
["ndem_05m_altstadt.tif", Internal_Math()._bigger_, 3],["ndem_05m_altstadt.tif", Internal_Math()._smaller_,60]]



##Knowledge_Engineering("H:\\Laser\\Testings\\test\\altstadt\\ndem_05m_altstadt.tif",
##"H:\\Laser\\Testings\\test\\altstadt\\results\\knwldg_altstadt_05m_1.tif"
##, knwldg_lst, "H:\\Laser\\Testings\\test\\altstadt\\ndvi_05m_altstadt.tif").calc_knowledge()
##Knowledge_Engineering("H:\\Laser\\Testings\\test\\altstadt\\ndem_05m_altstadt.tif",
##"H:\\Laser\\Testings\\test\\altstadt\\results\\knwldg_altstadt_05m_2.tif"
##, knwldg_lst_1, "H:\\Laser\\Testings\\test\\altstadt\\ndvi_05m_altstadt.tif").calc_knowledge()
Knowledge_Engineering("H:\\Laser\\Testings\\test\\pallien\\ndem_05m_pallien.tif",
"H:\\Laser\\Testings\\test\\pallien\\results\\knwldg_pallien_05m_3.tif"
, knwldg_lst_2, "H:\\Laser\\Testings\\test\\pallien\\ndvi_05m_pallien.tif").calc_knowledge()



