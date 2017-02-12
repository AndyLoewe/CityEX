#-------------------------------------------------------------------------------
# Name:        module_raster2poly
# Purpose:     creatibg and cleaning up of shapefiles
#
# Author:      s6anloew
#
# Created:     10.11.2014
# Copyright:   (c) s6anloew 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys
from osgeo import gdal,ogr,osr,gdalnumeric
import numpy as np


class Raster_2_Poly():
    def __init__(self, inFile, outFolder):
        self.infile =  inFile
        self.oufolder = outFolder
        os.chdir(str(self.oufolder))

        if os.path.exists(self.infile)==False:
            self.message =  "File " + self.infile + " does not exist"
            print 'File ' + self.infile + " does not exist"
            sys.exit(1)

        else:
            self.infile_knwlgd = gdal.Open(self.infile, gdal.GA_ReadOnly)
            self.fileoutput= os.path.join(outFolder, "buildings_" + os.path.split(self.infile)[1][0:-4] + ".shp" )


        if self.infile_knwlgd is None:
            self.message =  "Could not open " + self.infile
            sys.exit(1)
        else:
            self.raster_driver = self.infile_knwlgd.GetDriver()
            self.raster_driver.Register()

    def polygon(self,Min_Area,EPSG):
        self.min_area = Min_Area
        self.epsg  =EPSG

        try:
            self.band_knwlg = self.infile_knwlgd.GetRasterBand(1)
        except RuntimeError, e:
            self.message = "Band ( %i ) not found" % band_num
            sys.exit(1)
        #elevation = self.band_knwlg.ReadAsArray()

        dst_layername = os.path.split(self.fileoutput)[1][0:-4]
        self.poly_driver = ogr.GetDriverByName("ESRI Shapefile")

        temp_shape = self.poly_driver.CreateDataSource("temp.shp")
        dst_layer = temp_shape.CreateLayer("temp", srs = None )
        gdal.Polygonize(self.band_knwlg, self.band_knwlg, dst_layer, -1, [], callback=None)

        ref = osr.SpatialReference()
        ref.ImportFromEPSG(self.epsg)
        file = open("temp.prj", "w")
        file.write(ref.ExportToWkt())
        file.close()
        dst_layer =  None
        temp_shape = None


        dataSource = self.poly_driver.Open("temp.shp", 1)
        layer_in = dataSource.GetLayer(0)

        field_def_area = ogr.FieldDefn("area", ogr.OFTReal)
        field_def_id   = ogr.FieldDefn("id", ogr.OFTInteger)

        layer_in.CreateField(field_def_id)
        layer_in.CreateField(field_def_area)

        for i in range(layer_in.GetFeatureCount()) :
            feat = layer_in.GetFeature(i)
            geom = feat.GetGeometryRef()
            area = geom.Area()
            feat.SetField("id", int(i))
            feat.SetField("area", float(area))
            layer_in.SetFeature(feat)


        end_shape = self.poly_driver.CreateDataSource(dst_layername + ".shp")
        layer = end_shape.CreateLayer(dst_layername,geom_type=ogr.wkbPolygon)


        layer.CreateField(field_def_id)
        layer.CreateField(field_def_area)

        file = open(dst_layername + ".prj", "w")
        file.write(ref.ExportToWkt())
        file.close()

        featureDefn = layer.GetLayerDefn()

        for i in range(layer_in.GetFeatureCount()):
            feat = layer_in.GetFeature(i)
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(feat.GetGeometryRef())
            if feat.GetGeometryRef().Area() > float(self.min_area):
                outFeature.SetField('id', feat.GetField('id'))
                outFeature.SetField('area', feat.GetField('area'))
                layer.CreateFeature(outFeature)

        layer_in = None
        dataSource = None
        end_shape = None
        layer = None
        # remove the temp data
        os.remove(os.path.join(self.oufolder, "temp.shx"))
        os.remove(os.path.join(self.oufolder, "temp.prj"))
        os.remove(os.path.join(self.oufolder, "temp.dbf"))
        os.remove(os.path.join(self.oufolder, "temp.shp"))


##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\altstadt\\results\\knw_altstadt_05m_filter.tif","H:\\Laser\\Testings\\test\\altstadt\\results").polygon(70,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\feyen\\results\\knw_feyen_05m_filter.tif","H:\\Laser\\Testings\\test\\feyen\\results").polygon(70,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\gartenfeld\\results\\knw_gartenfeld_05m_filter.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results").polygon(70,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\maximin\\results\\knw_maximin_05m_filter.tif","H:\\Laser\\Testings\\test\\maximin\\results").polygon(70,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\trier_west\\results\\knw_trier_west_05m_filter.tif","H:\\Laser\\Testings\\test\\trier_west\\results").polygon(70,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\pallien\\results\\knw_pallien_05m_filter.tif","H:\\Laser\\Testings\\test\\pallien\\results").polygon(70,32632)










##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\altstadt\\results\\reclass_altstadt_1.tif","H:\\Laser\\Testings\\test\\altstadt\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\altstadt\\results\\reclass_altstadt_2.tif","H:\\Laser\\Testings\\test\\altstadt\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\altstadt\\results\\reclass_altstadt_3.tif","H:\\Laser\\Testings\\test\\altstadt\\results").polygon(99,32632)
##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\feyen\\results\\reclass_feyen_1.tif","H:\\Laser\\Testings\\test\\feyen\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\feyen\\results\\reclass_feyen_2.tif","H:\\Laser\\Testings\\test\\feyen\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\feyen\\results\\reclass_feyen_3.tif","H:\\Laser\\Testings\\test\\feyen\\results").polygon(80,32632)
##
##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\gartenfeld\\results\\reclass_gartenfeld_1.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\gartenfeld\\results\\reclass_gartenfeld_2.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\gartenfeld\\results\\reclass_gartenfeld_3.tif","H:\\Laser\\Testings\\test\\gartenfeld\\results").polygon(80,32632)
##
##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\maximin\\results\\reclass_maximin_1.tif","H:\\Laser\\Testings\\test\\maximin\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\maximin\\results\\reclass_maximin_2.tif","H:\\Laser\\Testings\\test\\maximin\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\maximin\\results\\reclass_maximin_3.tif","H:\\Laser\\Testings\\test\\maximin\\results").polygon(80,32632)
##
##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\pallien\\results\\reclass_pallien_1.tif","H:\\Laser\\Testings\\test\\pallien\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\pallien\\results\\reclass_pallien_2.tif","H:\\Laser\\Testings\\test\\pallien\\results").polygon(80,32632)
Raster_2_Poly("H:\\Laser\\Testings\\test\\pallien\\results\\reclass_pallien_3.tif","H:\\Laser\\Testings\\test\\pallien\\results").polygon(60,32632)
##
##Raster_2_Poly("H:\\Laser\\Testings\\test\\trier_west\\results\\reclass_trier_west_1.tif","H:\\Laser\\Testings\\test\\trier_west\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\trier_west\\results\\reclass_trier_west_2.tif","H:\\Laser\\Testings\\test\\trier_west\\results").polygon(80,32632)
##Raster_2_Poly("H:\\Laser\\Testings\\test\\trier_west\\results\\reclass_trier_west_3.tif","H:\\Laser\\Testings\\test\\trier_west\\results").polygon(80,32632)
