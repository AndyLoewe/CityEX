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
from osgeo import gdal
from osgeo import osr
from osgeo import ogr


class Tree_Top_Detection():
    def __init__(self, infile_green_knwlgd, Outfolder, windowsize, crit_percent, crit_height = None, EPSG = 32632):
        self.infile_green = infile_green_knwlgd
        self.outfolder = Outfolder
        self.windowsize = int(windowsize)
        self.crit_percent = float(crit_percent/100.0)
        self.crit_height = crit_height
        self.epsg = int(EPSG)

        self.name_green_knwlgd = os.path.split(self.infile_green)[1]
        self.outfile = os.path.join(self.outfolder,"tree_tops_" + self.name_green_knwlgd[:-4] + ".shp")

    def tree_detection(self):
        # predefined values, values which need to be reseted for each run
        id= 0
        double_tree = dict()
        double_tree_control = list()
        nameing_double = 0
        drv = ogr.GetDriverByName("ESRI Shapefile")
        # check if the
        if os.path.exists(self.outfile):
            print "fuff"
            drv.DeleteDataSource(self.outfile)
            #self.message = "The shapefile already exists please chose another name."
        layername_green = "tree_tops"
        datasource_green = drv.CreateDataSource(self.outfile)
        green_layer = datasource_green.CreateLayer(layername_green, geom_type= ogr.wkbPoint)

        fieldDefn = ogr.FieldDefn("id", ogr.OFTInteger)
        green_layer.CreateField(fieldDefn)


        # read the filtered data
        green_infile = gdal.Open(self.infile_green)
        green_filterd = green_infile.GetRasterBand(1)
        green_band = green_filterd.ReadAsArray()

        geotransobj = green_infile.GetGeoTransform()
        rows = green_infile.RasterYSize
        cols = green_infile.RasterXSize

        ref = osr.SpatialReference()
        ref.ImportFromEPSG(self.epsg)
        file = open(os.path.join(self.outfile[:-4] + ".prj"), "w")
        file.write(ref.ExportToWkt())
        file.close()
        ref = None
        if self.crit_height == None or self.crit_height == 0:
            green_mean = green_band[green_band != green_filterd.GetNoDataValue()].mean()
            self.crit_height = green_mean - np.std(green_band[green_band != green_filterd.GetNoDataValue()])
        else:
            self.crit_height = float(self.crit_height)

        for i in range(len(green_band)):
            for k in range(len(green_band[i])):
                po_tree_top = green_band[i][k]
                if po_tree_top != green_filterd.GetNoDataValue():
                    if   i < (len(green_band) - self.windowsize) -1 and k < len(green_band[i])- self.windowsize -1 and i > self.windowsize +1 and k > self.windowsize + 1:
                        values  = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 + 2 * self.windowsize, 1 + 2 * self.windowsize)
                    elif i == 0 and k > self.windowsize + 1 and k < len(green_band[i])- self.windowsize -1:
                        values = green_filterd.ReadAsArray(k - self.windowsize, 0, 1 + 2 * self.windowsize, 1 + self.windowsize)
                    elif i == 0 and k == len(green_band[i]) -1:
                        values = green_filterd.ReadAsArray(k - self.windowsize, 0, 1 +     self.windowsize, 1 + self.windowsize)
                    elif i == 0 and k == 0:
                        values = green_filterd.ReadAsArray(0, 0,              1 +     self.windowsize, 1 + self.windowsize)
                    elif i < (len(green_band) - self.windowsize) -1 and i > self.windowsize +1 and k == 0:
                        values = green_filterd.ReadAsArray(0, i - self.windowsize, 1 + 2 * self.windowsize, 1 + self.windowsize)
                    elif i == len(green_band) -1 and k == len(green_band) -1:
                        values = green_filterd.ReadAsArray(0, i - self.windowsize, 1 +     self.windowsize, 1 + self.windowsize)
                    elif i == len(green_band) -1 and k > self.windowsize + 1 and k < len(green_band[i])- self.windowsize -1:
                        values = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 + 2 * self.windowsize, 1 +     self.windowsize)
                    elif i == len(green_band) -1 and k == len(green_band[i]) -1:
                        values = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 +     self.windowsize, 1 +     self.windowsize)
                    elif  i > self.windowsize +1 and i < (len(green_band) - self.windowsize) -1 and k == len(green_band[i]) -1:
                        values = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 +     self.windowsize, 1 + 2 * self.windowsize)
                else:
                    values = np.ones((1,1))
                    values[values==1] = 9999

                if values.max() == po_tree_top and \
                (values != green_filterd.GetNoDataValue()).sum() > len(values) * len(values[0]) * self.crit_percent \
                and (values == values.max()).sum() == 1 \
                and po_tree_top > self.crit_height:
                    seed_x = geotransobj[0] + k * geotransobj[1]
                    seed_y = geotransobj[3] + i * geotransobj[5]
                    x = int(seed_x) + ((seed_x - int(seed_x))/2)
                    y = int(seed_y) + ((seed_y - int(seed_y))/2)
                    point = ogr.Geometry(ogr.wkbPoint)
                    point.AddPoint(x,y)
                    feat_def = green_layer.GetLayerDefn()
                    feat = ogr.Feature(feat_def)
                    feat.SetGeometry(point)
                    feat.SetField("id", id)
                    #feat.SetField("count", green_band[i][k])
                    green_layer.CreateFeature(feat)
                    id +=1

                elif values.max() == po_tree_top and \
                (values != green_filterd.GetNoDataValue()).sum() > len(values) * len(values[1])* self.crit_percent \
                and (values == values.max()).sum() > 1 and po_tree_top > self.crit_height:
                    for ii in range(len(values)):
                        for kk in range(len(values[ii])):
                            if values[ii][kk] == values.max():
                                """umwandlung in echte bild  indizies"""
                                if k - self.windowsize - 1 >= 0 and i - self.windowsize - 1 >= 0:
                                    i_max = i - self.windowsize + ii
                                    k_max = k - self.windowsize + kk
                                ## doo stuff
                                elif k - self.windowsize - 1 < 0 and i - self.windowsize - 1 < 0:
                                    i_max = ii
                                    k_max = kk
                                elif k - self.windowsize - 1 < 0 and i - self.windowsize - 1 >= 0:
                                    i_max = i - self.windowsize + ii
                                    k_max = kk
                                elif k - self.windowsize - 1 >= 0 and i - self.windowsize - 1 < 0:
                                    i_max = ii
                                    k_max = k - self.windowsize + kk
                                if not double_tree.has_key(str(nameing_double)):
                                    double_tree[str(nameing_double)] = [(i_max, k_max)]
                                else:
                                    double_tree[str(nameing_double)].append((i_max, k_max))
                    nameing_double += 1


        for key in double_tree.keys():
            chooser_list = []
            for chooser in range(len(double_tree[key])):
                i = double_tree[key][chooser][0]
                k = double_tree[key][chooser][1]
                if   i < (len(green_band) - self.windowsize) -1 and k < len(green_band[i])- self.windowsize -1 and i > self.windowsize +1 and k > self.windowsize + 1:
                    arr_double_tree  = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 + 2 * self.windowsize, 1 + 2 * self.windowsize)
                elif i == 0 and k > self.windowsize + 1 and k < len(green_band[i])- windowsize -1:
                    arr_double_tree = green_filterd.ReadAsArray(k - self.windowsize, 0, 1 + 2 * self.windowsize, 1 + self.windowsize)
                elif i == 0 and k == len(green_band[i]) -1:
                    arr_double_tree = green_filterd.ReadAsArray(k - self.windowsize, 0, 1 +     self.windowsize, 1 + self.windowsize)
                elif i == 0 and k == 0:
                    arr_double_tree = green_filterd.ReadAsArray(0, 0,              1 +     self.windowsize, 1 + self.windowsize)
                elif i < (len(green_band) - self.windowsize) -1 and i > self.windowsize +1 and k == 0:
                    arr_double_tree = green_filterd.ReadAsArray(0, i - self.windowsize, 1 + 2 * self.windowsize, 1 + self.windowsize)
                elif i == len(green_band) -1 and k == len(green_band) -1:
                    arr_double_tree = green_filterd.ReadAsArray(0, i - self.windowsize, 1 +     self.windowsize, 1 + self.windowsize)
                elif i == len(green_band) -1 and k > self.windowsize + 1 and k < len(green_band[i])- self.windowsize -1:
                    arr_double_tree = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 + 2 * self.windowsize, 1 +     self.windowsize)
                elif i == len(green_band) -1 and k == len(green_band[i]) -1:
                    arr_double_tree = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 +     self.windowsize, 1 +     self.windowsize)
                elif  i > self.windowsize +1 and i < (len(green_band) - self.windowsize) -1 and k == len(green_band[i]) -1:
                    arr_double_tree = green_filterd.ReadAsArray(k - self.windowsize, i - self.windowsize, 1 +     self.windowsize, 1 + 2 * self.windowsize)
                chooser_list.append(arr_double_tree[arr_double_tree !=  green_filterd.GetNoDataValue()].sum())
            tree_top = double_tree[key][chooser_list.index(max(chooser_list))]
            try:
                if double_tree_control.index(tree_top) >=0:
                    pass
            except ValueError:
                seed_x = geotransobj[0] + tree_top[1] * geotransobj[1]
                seed_y = geotransobj[3] + tree_top[0] * geotransobj[5]
                x = int(seed_x) + ((seed_x - int(seed_x)) /2)
                y = int(seed_y) + ((seed_y - int(seed_y)) /2)
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(x,y)
                feat_def = green_layer.GetLayerDefn()
                feat = ogr.Feature(feat_def)
                feat.SetGeometry(point)
                feat.SetField("id", id)
                #feat.SetField("count", green_band[i][k])
                green_layer.CreateFeature(feat)
                id +=1
                double_tree_control.append(tree_top)
        green_infile = None
        green_layer = None
        green_band = None
        feat = None
        point = None
        datasource_green = None


#Tree_Top_Detection("E:\\Laser\\Testings\\test\\altstadt\\results\green_knwdg_altstadt_1.tif", "E:\\Laser\\Testings\\test\\altstadt\\results\\", 7, 50).tree_detection()
##Tree_Top_Detection("E:\\Laser\\Testings\\test\\altstadt\\results\green_knwdg_altstadt_2.tif","E:\\Laser\\Testings\\test\\altstadt\\results\\", 7, 50).tree_detection()
##Tree_Top_Detection("E:\\Laser\\Testings\\test\\altstadt\\results\green_knwdg_altstadt_3.tif","E:\\Laser\\Testings\\test\\altstadt\\results\\", 7, 50).tree_detection()
#Tree_Top_Detection("H:\\Laser\\Testings\\test\\altstadt\\results\green_knw_altstadt_05m.tif","H:\\Laser\\Testings\\test\\altstadt\\results", 7, 30)
#Tree_Top_Detection("H:\\Laser\\Testings\\test\\altstadt\\results\green_knw_altstadt_05m.tif","H:\\Laser\\Testings\\test\\altstadt\\results", 7, 0)

##Tree_Top_Detection("H:\\Laser\\Testings\\test\\feyen\\results\green_knwdg_feyen_1.tif","H:\\Laser\\Testings\\test\\feyen\\results\\", 7, 50).tree_detection()
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\feyen\\results\green_knwdg_feyen_2.tif","H:\\Laser\\Testings\\test\\feyen\\results\\", 7, 50).tree_detection()
##
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\gartenfeld\\results\green_knwdg_gartenfeld_1.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results\\", 7, 50).tree_detection()
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\gartenfeld\\results\green_knwdg_gartenfeld_2.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results\\", 7, 50).tree_detection()
##
##
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\maximin\\results\green_knwdg_maximin_1.tif","H:\\Laser\\Testings\\test\\maximin\\results\\", 7, 50).tree_detection()
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\maximin\\results\green_knwdg_maximin_2.tif","H:\\Laser\\Testings\\test\\maximin\\results\\", 7, 50).tree_detection()
##
##
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\pallien\\results\green_knwdg_pallien_1.tif","H:\\Laser\\Testings\\test\\pallien\\results\\", 7, 50).tree_detection()
##Tree_Top_Detection("H:\\Laser\\Testings\\test\\pallien\\results\green_knwdg_pallien_2.tif","H:\\Laser\\Testings\\test\\pallien\\results\\", 7, 50).tree_detection()
##
##
Tree_Top_Detection("H:\\Laser\\Testings\\test\\trier_west\\results\green_knwdg_trier_west_1.tif","H:\\Laser\\Testings\\test\\trier_west\\results\\", 7, 50).tree_detection()
Tree_Top_Detection("H:\\Laser\\Testings\\test\\trier_west\\results\green_knwdg_trier_west_2.tif","H:\\Laser\\Testings\\test\\trier_west\\results\\", 7, 50).tree_detection()




