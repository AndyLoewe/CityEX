#-------------------------------------------------------------------------------
# Name:        main_frame
# Purpose:     will handel all the scripts provided by me
#
# Author:      Andreas Loewe
#
# Created:     27.08.2014
# Copyright:   (c) Andreas Loewe 2014
# Licence:     <GNU - Free use>
#-------------------------------------------------------------------------------
import os, sys
from PyQt4.QtCore import *
from PyQt4.QtCore import (QString, Qt)
from PyQt4.QtGui import *
#from PyQt4.QtGui import (QFont, QPalette)
#from PyQt4.QtSql import (QSqlDatabase, QSqlQuery, QSqlRelation,\
  #   QSqlRelationalDelegate, QSqlRelationalTableModel,QSqlTableModel)
import json
from scipy import ndimage
#import numpy as np
import gdal
import osr
#import osgeo
#from osgeo import gdal_array


dirname, filename = os.path.split(os.path.abspath(__file__))        # get the Name of the folder the file is currently in

os.chdir(os.path.join(dirname, "gui"))
guipath = os.path.join(dirname, "gui")
helppath = os.path.join(dirname, "help")
modulpath = os.path.join(dirname, "modul")
os.chdir(guipath)

try:
    from gui.CityEX import Ui_CityEX

except:
    from CityEX import Ui_CityEX

os.chdir(modulpath)

## Import the moduls
try:

    from modul.module_ndem import NDEM
    from modul.module_ndvi import NDVI
    from modul.module_filter import Filter_ndem
    from modul.module_math import Internal_Math
    from modul.module_classification import Reclassification
    from modul.module_knwlgd import Knowledge_Engineering
    from modul.module_xyz import Create_elevation_models
    from modul.module_green_knwlgd import Green_Knowledge_Engineering
    from modul.module_locla_maxima import Tree_Top_Detection
    from modul.module_green_knwlgd import *
    from modul.module_raster2poly import Raster_2_Poly
except:
    from module_ndem import NDEM
    from module_ndvi import NDVI
    from module_filter import Filter_ndem
    from module_math import Internal_Math
    from module_classification import Reclassification
    from module_knwlgd import Knowledge_Engineering
    from module_xyz import Create_elevation_models
    from module_green_knwlgd import Green_Knowledge_Engineering
    from module_locla_maxima import Tree_Top_Detection
    from module_raster2poly import Raster_2_Poly

class CityEX(QWidget, Ui_CityEX):
    def __init__(self, parent = None):
        super(CityEX, self).__init__(parent)
        QWidget.__init__(self, parent)
        self.setupUi(self)

# ----- predefined values ---------------------------------------##
        self.tabWidget_main.setCurrentIndex(0)
        self.help_list = ['Inputs', 'Mainwindow', 'Outputs']

        self.check_box_lst_filter = [self.checkBox_tab2_closing, self.checkBox_tab2_opening,\
                                     self.checkBox_tab2_erosion, self.checkBox_tab2_fillhole]
        self.ndimage_func_lst = [ndimage.binary_closing, ndimage.binary_opening, ndimage.binary_erosion, ndimage.binary_fill_holes]
        self.check_b_filter_dic = {self.checkBox_tab2_closing : [self.spinBox_tab2_x_closing, self.spinBox_tab2_y_closing],\
                                   self.checkBox_tab2_erosion : [self.spinBox_tab2_x_erosion, self.spinBox_tab2_y_erosion],\
                                   self.checkBox_tab2_opening : [self.spinBox_tab2_x_opening, self.spinBox_tab2_y_opening],\
                                   self.checkBox_tab2_fillhole : [self.spinBox_tab2_x_filling, self.spinBox_tab2_y_filling]
                                    }
        self.no_data_msg = "No data was chosen"
        self.now_you_see_me = "Nothing to see here!"
        self.input_value = 0
        self.support_value = 0
        self.infile_dem = None
        self.infile_dom = None
        self.infile_support = None
        self.table_item_lst = []
        self.table_green_item_lst = []
        self.handel_start()


# ----- Connects with comboboxs ---------------------------------##
        self.connect(self.comboBox_tab1_input, SIGNAL("currentIndexChanged(int)"), self.handel_inputs)
        self.connect(self.comboBox_tab1_support, SIGNAL("currentIndexChanged(int)"), self.handel_support)
        self.connect(self.comboBox_tab1_ir,SIGNAL("activated(int)"), self.get_band_value_ir)
        self.connect(self.comboBox_tab1_red, SIGNAL("activated(int)"), self.get_band_value_red)
##        self.connect()
##        self.connect()
##        self.connect()
##        self.connect()
##        self.connect()
##        self.connect()
# ----- Connects with pushButtons -------------------------------##

        self.connect(self.pushButton_tab1_input_dem, SIGNAL("clicked()"),self.pushButton_input_dem)
        self.connect(self.pushButton_tab1_input_dom, SIGNAL("clicked()"),self.pushButton_input_dom)
        self.connect(self.pushButton_tab1_input_support, SIGNAL("clicked()"), self.pushButton_input_support)
        self.connect(self.pushButton_tab1_output, SIGNAL("clicked()"),self.pushButton_output)

        self.connect(self.pushButton_tab2_add, SIGNAL("clicked()"), self.row_add)
        self.connect(self.pushButton_tab2_delete, SIGNAL("clicked()"), self.row_delete)
        self.connect(self.tableWidget_tab2_knowlegde, SIGNAL('cellClicked(int,int)'),self.returnRowForRemove)
        self.connect(self.tableWidget_tab2_knowlegde, SIGNAL('cellActivated(int,int)'),self.returnRowForRemove)

        self.connect(self.pushButton_tab3_add, SIGNAL("clicked()"), self.row_add_green)
        self.connect(self.pushButton_tab3_delete, SIGNAL("clicked()"), self.row_delete_green)

        self.connect(self.pushButton_global_ok, SIGNAL("clicked()"), self.ok_event)
        self.connect(self.pushButton_global_cancel, SIGNAL("clicked()"), self.close_event)

# ----- Connects with other objects -----------------------------###
        self.connect(self.treeWidget_tab4_help, SIGNAL("itemSelectionChanged()"), self.helper_selection)
        for lst in self.check_b_filter_dic.values():
            for widget in range(len(lst)):
                self.connect(lst[widget], SIGNAL("valueChanged(int)"), self.handel_filter_settings)
        for widget in range(len(self.check_b_filter_dic.keys())):
            self.connect(self.check_b_filter_dic.keys()[widget], SIGNAL("stateChanged(int)"), self.handel_filter_checked)
        self.connect(self.checkBox_tab2_fillhole, SIGNAL("stateChanged(int)"), self.handel_filter_checked)
        self.connect(self.checkBox_tab3_closing, SIGNAL("stateChanged(int)"), self.handel_green_filter)
        self.connect(self.spinBox_tab3_x_closing, SIGNAL("valueChanged(int)"), self.handel_green_settings)
        self.connect(self.spinBox_tab3_y_closing, SIGNAL("valueChanged(int)"), self.handel_green_settings)

        self.connect(self.tableWidget_tab2_knowlegde, SIGNAL("cellPressed(int,int)"), self.read_table_knwlgd)
        self.connect(self.tableWidget_tab2_knowlegde, SIGNAL("currentCellChanged(int, int)"), self.read_table_knwlgd)
        self.connect(self.tableWidget_tab2_knowlegde, SIGNAL("cellEntered(int,int)"), self.read_table_knwlgd)

        self.connect(self.tableWidget_tab3_knowlegde, SIGNAL("cellPressed(int,int)"), self.read_table_green_knwlgd)
        self.connect(self.tableWidget_tab3_knowlegde, SIGNAL("currentCellChanged(int, int)"), self.read_table_green_knwlgd)
        self.connect(self.tableWidget_tab3_knowlegde, SIGNAL("cellEntered(int,int)"), self.read_table_green_knwlgd)


# ----- Start of all other functions -----------###

# ----- Functions for Tab 1 --------------------###
    def handel_inputs(self, value):
        self.validat_inputs()
        if value == 0:
            self.lineEdit_tab1_input_dem.setPlaceholderText(self.now_you_see_me)
            self.lineEdit_tab1_input_dom.setPlaceholderText(self.now_you_see_me)
            self.checkBox_tab1_ndem.setChecked(False)
            self.checkBox_tab1_ndem.setEnabled(False)
            self.lineEdit_tab1_input_dem.setEnabled(False)
            self.lineEdit_tab1_input_dom.setEnabled(False)
            self.pushButton_tab1_input_dem.setEnabled(False)
            self.pushButton_tab1_input_dom.setEnabled(False)
            self.spinBox_tab1_EPSG.setEnabled(False)
            self.doubleSpinBox_tab1_cellsize.setEnabled(False)
            self.spinBox_tab1_nodata.setEnabled(False)
            self.input_value = 0
        if value == 1:
            self.lineEdit_tab1_input_dem.setPlaceholderText("Insert your nDEM here!")
            self.lineEdit_tab1_input_dom.setPlaceholderText(self.now_you_see_me)
            self.checkBox_tab1_ndem.setChecked(False)
            self.checkBox_tab1_ndem.setEnabled(False)
            self.lineEdit_tab1_input_dem.setEnabled(True)
            self.lineEdit_tab1_input_dom.setEnabled(False)
            self.pushButton_tab1_input_dem.setEnabled(True)
            self.pushButton_tab1_input_dom.setEnabled(False)
            self.spinBox_tab1_EPSG.setEnabled(False)
            self.doubleSpinBox_tab1_cellsize.setEnabled(False)
            self.spinBox_tab1_nodata.setEnabled(False)
            self.input_value = 1
        if value == 2:
            self.lineEdit_tab1_input_dem.setPlaceholderText("Insert your DEM here!")
            self.lineEdit_tab1_input_dom.setPlaceholderText("Insert your DOM here!")
            self.checkBox_tab1_ndem.setEnabled(True)
            self.checkBox_tab1_ndem.setChecked(True)
            self.lineEdit_tab1_input_dem.setEnabled(True)
            self.lineEdit_tab1_input_dom.setEnabled(True)
            self.pushButton_tab1_input_dem.setEnabled(True)
            self.pushButton_tab1_input_dom.setEnabled(True)
            self.spinBox_tab1_EPSG.setEnabled(False)
            self.doubleSpinBox_tab1_cellsize.setEnabled(False)
            self.spinBox_tab1_nodata.setEnabled(True)
            self.input_value = 2
##        if value == 3:
##            self.lineEdit_tab1_input_dem.setPlaceholderText("Insert your First Return data here!")
##            self.lineEdit_tab1_input_dom.setPlaceholderText("Insert your Last Return data here!")
##            self.lineEdit_tab1_input_dem.setEnabled(True)
##            self.lineEdit_tab1_input_dom.setEnabled(True)
##            self.pushButton_tab1_input_dem.setEnabled(True)
##            self.pushButton_tab1_input_dom.setEnabled(True)
##            self.spinBox_tab1_EPSG.setEnabled(True)
##            self.doubleSpinBox_tab1_cellsize.setEnabled(True)
##            self.spinBox_tab1_nodata.setEnabled(True)
##            self.input_value = 3

    def handel_start(self):
        self.validat_inputs()
        self.lineEdit_tab1_input_dem.setEnabled(False)
        self.lineEdit_tab1_input_dom.setEnabled(False)
        self.lineEdit_tab1_support.setEnabled(False)
        self.pushButton_tab1_input_dem.setEnabled(False)
        self.pushButton_tab1_input_dom.setEnabled(False)
        self.pushButton_tab1_input_support.setEnabled(False)
        self.spinBox_tab1_nodata.setEnabled(False)
        self.spinBox_tab1_EPSG.setEnabled(False)
        self.doubleSpinBox_tab1_cellsize.setEnabled(False)
        self.comboBox_tab1_ir.setEnabled(False)
        self.comboBox_tab1_red.setEnabled(False)
        self.lineEdit_tab1_input_dem.setPlaceholderText(self.now_you_see_me)
        self.lineEdit_tab1_input_dom.setPlaceholderText(self.now_you_see_me)
        self.lineEdit_tab1_support.setPlaceholderText(self.now_you_see_me)
        self.spinBox_tab3_x_closing.setEnabled(False)
        self.spinBox_tab3_y_closing.setEnabled(False)
        for wi in range(len(self.check_box_lst_filter)):
            value_spin =  self.check_b_filter_dic.get(self.check_box_lst_filter[wi])
            value_spin[0].setEnabled(False)
            value_spin[1].setEnabled(False)


    def handel_support(self, value):
        self.validat_inputs()
        if value == 0:
            self.lineEdit_tab1_support.setPlaceholderText(self.now_you_see_me)
            self.lineEdit_tab1_support.setEnabled(False)
            self.pushButton_tab1_input_support.setEnabled(False)
            self.label_band_red.setEnabled(False)
            self.label_band_red.setText("Red Band:")
            self.label_band_ifrared.setEnabled(False)
            self.comboBox_tab1_red.setEnabled(False)
            self.comboBox_tab1_ir.setEnabled(False)
            self.support_value = 0
            for i in range(self.comboBox_tab1_red.count()):
                self.comboBox_tab1_ir.removeItem(0)
                self.comboBox_tab1_red.removeItem(0)

        if value == 1:
            self.lineEdit_tab1_support.setPlaceholderText("Insert the path for your image!")
            self.lineEdit_tab1_support.setEnabled(True)
            self.pushButton_tab1_input_support.setEnabled(True)
            self.label_band_red.setEnabled(True)
            self.label_band_red.setText("Red Band:")
            self.label_band_ifrared.setEnabled(True)
            self.comboBox_tab1_red.setEnabled(True)
            self.comboBox_tab1_ir.setEnabled(True)
            self.support_value = 1

        if value == 2:
            self.lineEdit_tab1_support.setPlaceholderText("Insert the path for your NDVI image!")
            self.name_supp = os.path.split(str(self.infile_support))[1]
            self.lineEdit_tab1_support.setEnabled(True)
            self.pushButton_tab1_input_support.setEnabled(True)
            self.label_band_red.setText("Red Band:")
            self.label_band_red.setEnabled(True)
            self.label_band_ifrared.setEnabled(False)
            self.comboBox_tab1_red.setEnabled(True)
            self.comboBox_tab1_ir.setEnabled(False)
            self.support_value = 2
            for i in range(self.comboBox_tab1_red.count()):
                self.comboBox_tab1_ir.removeItem(0)


        if value == 3:
            self.lineEdit_tab1_support.setPlaceholderText("Insert the path for your image!")
            self.lineEdit_tab1_support.setEnabled(True)
            self.pushButton_tab1_input_support.setEnabled(True)
            self.label_band_red.setEnabled(True)
            self.label_band_red.setText("Choose:")
            self.label_band_ifrared.setEnabled(False)
            self.comboBox_tab1_red.setEnabled(True)
            self.comboBox_tab1_ir.setEnabled(False)
            self.support_value = 3
            for i in range(self.comboBox_tab1_red.count()):
                self.comboBox_tab1_ir.removeItem(0)


    def pushButton_input_dem(self):
        self.infile_dem = QFileDialog().getOpenFileName(self,'Open', r"" + dirname, 'Any file (*.*)' '\n' 'TIF (*.tif)' '\n' 'Erdas (*.img)' )
        if self.infile_dem == "":
            self.lineEdit_tab1_input_dem.setText(self.no_data_msg)
        else:
            if self.input_value == 1:
                self.lineEdit_tab1_input_dem.setText(self.infile_dem)
                self.ndem_name = os.path.split(str(self.infile_dem))[1]
            elif self.input_value ==2:
                self.lineEdit_tab1_input_dem.setText(self.infile_dem)
                self.ndem_name = "ndem_" + os.path.split(str(self.infile_dem))[1]
            elif self.input_value == 3:
                 self.ndem_name = "ndem_" + os.path.split(str(self.infile_dem))[1][0:-4] + ".tif"
            self.handel_epsg()
        self.validat_inputs()

    def pushButton_input_dom(self):
        self.validat_inputs()
        self.infile_dom = QFileDialog().getOpenFileName(self,'Open', r"" + dirname, 'Any file (*.*)' '\n' 'TIF (*.tif)' '\n' 'Erdas (*.img)' )
        if self.infile_dom == "":
            self.lineEdit_tab1_input_dom.setText(self.no_data_msg)
        else:
            self.lineEdit_tab1_input_dom.setText(self.infile_dom)
            self.handel_epsg()

    def pushButton_input_support(self):
        self.infile_support = QFileDialog().getOpenFileName(self,'Open', r"" + dirname, 'Any file (*.*)' '\n' 'TIF (*.tif)' '\n' 'Erdas (*.img)' )
        if self.infile_support == "":
            self.combox_tab1_bandfiller("no data")
            self.lineEdit_tab1_support.setText(self.no_data_msg)
        else:
            for i in range(self.comboBox_tab1_red.count()):
                self.comboBox_tab1_ir.removeItem(0)
                self.comboBox_tab1_red.removeItem(0)
            self.lineEdit_tab1_support.setText(self.infile_support)
            self.combox_tab1_bandfiller(self.infile_support)
            self.InputDS_support = gdal.Open(str(self.infile_support))
            bandlst = [self.InputDS_support.GetRasterBand(i+1) for i in range(self.InputDS_support.RasterCount)]
            for bnd in range(len(bandlst)):
                band = bandlst[bnd].GetBand()
                band_name = "Band_" + str(band.__hash__())
                self.comboBox_tab1_red.insertItem(bnd, band_name)
                self.comboBox_tab1_ir.insertItem(bnd, band_name)
            self.validat_inputs()

    def get_band_value_red(self, v):
        self.value_red_band = v
    def get_band_value_ir(self, v):
        self.value_ir_band = v

    def pushButton_output(self):
        #self.outfile = QFileDialog().getSaveFileName(self,'Open', r"" + dirname, 'Any file (*.*)' '\n' 'TIF (*.tif)' '\n' 'Erdas (*.img)' )
        self.outfile = QFileDialog().getExistingDirectory(self,'Open', dirname)

        if self.outfile == "":
            self.lineEdit_tab1_output.setText(self.no_data_msg)
        else:
            self.lineEdit_tab1_output.setText(self.outfile)
        self.validat_inputs()

    def handel_epsg(self):
        self.validat_inputs()
        set_epsg = gdal.Open(str(self.infile_dem))
        srs = osr.SpatialReference()
        srs.ImportFromWkt(set_epsg.GetProjection())
        epsg = srs.GetAttrValue("AUTHORITY", 1)
        self.spinBox_tab1_EPSG.setValue(int(epsg))
        cell_size = set_epsg.GetGeoTransform()
        self.doubleSpinBox_tab1_cellsize.setValue(float(cell_size[1]))
        band_test = set_epsg.GetRasterBand(1)
        try:
            self.spinBox_tab1_nodata.setValue(int(band_test.GetNoDataValue()))
        except:
            try:
                imag = band_test.GetNoDataValue()
                self.spinBox_tab1_nodata.setValue(float(imag.imag))

            except:
                self.spinBox_tab1_nodata.setValue(0)
        cell_size = None
        band_test = None
        set_epsg = None


    def combox_tab1_bandfiller(self, infile):
            if infile == "no data":
                self.lineEdit_global_error.setText("Error while loading data")
            else:
                self.lineEdit_global_error.setText("Everything worked")

# ----- Functions for Tab 2 --------------------###

    def row_add(self):
        self.cur_row = self.tableWidget_tab2_knowlegde.rowCount()
        self.tableWidget_tab2_knowlegde.setRowCount(self.cur_row + 1)
        self.comboboxes_for_input()
        #self.read_table_knwlgd()


    def comboboxes_for_input(self):
        font = QFont("Segoe UI", 12)
        self.comboBox_data = QComboBox()
        self.comboBox_data.setFont(font)
        self.comboBox_data.setEditable(True)
        ### define comboBox for the input data ###
        if self.input_value == 0 and self.infile_support == None: ### no data was selected
            self.comboBox_data.insertItem(0, "no data")
            self.comboBox_data.setEditable(False)
        elif  self.infile_dem != None and self.infile_support != None:
             self.name_supp = os.path.split(str(self.infile_support))[1]
             self.comboBox_data.insertItem(0, str(self.ndem_name))
             self.comboBox_data.insertItem(1, str(self.name_supp))
             self.comboBox_data.setEditable(False)
        elif self.infile_dem != None:
             self.comboBox_data.insertItem(0, str(self.ndem_name))
             self.comboBox_data.setEditable(False)
        else:
            self.comboBox_data.insertItem(0, "no data")
            self.comboBox_data.setEditable(False)
                ### define comboBox for the operators ###
        self.comboBox_opp = QComboBox()
        self.comboBox_opp.setFont(font)
        self.comboBox_opp.setEditable(True)
        self.comboBox_opp.insertItem(0, "+")
        self.comboBox_opp.insertItem(1, "-")
        self.comboBox_opp.insertItem(2, ">")
        self.comboBox_opp.insertItem(3, "<")
        self.comboBox_opp.insertItem(4, "<=")
        self.comboBox_opp.insertItem(5, ">=")
        self.comboBox_opp.insertItem(6, "*")

        self.comboBox_opp.setEditable(False)
        self.tableWidget_tab2_knowlegde.setCellWidget(self.cur_row, 0, self.comboBox_data)
        self.tableWidget_tab2_knowlegde.setCellWidget(self.cur_row, 1, self.comboBox_opp)


    def row_delete(self):
        try:
            if self.rowRemove < self.tableWidget_tab2_knowlegde.rowCount() and not self.rowRemove == -999:
                self.tableWidget_tab2_knowlegde.removeRow(self.rowRemove)
            else:
                self.cur_row = self.tableWidget_tab2_knowlegde.rowCount()
                self.tableWidget_tab2_knowlegde.setRowCount(self.cur_row - 1)
        except:
            self.cur_row = self.tableWidget_tab2_knowlegde.rowCount()
            self.tableWidget_tab2_knowlegde.setRowCount(self.cur_row - 1)
        self.rowRemove = -999
        #self.read_table_knwlgd()


    def returnRowForRemove(self, rowRemove, colRemove):
        self.rowRemove = rowRemove


    def handel_filter_settings(self, v):
        self.handel_filter_checked(42)


    def handel_filter_checked(self, v):
        self.validat_inputs()
        #self.filter_settings = {}
        self.filter_settings = []
        for wi in range(len(self.check_box_lst_filter)):
            value_spin =  self.check_b_filter_dic.get(self.check_box_lst_filter[wi])
            if self.check_box_lst_filter[wi].isChecked():
                value_spin[0].setEnabled(True)
                value_spin[1].setEnabled(True)
                self.filter_settings.append([self.ndimage_func_lst[wi], (value_spin[0].value(),value_spin[1].value())])
                #self.filter_settings[self.ndimage_func_lst[wi]] = [value_spin[0].value(),value_spin[1].value()]
            else:
                value_spin[0].setEnabled(False)
                value_spin[1].setEnabled(False)



    def read_table_knwlgd(self, a,n):
        self.mathobj = Internal_Math()
        self.validat_inputs()
        self.table_item_lst = []
        try:
            for tabitem in range(self.tableWidget_tab2_knowlegde.rowCount()):
                data= self.tableWidget_tab2_knowlegde.cellWidget(tabitem,0)
                mathop = self.tableWidget_tab2_knowlegde.cellWidget(tabitem,1)
                value = self.tableWidget_tab2_knowlegde.item(tabitem, 2)
                if str(mathop.currentText()) == "+":
                    mathop = self.mathobj._add_
                elif str(mathop.currentText()) == "-":
                    mathop = self.mathobj._minus_
                elif str(mathop.currentText()) == "*":
                    mathop = self.mathobj._multi_
                elif str(mathop.currentText()) == ">":
                    mathop = self.mathobj._bigger_
                elif str(mathop.currentText()) == ">=":
                    mathop = self.mathobj._bigger_equal
                elif str(mathop.currentText()) == "<":
                    mathop = self.mathobj._smaller_
                elif str(mathop.currentText()) == "<=":
                    mathop = self.mathobj._smaller_equal

                self.table_item_lst.append([str(data.currentText()), mathop, float(value.text())])

        except:
            message = "On or more values are not float or integer values"
            self.lineEdit_global_error.setText(message)

# ----- Functions for Tab 3 --------------------###
    def row_add_green(self):
        self.cur_row = self.tableWidget_tab3_knowlegde.rowCount()
        self.tableWidget_tab3_knowlegde.setRowCount(self.cur_row + 1)
        self.comboboxes_for_input_green()
        #self.read_table_knwlgd()


    def comboboxes_for_input_green(self):
        font = QFont("Segoe UI", 12)
        self.comboBox_data = QComboBox()
        self.comboBox_data.setFont(font)
        self.comboBox_data.setEditable(True)
        ### define comboBox for the input data ###
        if self.input_value == 0 and self.infile_support == None: ### no data was selected
            self.comboBox_data.insertItem(0, "no data")
            self.comboBox_data.setEditable(False)
        elif  self.infile_dem != None and self.infile_support != None:
             self.name_supp = os.path.split(str(self.infile_support))[1]
             self.comboBox_data.insertItem(0, str(self.ndem_name))
             self.comboBox_data.insertItem(1, str(self.name_supp))
             self.comboBox_data.setEditable(False)
        elif self.infile_dem != None:
             self.comboBox_data.insertItem(0, str(self.ndem_name))
             self.comboBox_data.setEditable(False)
        else:
            self.comboBox_data.insertItem(0, "no data")
            self.comboBox_data.setEditable(False)
                ### define comboBox for the operators ###
        self.comboBox_opp = QComboBox()
        self.comboBox_opp.setFont(font)
        self.comboBox_opp.setEditable(True)
        self.comboBox_opp.insertItem(0, "+")
        self.comboBox_opp.insertItem(1, "-")
        self.comboBox_opp.insertItem(2, ">")
        self.comboBox_opp.insertItem(3, "<")
        self.comboBox_opp.insertItem(4, "<=")
        self.comboBox_opp.insertItem(5, ">=")
        self.comboBox_opp.insertItem(6, "*")

        self.comboBox_opp.setEditable(False)
        self.tableWidget_tab3_knowlegde.setCellWidget(self.cur_row, 0, self.comboBox_data)
        self.tableWidget_tab3_knowlegde.setCellWidget(self.cur_row, 1, self.comboBox_opp)


    def row_delete_green(self):
        try:
            if self.rowRemove < self.tableWidget_tab3_knowlegde.rowCount() and not self.rowRemove == -999:
                self.tableWidget_tab3_knowlegde.removeRow(self.rowRemove)
            else:
                self.cur_row = self.tableWidget_tab3_knowlegde.rowCount()
                self.tableWidget_tab3_knowlegde.setRowCount(self.cur_row - 1)
        except:
            self.cur_row = self.tableWidget_tab3_knowlegde.rowCount()
            self.tableWidget_tab3_knowlegde.setRowCount(self.cur_row - 1)
        self.rowRemove = -999
        #self.read_table_knwlgd()


    def read_table_green_knwlgd(self, a,n):
        self.validat_inputs()
        self.mathobj = Internal_Math()
        self.table_green_item_lst = []
        try:
            for tabitem in range(self.tableWidget_tab3_knowlegde.rowCount()):
                data= self.tableWidget_tab3_knowlegde.cellWidget(tabitem,0)
                mathop = self.tableWidget_tab3_knowlegde.cellWidget(tabitem,1)
                value = self.tableWidget_tab3_knowlegde.item(tabitem, 2)
                if str(mathop.currentText()) == "+":
                    mathop = self.mathobj._add_
                elif str(mathop.currentText()) == "-":
                    mathop = self.mathobj._minus_
                elif str(mathop.currentText()) == "*":
                    mathop = self.mathobj._multi_
                elif str(mathop.currentText()) == ">":
                    mathop = self.mathobj._bigger_
                elif str(mathop.currentText()) == ">=":
                    mathop = self.mathobj._bigger_equal
                elif str(mathop.currentText()) == "<":
                    mathop = self.mathobj._smaller_
                elif str(mathop.currentText()) == "<=":
                    mathop = self.mathobj._smaller_equal

                self.table_green_item_lst.append([str(data.currentText()), mathop, float(value.text())])

        except:
            message = "On or more values are not float or integer values"
            self.lineEdit_global_error.setText(message)

    def handel_green_filter(self, v):
        self.filter_settings_green = []

        if self.checkBox_tab3_closing.isChecked():
            self.spinBox_tab3_x_closing.setEnabled(True)
            self.spinBox_tab3_y_closing.setEnabled(True)
            self.filter_settings_green.append([ndimage.binary_closing, (self.spinBox_tab3_x_closing.value(),self.spinBox_tab3_y_closing.value())])
        else:
                self.spinBox_tab3_x_closing.setEnabled(False)
                self.spinBox_tab3_y_closing.setEnabled(False)


    def handel_green_settings(self, v):
        self.handel_green_filter(42)

# ----- Functions for Tab 4 --------------------###
    def helper_selection(self):
        help_item = self.treeWidget_tab4_help.currentItem()
        helpDict = json.loads(open(os.path.join(helppath, "help.json")).read())
        for helpitem in range(len(self.help_list)):
            if help_item.text(0) == str(self.help_list[helpitem]):
                self.textEdit_tab4_help.setText(helpDict[str(self.help_list[helpitem])][0])
                break
            else:
                self.textEdit_tab4_help.setText("An error appiered, I am sorry :(")

# ----- Functions for globals ------------------###

    def close_event(self):
        print self.comboBox_tab1_ir.currentIndex()
        reply = QMessageBox.question(self, 'Message','Do you want to quit?', QMessageBox.Yes, QMessageBox.No)
        if  reply == QMessageBox.Yes:
            app.closeAllWindows()
        else:
            pass


    def name_creater(self):
        """the function creates the outputnames
           it creates everytime all names which could posibily be needed
           the ok_event will use these names
        """
        if self.ndem_name != None or self.ndem_name != self.no_data_msg:

            self.outfile_ndem = os.path.join(str(self.outfile), self.ndem_name)
            self.outfile_knwlgd = os.path.join(str(self.outfile), "knwlgd_" + self.ndem_name)
            self.outfile_knwlgd_green = os.path.join(str(self.outfile), "knwlgd_green_" + self.ndem_name)
            self.outfile_filtered = os.path.join(str(self.outfile), "filterd_" + self.ndem_name)
            self.outfile_classiefied = os.path.join(str(self.outfile), "classified_"+ self.ndem_name)

        try:
            if self.name_supp != None or self.name_supp != self.no_data_msg:
                if self.support_value == 1:
                    self.outfile_support = os.path.join(self.outfile, "ndvi_" + self.name_supp)
                else:
                    self.outfile_support = os.path.join(self.outfile, self.name_supp)

        except:
            self.outfile_support = self.no_data_msg

        #### check if all the variables are passed in the right way and format
        """missing: --  """
        print self.outfile_classiefied, self.outfile_filtered, self.outfile_support, self.outfile_ndem, self.outfile_knwlgd_green, self.outfile_knwlgd_green
        print""
        print self.table_green_item_lst, self.table_item_lst, self.filter_settings, self.filter_settings_green
        print self.spinBox_tab1_nodata.value(), self.spinBox_tab1_EPSG.value(), self.spinBox_tab3_iter.value(),\
        self.spinBox_tab3_nodata_allowed.value(), self.spinBox_tab3_windowsize.value(), self.doubleSpinBox_tab3_cri_value.value()

    def validat_inputs(self):
        if self.input_value == 0 or self.lineEdit_tab1_output.text() == self.no_data_msg or self.lineEdit_tab1_output.text() == "" :
            self.pushButton_global_ok.setEnabled(False)
        else:
            self.validate_options()

##        elif self.input_value == 1 and self.support_value == 0:
##            self.validate_options()
##        elif self.input_value == 1 and self.support_value != 0:
##            self.validate_options()
##        elif self.input_value == 2 and self.support_value == 0:
##            self.validate_options()
##        elif self.input_value == 2 and self.support_value != 0:
##            self.validate_options()

    def validate_options(self):
        if self.support_value == 0:
            if not self.checkBox_tab1_buildings.isChecked() and not self.checkBox_tab1_trees.isChecked() \
            and not self.checkBox_tab1_ndem.isChecked():
                self.pushButton_global_ok.setEnabled(False)

            elif self.checkBox_tab1_buildings.isChecked() and self.checkBox_tab1_trees.isChecked() and self.checkBox_tab1_ndem.isChecked():
                # if all are checked
                if len(self.table_item_lst) !=  0 and len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" :
                    self.pushButton_global_ok.setEnabled(True)


            elif self.checkBox_tab1_buildings.isChecked() and self.checkBox_tab1_ndem.isChecked():
                # if ndem and buildings are checked
                if len(self.table_item_lst) !=  0 and self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" :
                    self.pushButton_global_ok.setEnabled(True)

            elif  self.checkBox_tab1_trees.isChecked() and self.checkBox_tab1_ndem.isChecked():
                # if ndem and trees are checked
                if len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" :
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_buildings.isChecked() and self.checkBox_tab1_trees.isChecked():
                # if trees and buildings are chekced
                if (self.table_item_lst) !=  0 and len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_buildings.isChecked():
                # if buildings are checked
                if len(self.table_item_lst) != 0 and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_trees.isChecked():
                # if trees is checkedprint "0.1.2"
                if len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_ndem.isChecked():
                # if ndem is checked
                if self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" :
                    self.pushButton_global_ok.setEnabled(True)

        else:
            if not self.checkBox_tab1_buildings.isChecked() and not self.checkBox_tab1_trees.isChecked() \
            and not self.checkBox_tab1_ndem.isChecked():
                self.pushButton_global_ok.setEnabled(False)

            elif self.checkBox_tab1_buildings.isChecked() and self.checkBox_tab1_trees.isChecked() and self.checkBox_tab1_ndem.isChecked() \
            and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                # if all are checked
                if len(self.table_item_lst) !=  0 and len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" \
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_buildings.isChecked() and self.checkBox_tab1_ndem.isChecked():
                # if ndem and buildings are checked
                if len(self.table_item_lst) !=  0 and self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" \
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)#

            elif self.checkBox_tab1_trees.isChecked() and self.checkBox_tab1_ndem.isChecked():
                # if ndem and trees are checked
                if len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" \
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)

            elif  self.checkBox_tab1_trees.isChecked() and self.checkBox_tab1_ndem.isChecked():
                # if trees and buildings are chekced
                if (self.table_item_lst) !=  0 and len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != ""\
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_buildings.isChecked():
                # if buildings are checked
                if len(self.table_item_lst) != 0 and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != ""\
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_trees.isChecked():
                # if trees is checked
                if len(self.table_green_item_lst) != 0 and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != ""\
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)

            elif self.checkBox_tab1_ndem.isChecked():
                # if ndem is checked
                if self.lineEdit_tab1_input_dom.text() != self.no_data_msg and self.lineEdit_tab1_input_dom.text() != ""\
                and self.lineEdit_tab1_input_dem.text() != self.no_data_msg and self.lineEdit_tab1_input_dem.text() != "" \
                and self.lineEdit_tab1_support.text() != self.no_data_msg and self.lineEdit_tab1_support.text() !="":
                    self.pushButton_global_ok.setEnabled(True)


    def ok_event(self):
        ### create the names to find all the values
        self.name_creater()
        ndem_check_value = 0
        ndvi_check_value = 0
        ## Will check the dicision tree for the input and supports and will create the data if buildings are checked
        if self.checkBox_tab1_buildings.isChecked():
            if self.input_value == 1 and self.support_value == 0:
                self.knwlgd = Knowledge_Engineering(str(self.infile_dem), str(self.outfile_knwlgd), self.table_item_lst, None, int(self.spinBox_tab1_nodata.value())).calc_knowledge()
                message = self.knwlgd[1]
                self.lineEdit_global_error.setText(message)

                self.filter = Filter_ndem(str(self.outfile_knwlgd), str(self.infile_dem), str(self.outfile_filtered), self.filter_settings).filter_application()
                message  = self.filter[1]
                self.lineEdit_global_error.setText(message)

                self.classification = Reclassification(str(self.outfile_filtered), str(self.outfile_classiefied)).Reclassify()

                self.raster2poly = Raster_2_Poly(self.outfile_classiefied, str(self.outfile))



            elif self.input_value == 1 and self.support_value == 1:
                self.ndvi = NDVI(str(self.infile_support), str(self.outfile_support), int(self.comboBox_tab1_red.currentIndex()), int(self.comboBox_tab1_ir.currentIndex())).calc_ndvi() ## fehlen tut noch die variablen fuer die baender
                message = self.ndvi[1]

                self.knwlgd = Knowledge_Engineering(str(self.infile_dem), str(self.outfile_knwlgd), self.table_item_lst,\
                self.outfile_support, int(self.spinBox_tab1_nodata.value()), int(self.comboBox_tab1_red.currentIndex())).calc_knowledge()
                message = self.knwlgd[1]
                self.lineEdit_global_error.setText(message)

                self.filter = Filter_ndem(str(self.outfile_knwlgd), str(self.infile_dem), str(self.outfile_filtered), self.filter_settings).filter_application()
                message  = self.filter[1]
                self.lineEdit_global_error.setText(message)

                self.classification = Reclassification(str(self.outfile_filtered), str(self.outfile_classiefied)).Reclassify()

                self.raster2poly = Raster_2_Poly(self.outfile_classiefied,str(self.outfile))
                ndvi_check_value = 1

            elif self.input_value == 1 and (self.support_value == 2 or self.support_value ==3):
                self.knwlgd = Knowledge_Engineering(str(self.infile_dem), str(self.outfile_knwlgd), self.table_item_lst, str(self.outfile_support),\
                 int(self.spinBox_tab1_nodata.value()),self.comboBox_tab1_red.currentIndex(),int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).calc_knowledge()
                message = self.knwlgd[1]
                self.lineEdit_global_error.setText(message)

                self.filter = Filter_ndem(str(self.outfile_knwlgd), str(self.infile_dem), str(self.outfile_filtered), self.filter_settings).filter_application()
                message  = self.filter[1]
                self.lineEdit_global_error.setText(message)

                self.classification = Reclassification(str(self.outfile_filtered), str(self.outfile_classiefied)).Reclassify()

                self.raster2poly = Raster_2_Poly(self.outfile_classiefied,str(self.outfile))


            elif self.input_value == 2 and self.support_value == 0:
                self.ndem_model = NDEM(str(self.infile_dem), str(self.infile_dom),str(self.outfile_ndem), int(self.spinBox_tab1_nodata.value()))
                self.knwlgd = Knowledge_Engineering(str(self.infile_dem), str(self.outfile_knwlgd), self.table_item_lst, None, int(self.spinBox_tab1_nodata.value()) , 0).calc_knowledge()
                message = self.knwlgd[1]
                self.lineEdit_global_error.setText(message)

                self.filter = Filter_ndem(str(self.outfile_knwlgd), str(self.infile_dem), str(self.outfile_filtered), self.filter_settings).filter_application()
                message  = self.filter[1]
                self.lineEdit_global_error.setText(message)

                self.classification = Reclassification(str(self.outfile_filtered), str(self.outfile_classiefied)).Reclassify()

                self.raster2poly = Raster_2_Poly(self.outfile_classiefied,str(self.outfile))
                ndem_check_value = 1


            elif self.input_value == 2 and (self.support_value == 2 or self.support_value ==3):
                ## 1. modul_classification	2. modul_filter	3. knwlgd	4. modul_ndem
                self.ndem_model = NDEM(str(self.infile_dem), str(self.infile_dom),str(self.outfile_ndem), int(self.spinBox_tab1_nodata.value()))

                self.knwlgd = Knowledge_Engineering(str(self.infile_dem), str(self.outfile_knwlgd), self.table_item_lst, str(self.outfile_support), int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).calc_knowledge()
                message = self.knwlgd[1]
                self.lineEdit_global_error.setText(message)

                self.filter = Filter_ndem(str(self.outfile_knwlgd), str(self.infile_dem), str(self.outfile_filtered), self.filter_settings).filter_application()
                message  = self.filter[1]
                self.lineEdit_global_error.setText(message)

                self.classification = Reclassification(str(self.outfile_filtered), str(self.outfile_classiefied)).Reclassify()

                self.raster2poly = Raster_2_Poly(self.outfile_classiefied,str(self.outfile))
                ndem_check_value = 1



            elif self.input_value == 2 and self.support_value == 1:
                self.ndvi = NDVI(str(self.infile_support), str(self.outfile_support), int(self.comboBox_tab1_red.currentIndex()), int(self.comboBox_tab1_ir.currentIndex())).calc_ndvi() ## fehlen tut noch die variablen fuer die baender
                message = self.ndvi[1]

                self.ndem_model = NDEM(str(self.infile_dem), str(self.infile_dom),str(self.outfile_ndem), int(self.spinBox_tab1_nodata.value()))

                self.knwlgd = Knowledge_Engineering(str(self.infile_dem), str(self.outfile_knwlgd), self.table_item_lst, str(self.outfile_support), \
                int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).calc_knowledge()
                message = self.knwlgd[1]
                self.lineEdit_global_error.setText(message)

                self.filter = Filter_ndem(str(self.outfile_knwlgd), str(self.infile_dem), str(self.outfile_filtered), self.filter_settings).filter_application()
                message  = self.filter[1]
                self.lineEdit_global_error.setText(message)

                self.classification = Reclassification(str(self.outfile_filtered), str(self.outfile_classiefied)).Reclassify()

                self.raster2poly = Raster_2_Poly(self.outfile_classiefied,str(self.outfile))
                ndem_check_value = 1
                ndvi_check_value = 1
                self.comboBox_tab1_ir.currentIndex()



        if self.checkBox_tab1_trees.isChecked():
            if self.input_value == 1 and self.support_value == 0:
                self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,None,\
                int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) ,0).green_calc_knowledge()
                message  = self.green_knwlg[1]
                self.lineEdit_global_error.setText(message)
                self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))

            elif self.input_value == 1 and self.support_value == 1:
                if ndvi_check_value == 1:
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst, str(self.outfile_suppor),\
                    int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)
                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))
                else:
                    self.ndvi = NDVI(str(self.infile_support), str(self.outfile_support), int(self.comboBox_tab1_red.currentIndex()), int(self.comboBox_tab1_ir.currentIndex())).calc_ndvi() ## fehlen tut noch die variablen fuer die baender
                    message = self.ndvi[1]
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,str(self.outfile_suppor),\
                    int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)
                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))

            elif self.input_value == 1 and (self.support_value == 2 or self.support_value ==3):
                self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,\
                str(self.outfile_support),int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                message  = self.green_knwlg[1]
                self.lineEdit_global_error.setText(message)
                self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))

            elif self.input_value == 2 and self.support_value == 0:
                if ndem_check_value == 1:
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,\
                    None,int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)
                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))
                else:
                    self.ndem_model = NDEM(str(self.infile_dem), str(self.infile_dom),str(self.outfile_ndem))
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,None,\
                    int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , 0).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)
                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))



            elif self.input_value == 2 and self.support_value == 1:
                if ndem_check_value == 1:
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst, \
                    str(self.outfile_support),int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)
                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))

                else:
                    self.ndem_model = NDEM(str(self.infile_dem), str(self.infile_dom),str(self.outfile_ndem))
                    self.ndvi = NDVI(str(self.infile_support), str(self.outfile_support), int(self.comboBox_tab1_red.currentIndex()), int(self.comboBox_tab1_ir.currentIndex())).calc_ndvi() ## fehlen tut noch die variablen fuer die baender
                    message = self.ndvi[1]

                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,str(self.outfile_support),\
                    int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)

                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))



            elif self.input_value == 2 and (self.support_value == 2 or self.support_value ==3):
                if ndem_check_value == 1:
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,str(self.outfile_support),\
                    int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)

                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))
                else:
                    self.ndem_model = NDEM(str(self.infile_dem), str(self.infile_dom),str(self.outfile_ndem))
                    self.green_knwlg = Green_Knowledge_Engineering(str(self.outfile_ndem), str(self.outfile_knwlgd_green), self.table_green_item_lst,\
                    str(self.outfile_support),int(self.spinBox_tab3_iter.value()),self.filter_settings_green, int(self.spinBox_tab1_nodata.value()) , int(self.comboBox_tab1_red.currentIndex())).green_calc_knowledge()
                    message  = self.green_knwlg[1]
                    self.lineEdit_global_error.setText(message)
                    self.local_max = Tree_Top_Detection(str(self.outfile_knwlgd_green), int(self.spinBox_tab3_windowsize.value()), int(self.spinBox_tab3_nodata_allowed.value()), float(self.doubleSpinBox_tab3_cri_value.value()))









# ----- will run the program -------------------###
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = CityEX()
    form.show()
    app.exec_()
    app = None
