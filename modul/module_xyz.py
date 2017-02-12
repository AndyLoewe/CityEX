#-------------------------------------------------------------------------------
# Name:        modul_xyz
# Purpose:
#
# Author:      s6anloew
#
# Created:     03.09.2014
# Copyright:   (c) s6anloew 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy as np
#import matplotlib.mlab as ml
import scipy.interpolate as il
import gdal
from osr import SpatialReference
import os, sys


class Create_elevation_models():
    def __init__(self, xyz_dem, xyz_dom, outFolder, cellSize, EPSG,**args):
        self.infile_dem = xyz_dem
        self.infile_dom = xyz_dom
        self.outfolder = str(outFolder)
        self.cellsize = float(cellSize)
        self.epsg = int(EPSG)
        self.data_lst = []
        self.data_out_lst= []
        if type(self.infile_dem) != list or type(self.infile_dom) != list:
            self.data_lst = [str(self.infile_dem), str(self.infile_dom)]
        else:
            if len(self.infile_dem) == len(self.infile_dom):
                for i in range(len(self.infile_dem)):
                    self.data_lst.append(str(self.infile_dem[i]))
                    self.data_lst.append(str(self.infile_dom[i]))
            else:
                self.message = "you need the same amount of first and last returns"


    def calc_elevation_models(self):
        for item in range(len(self.data_lst)):
            file_name = self.data_lst[item].strip(".xyz")
            self.outfile = os.path.join(self.outfolder,file_name + ".tif")
            x,y,z = np.loadtxt(self.data_lst[item], skiprows=1,unpack = True)
            xmin,xmax,ymin,ymax = [min(x),max(x),min(y),max(y)]
            #size of the grid
            nx = (int(xmax - xmin + 1))
            ny = (int(ymax - ymin + 1))

            # Generate a regular grid to interpolate the data.
            xi = np.linspace(xmin, xmax, nx)
            yi = np.linspace(ymin, ymax, ny)
            xi, yi = np.meshgrid(xi, yi)
            # adding the z - values
            zi = il.griddata((x, y), z, (xi, yi),method='nearest') # linear, cubic, nearest


            #---------------  Write to GeoTIFF ------------------------
            nrows,ncols = np.shape(zi)
            xres = (xmax-xmin)/float(ncols)
            yres = (ymax-ymin)/float(nrows)
            geotransform=(xmin,xres,0,ymin,0, yres)

            self.outDS = gdal.GetDriverByName('GTiff').Create(self.outfile,ncols, nrows, 1 ,gdal.GDT_Float32,['TFW=YES', 'COMPRESS=PACKBITS'])
            self.outDS.SetGeoTransform(geotransform)  # Specify its coordinates
            srs = SpatialReference()                 # Establish its coordinate encoding
            srs.ImportFromEPSG(self.epsg)                     # WGS 84 / UTM zone 32N
            self.outDS.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system to the file
            self.outDS.GetRasterBand(1).WriteArray(zi)   # Writes my array to the raster
            #self.outDS.FlushCache()
            self.data_out_lst.append(self.outfile)
            self.outDS = None
            zi= None
            x,y,z = None, None, None
            nrows,ncols = None, None
        return [self.message, self.data_out_lst]

