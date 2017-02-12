#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Andy
#
# Created:     30.12.2014
# Copyright:   (c) Andy 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys
import numpy as np
import gdal
from scipy import ndimage
dirname = os.path.split(os.path.abspath(__file__))[0]
os.chdir(dirname)
try:
    from modul.module_math import Internal_Math
except:
    from module_math import Internal_Math


class Green_Knowledge_Engineering():
    def __init__(self, nDEM,  outfolder, knwldg_lst, support = None, num_itr = 1, closing = [], no_Data = -9999, band= 0):
        self.infile_ndem = nDEM
        self.infile_support = support
        self.outfile = outfolder
        self.green_knwldg_lst= knwldg_lst
        self.num_iter = num_itr
        self.closing = closing
        self.no_data = no_Data
        self.band = int(band) + 1
        self.name_ndem  = os.path.split(self.infile_ndem)[1]
        try:
            self.name_support = os.path.split(self.infile_support)[1]
        except:
            self.name_support = None
       ##self.outfile = os.path.join(self.outfolder,"green_knwldg_" + self.name_ndem)


    def green_calc_knowledge(self):
        self.arrary_lst = []
        if self.infile_support != None:
            try:
                IN_support = gdal.Open(self.infile_support)
                IN_nDEM = gdal.Open(self.infile_ndem)

                band_NDVI = IN_support.GetRasterBand(self.band)
                band_nDEM = IN_nDEM.GetRasterBand(1)
                driver = IN_support.GetDriver()

            except:
                self.message = "The data cloudn't be opend!"

            if IN_support.RasterYSize ==  IN_nDEM.RasterYSize and  IN_support.RasterXSize ==  IN_nDEM.RasterXSize:
                rows = IN_support.RasterYSize
                cols = IN_support.RasterXSize

                outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
                outDS.SetGeoTransform(IN_support.GetGeoTransform())
                outDS.SetProjection(IN_support.GetProjection())
            else:
                self.message = "the rasters dont have the same extend!"
        else:
            try:
                IN_nDEM = gdal.Open(self.infile_ndem)
                band_nDEM = IN_nDEM.GetRasterBand(1)
                driver = IN_nDEM.GetDriver()
            except:
                self.message = "The data cloudn't be opend!"

            rows = IN_nDEM.RasterYSize
            cols = IN_nDEM.RasterXSize

            outDS = driver.Create(self.outfile, cols, rows,1, gdal.GDT_Float32)
            outDS.SetGeoTransform(IN_nDEM.GetGeoTransform())
            outDS.SetProjection(IN_nDEM.GetProjection())


        blockSize = 2000
        band_building = outDS.GetRasterBand(1)
        for ii in range(0, rows, blockSize):
            if ii + blockSize < rows:
                numRows = blockSize
            else:
                numRows = rows - ii

            for j in range(0, cols, blockSize):
                if j + blockSize < cols:
                    numCols = blockSize
                else:
                    numCols = cols - j
                """get the data"""
                if self.infile_support != None:
                    test_support = band_NDVI.ReadAsArray(j,ii,numCols,numRows)
                    test_ndem = band_nDEM.ReadAsArray(j,ii,numCols,numRows)
                else:
                    test_ndem = band_nDEM.ReadAsArray(j,ii,numCols,numRows)

                for knw in range(len(self.green_knwldg_lst)):
                    lst_ele = self.green_knwldg_lst[knw]
                    if lst_ele[0] == self.name_ndem:
                        arr = lst_ele[1](test_ndem, lst_ele[2])
                    elif lst_ele[0] == self.name_support:
                        arr = lst_ele[1](test_support, lst_ele[2])
                    else:
                        self.message = "the data was inconstistant"
                    self.arrary_lst.append(arr)

                mask = sum(self.arrary_lst) == len(self.arrary_lst)
                self.arrary_lst =[]
                mask = mask.astype(int)
                for kk in range(self.num_iter):
                    for i in range(len(mask)):
                        for k in range(len(mask[i])):
                            if mask[i][k] == 0:
                                if (i < len(mask)-1 and k < len(mask[i])-1) and i != 0 and k !=0:
                                    value_new  =  [mask[i-1][k-1], mask[i-1][k], mask[i-1][k+1], mask[i][k-1], mask[i][k+1],mask[i+1][k-1], mask[i+1][k], mask[i+1][k+1]]
                                    counter_negativ = value_new.count(0)
                                    counter =         value_new.count(1)
                                elif i != 0 and i < len(mask)-1  and k == len(mask[i]) -1:
                                    value_new = [mask[i-1][k-1], mask[i-1][k], mask[i][k-1], mask[i+1][k-1], mask[i+1][k]]
                                    counter_negativ = value_new.count(0)
                                    counter =         value_new.count(1)
                                elif  i != 0 and i < len(mask)-1 and k == 0:
                                    value_new = [mask[i-1][k], mask[i-1][k+1],  mask[i][k+1], mask[i+1][k], mask[i+1][k+1]]
                                    counter_negativ = value_new.count(0)
                                    counter =         value_new.count(1)
                                elif i == 0 and k != 0 and k < len(mask[i]) -1  :
                                    value_new = [ mask[i][k-1], mask[i][k+1],mask[i+1][k-1], mask[i+1][k], mask[i+1][k+1]]
                                    counter_negativ = value_new.count(0)
                                    counter =         value_new.count(1)
                                elif i == len(mask)-1 and k != 0 and k < len(mask[i])- 1:
                                    value_new = [ mask[i][k-1], mask[i][k+1],mask[i-1][k-1], mask[i-1][k], mask[i-1][k+1]]
                                    counter_negativ = value_new.count(0)
                                    counter =         value_new.count(1)
                                else:
                                    value_new = [1]
                                    counter_negativ = value_new.count(0)
                                    counter =         value_new.count(1)
                                if counter_negativ <= 3:
                                    mask[i][k] = 1
                                elif counter <= 2:
                                    mask[i][k] = 0
                                else:
                                    pass


                """write the data"""
                if len(self.closing) != 0:
                    closed_mask = ndimage.binary_closing(mask,structure=np.ones((self.closing[0],self.closing[1])))
                    band_buildup = np.choose(closed_mask, (self.no_data, test_ndem))
                else:
                    band_buildup = np.choose(mask.astype(bool),(self.no_data, test_ndem))

                band_building.WriteArray(band_buildup, j,ii)
                band_building.SetNoDataValue(self.no_data)


        outDS = None
        IN_nDEM = None
        IN_support = None
        self.message = "Everything worked!"
        return [self.outfile, self.message]

knwldg_lst =   [["ndvi_05m_feyen.tif", Internal_Math()._bigger_, 0.3],["ndem_05m_feyen.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_feyen.tif", Internal_Math()._smaller_,30]]
knwldg_lst_1 = [["ndvi_05m_feyen.tif", Internal_Math()._bigger_, 0.4],["ndem_05m_feyen.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_feyen.tif", Internal_Math()._smaller_,60]]

knwldg_lst_2 =   [["ndvi_05m_gartenfeld.tif", Internal_Math()._bigger_, 0.3],["ndem_05m_gartenfeld.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_gartenfeld.tif", Internal_Math()._smaller_,30]]
knwldg_lst_3 = [["ndvi_05m_gartenfeld.tif", Internal_Math()._bigger_, 0.4],["ndem_05m_gartenfeld.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_gartenfeld.tif", Internal_Math()._smaller_,60]]

knwldg_lst_4 =   [["ndvi_05m_maximin.tif", Internal_Math()._bigger_, 0.3],["ndem_05m_maximin.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_maximin.tif", Internal_Math()._smaller_,30]]
knwldg_lst_5 = [["ndvi_05m_maximin.tif", Internal_Math()._bigger_, 0.4],["ndem_05m_maximin.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_maximin.tif", Internal_Math()._smaller_,60]]

knwldg_lst_6 =   [["ndvi_05m_pallien.tif", Internal_Math()._bigger_, 0.3],["ndem_05m_pallien.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_pallien.tif", Internal_Math()._smaller_,30]]
knwldg_lst_7 = [["ndvi_05m_pallien.tif", Internal_Math()._bigger_, 0.4],["ndem_05m_pallien.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_pallien.tif", Internal_Math()._smaller_,60]]

knwldg_lst_8 =   [["ndvi_05m_trier_west.tif", Internal_Math()._bigger_, 0.3],["ndem_05m_trier_west.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_trier_west.tif", Internal_Math()._smaller_,30]]
knwldg_lst_9 = [["ndvi_05m_trier_west.tif", Internal_Math()._bigger_, 0.4],["ndem_05m_trier_west.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_trier_west.tif", Internal_Math()._smaller_,60]]

#knwldg_lst_2 = [["ndvi_05m_altstadt.tif", Internal_Math()._bigger_, 0.5],["ndem_05m_altstadt.tif", Internal_Math()._bigger_, 2.5],["ndem_05m_altstadt.tif", Internal_Math()._smaller_,60]]
#Green_Knowledge_Engineering(,,,,,)
Green_Knowledge_Engineering("E:\\Laser\\Testings\\test\\altstadt\\ndem_05m_altstadt.tif","E:\\Laser\\Testings\\test\\altstadt\\results\\green_knwdg_altstadt_1.tif",
knwldg_lst,"E:\\Laser\\Testings\\test\\altstadt\\ndvi_05m_altstadt.tif",1,[3,3]).green_calc_knowledge()
##Green_Knowledge_Engineering("E:\\Laser\\Testings\\test\\altstadt\\ndem_05m_altstadt.tif","E:\\Laser\\Testings\\test\\altstadt\\results\\green_knwdg_altstadt_2.tif",
## knwldg_lst_1,"E:\\Laser\\Testings\\test\\altstadt\\ndvi_05m_altstadt.tif",1,[3,3]).green_calc_knowledge()
##Green_Knowledge_Engineering("E:\\Laser\\Testings\\test\\altstadt\\ndem_05m_altstadt.tif","E:\\Laser\\Testings\\test\\altstadt\\results\\green_knwdg_altstadt_3.tif",
## knwldg_lst_2,"E:\\Laser\\Testings\\test\\altstadt\\ndvi_05m_altstadt.tif",1,[3,3]).green_calc_knowledge()

##
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\feyen\\ndem_05m_feyen.tif","H:\\Laser\\Testings\\test\\feyen\\results\\green_knwdg_feyen_1.tif",
## knwldg_lst,"H:\\Laser\\Testings\\test\\feyen\\ndvi_05m_feyen.tif",1,[3,3]).green_calc_knowledge()
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\feyen\\ndem_05m_feyen.tif","H:\\Laser\\Testings\\test\\feyen\\results\\green_knwdg_feyen_2.tif",
## knwldg_lst_1,"H:\\Laser\\Testings\\test\\feyen\\ndvi_05m_feyen.tif",1,[3,3]).green_calc_knowledge()
##
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\gartenfeld\\ndem_05m_gartenfeld.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results\\green_knwdg_gartenfeld_1.tif",
## knwldg_lst_2,"H:\\Laser\\Testings\\test\\gartenfeld\\ndvi_05m_gartenfeld.tif",1,[3,3]).green_calc_knowledge()
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\gartenfeld\\ndem_05m_gartenfeld.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results\\green_knwdg_gartenfeld_2.tif",
## knwldg_lst_3,"H:\\Laser\\Testings\\test\\gartenfeld\\ndvi_05m_gartenfeld.tif",1,[3,3]).green_calc_knowledge()
##
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\maximin\\ndem_05m_maximin.tif","H:\\Laser\\Testings\\test\\maximin\\results\\green_knwdg_maximin_1.tif",
## knwldg_lst_4,"H:\\Laser\\Testings\\test\\maximin\\ndvi_05m_maximin.tif",1,[3,3]).green_calc_knowledge()
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\maximin\\ndem_05m_maximin.tif","H:\\Laser\\Testings\\test\\maximin\\results\\green_knwdg_maximin_2.tif",
## knwldg_lst_5,"H:\\Laser\\Testings\\test\\maximin\\ndvi_05m_maximin.tif",1,[3,3]).green_calc_knowledge()
##
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\pallien\\ndem_05m_pallien.tif","H:\\Laser\\Testings\\test\\pallien\\results\\green_knwdg_pallien_1.tif",
## knwldg_lst_6,"H:\\Laser\\Testings\\test\\pallien\\ndvi_05m_pallien.tif",1,[3,3]).green_calc_knowledge()
##Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\pallien\\ndem_05m_pallien.tif","H:\\Laser\\Testings\\test\\pallien\\results\\green_knwdg_pallien_2.tif",
## knwldg_lst_7,"H:\\Laser\\Testings\\test\\pallien\\ndvi_05m_pallien.tif",1,[3,3]).green_calc_knowledge()
##
Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\trier_west\\ndem_05m_trier_west.tif","H:\\Laser\\Testings\\test\\trier_west\\results\\green_knwdg_trier_west_1.tif",
 knwldg_lst_8,"H:\\Laser\\Testings\\test\\trier_west\\ndvi_05m_trier_west.tif",1,[3,3]).green_calc_knowledge()
Green_Knowledge_Engineering("H:\\Laser\\Testings\\test\\trier_west\\ndem_05m_trier_west.tif","H:\\Laser\\Testings\\test\\trier_west\\results\\green_knwdg_trier_west_2.tif",
 knwldg_lst_9,"H:\\Laser\\Testings\\test\\trier_west\\ndvi_05m_trier_west.tif",1,[3,3]).green_calc_knowledge()