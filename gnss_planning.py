# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNSSplanning
                                 A QGIS plugin
 This plugin predict GNSS satellites position over reciver's sky given an
 epoch and a skyline obstruction.
                              -------------------
        begin                : 2017-02-09
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Cesc Masdeu Ferrer
        email                : cescmf@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import qgis libraries in order to interoperate with QGIS elements.
import qgis
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from osgeo import gdal
import processing
# Import PyQt4 libraries in order to satisfy functional needs. (QMessageBox, QFileDialog)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox, QApplication
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from gnss_planning_dialog import GNSSplanningDialog
# Import other modules
import sys
import os.path
import os
import numpy as np
from math import pi
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import matplotlib.pyplot as plt
# Import plugin modules
from scripts.ImportTLE import Import_TLE
from scripts.transform import geographic_to_ITRF, ITRF_to_geographic
from scripts.Propagate import propagate
from scripts.DOP import getDOP_values
from scripts.Polarplot import PolarChart_class
from scripts.Profiles import linesProfiles
from scripts.Capture_coords import CaptureCoords
from scripts.Satellite import Satellite_class
from scripts.commonfun import getCurrentPath

class GNSSplanning():
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = GNSSplanningDialog()
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GNSSplanning_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GNSSplanning')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GNSSplanning')
        self.toolbar.setObjectName(u'GNSSplanning')

        # Import TLE files:
        try:
            Import_TLE()
        except:
            msg = QMessageBox()
            msg.setText("Internet connection error")
            msg.setDetailedText('Please check your Internet connection')
            msg.exec_()

        # Capture coordinates from QGIS canvas.
        self.dlg.pushButton_Select.clicked.connect(self.select_on_canvas)
        # Capture coordinates from QGIS canvas.
        self.dlg.pushButton_Copy.clicked.connect(self.copy_on_form)
        # Initialize propagate button.
        self.dlg.pushButton_Propagate.clicked.connect(self.run_first_propagate)
        # propagate next epochs
        self.dlg.horizontalSlider_Plot.valueChanged.connect(self.run_propagate)

        self.layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in self.layers:
            layer_list.append(layer.name())
            self.dlg.comboBox_Skyline.addItems(layer_list)


        self.skyline = "off"
        self.mask = 0
        self.plt = plt
        self.plot(plotSat_List=[])

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GNSSplanning', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GNSSplanning/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GNSS Planning'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GNSSplanning'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar


    def select_on_canvas(self):
        """ capture coordinates from QGIS in one click in EPSG:4326 (WGS 1984)
        independently from what your current CRS is."""
        self.mapTool = CaptureCoords(self.iface)
        self.iface.mapCanvas().setMapTool(self.mapTool)
    def copy_on_form(self):
        try:
            self.dlg.lineEdit_LonX.setText(self.mapTool.x_WGS)
            self.dlg.lineEdit_LatY.setText(self.mapTool.y_WGS)
        except:
            pass


    def run_first_propagate(self):
        self.horizon()
        """Propagate satellites position at first epoch."""
        if self.dlg.checkBox_Skyline.isChecked():
            self.skyline = "on"


        else:
            self.skyline = "off"


        if self.read_parameters():
            self.observer_position()
            self.get_epochs()
            self.run_propagate()
        else:
            pass


    def horizon(self):

        try:
            selectedLayerIndex = self.dlg.comboBox_Skyline.currentIndex()

            rasterlayer = self.layers[selectedLayerIndex]
            horizonresults = self.plugin_dir + r'\scripts\profiles\horizon.txt'
            x = self.mapTool.x_UTM 
            y = self.mapTool.y_UTM 
            xy = str(x)+","+str(y)
           processing.runalg('grass7:r.horizon.height',rasterlayer.name(),xy,0.0,5.0,0.0,360.0,10000.0,'1.0',True,'456817.5,484552.5,4549752.5,4668457.5',None,horizonresults)

        except:
            pass


    def run_propagate(self):
        try:
            self.epochNum = self.dlg.horizontalSlider_Plot.value()
            self.epoch = self.dicc_epochs[self.epochNum]
            results = propagate(self.geo_observer, self.XYZ_observer, self.epoch, self.epochNum, self.mask, self.skyline, self.constellations)
            plotSat_List = results[0]
            XYZSat_List = results[1]
            meus = results[2]

            self.plot(plotSat_List)

            DOP = getDOP_values(self.XYZ_observer, XYZSat_List[1])
            message = "   GDOP %.2f        PDOP %.2f        TDOP %.2f        HDOP %.2f        VDOP %.2f" % (DOP[1][0], DOP[1][1], DOP[1][2], DOP[1][3], DOP[1][4])
            self.dlg.label_DOP.setText(str(message))

        except:
            pass


    def read_parameters(self):
        check = True

        try:
            self.lonX_obs = float(self.dlg.lineEdit_LonX.text())
            self.latY_obs = float(self.dlg.lineEdit_LatY.text())
            self.hZ_obs = float(self.dlg.lineEdit_hZ.text())
            self.antenna = float(self.dlg.lineEdit_Antenna.text())
        except:
            check = False
            msg = QMessageBox()
            msg.setText("Invalid parameters")
            msg.setDetailedText("Coordinates and mask values must be integer or float. Empty forms are not allowed.")
            msg.exec_()

        self.inputCood_observer = [self.lonX_obs, self.latY_obs, self.hZ_obs + self.antenna]


        # input and check mask value:
        if self.dlg.checkBox_Mask.isChecked():
            self.mask = float(self.dlg.lineEdit_Mask.text())
            if self.mask < 0:
                check = False
                msg = QMessageBox()
                msg.setText("Invalid mask parameter")
                msg.setDetailedText("Mask values must be >= 0")
                msg.exec_()
        else:
            self.mask = 0.0


        # add contelations:
        self.constellations = []
        if self.dlg.checkBox_GPS.isChecked():
            self.constellations.append("GPS")
        if self.dlg.checkBox_GLONASS.isChecked():
            self.constellations.append("Glonass")
        if self.dlg.checkBox_GALILEO.isChecked():
            self.constellations.append("Galileo")
        if self.dlg.checkBox_BEIDOU.isChecked():
            self.constellations.append("BeiDou")

        # input epochs values:
        self.dateEpoch = str(self.dlg.dateEdit_Date.date().toPyDate()).split("-")
        self.timeEpoch = str(self.dlg.timeEdit_Time.time().toPyTime()).split(":")
        self.interval = int(self.dlg.spinBox_Interval.text())
        self.step_min = int(self.dlg.comboBox_Steps.currentText())

        return check


    def observer_position(self):
        if self.dlg.radioButton_Geogr.isChecked() or self.dlg.radioButton_Select.isChecked():
            self.geo_observer = self.inputCood_observer
            self.XYZ_observer = geographic_to_ITRF(self.geo_observer)
        else:
            self.XYZ_observer = self.inputCood_observer
            self.geo_observer = ITRF_to_geographic(self.XYZ_observer)


    def get_epochs(self):
    # calculate dates and times for each epoch:
        Y = int(self.dateEpoch[0])
        M = int(self.dateEpoch[1])
        D = int(self.dateEpoch[2])
        h = int(self.timeEpoch[0])
        m = int(self.timeEpoch[1])
        s = int(self.timeEpoch[2])

        # get number of epochs:
        interval = self.interval
        step = self.step_min
        steps = interval * 60/step

        # put all epochs into diccionary:
        obs = 1
        self.dicc_epochs = {}
        while (obs-1) <= steps:
            epoch = [Y, M, D, h, m, s]
            self.dicc_epochs[obs] = epoch
            m = m + step

            if m >= 60:
                m = m - 60
                h = h + 1
            if h == 24:
                h = 0
                D = D + 1
            dicc_dayM = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30,
                         7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
            if D > dicc_dayM[M]:
                D = 1
                M = M + 1
            if M > 12:
                M = 1
                Y = Y + 1

            obs = obs + 1  # loop

        # Define slider parameters
        self.dlg.horizontalSlider_Plot.setMinimum(1)
        self.dlg.horizontalSlider_Plot.setMaximum(obs-1)
        self.dlg.horizontalSlider_Plot.setSingleStep(1)
        self.dlg.horizontalSlider_Plot.setValue(1)


    def plot(self, plotSat_List):
        fig = Figure()
        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_title("Sky plot", va='bottom')
        ax.set_rticks([90, 75, 60, 45, 30, 15])


        if len(plotSat_List) == 0:
            pass
        else:
            self.dlg.mplvl.removeWidget(self.canvas)

            theta = [np.pi * 2]
            radii = [90]
            width = [np.pi * 2]
            bars = ax.bar(theta, radii, width=width, bottom=0.0)

            # Use custom colors and opacity
            for r, bar in zip(radii, bars):
                bar.set_alpha(0)

            # get satellites features calling Satellite_class. Get NORAD number back from txt files.
            labels = []
            positions = []
            obsNum, sat_to_plot_list  = plotSat_List[0], plotSat_List[1]
            for sat_to_plot in sat_to_plot_list:
                # get satellites NORAD number and get parameters back
                NORADnum = sat_to_plot[2]
                ve = Satellite_class(NORADnum)
                ve.getSatParameters()
                labels.append(ve.nickname)
                # get satellites position
                azSat = sat_to_plot[0] / 180 *pi # radians
                altSat = 90 - sat_to_plot[1]
                positions.append([azSat, altSat])

            # put into array
            poitionsArray = np.array(positions)
            azP = poitionsArray[:, 0]
            altP = poitionsArray[:, 1]

            # plot satellites labels
            for label, x, y in zip(labels, azP, altP):
                if label[0] == "R":   #Glonass
                    color = 'yellow'
                elif label[0] == "G": # GPS
                    color = 'red'
                elif label[0] == "C": # BeiDu
                    color = "blue"
                elif label[0] == "E":
                    color =  "green"

                ax.annotate(label, xy=(x, y), xytext=(10, -5),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.1', fc=color, alpha=0.4))

            # get skyline from txt files
            pluginPath = str(getCurrentPath())
            if self.skyline == "on":
                 horizon = np.genfromtxt(str(pluginPath) + "profiles\\" + 'horizon.txt', delimiter=',')
                 horizon = horizon[1:, :]
                # plot skyline
                 ax.plot((horizon[:, 0]) / 180 * pi , (90-horizon[:, 1]))

            # make maskline
            maskList = []
            for angle in range(0, 361):
                maskList.append([float(angle), float(self.mask)])
            maskArray = np.array(maskList)
            # plot maskline
            ax.plot((360 - maskArray[:, 0]) / 180 * np.pi , (90 - maskArray[:, 1]))

            ax.set_title("Epoch: %s/%s/%s  %sh %sm %ss" % (str(self.epoch[0]), str(self.epoch[1]), str(self.epoch[2]),str(self.epoch[3]),str(self.epoch[4]), str(self.epoch[5])), va='bottom')

        self.canvas = FigureCanvas(fig)
        self.dlg.mplvl.addWidget(self.canvas)
        self.canvas.draw()


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
