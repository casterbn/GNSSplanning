"""
-------------------------------------------------------------------------------
Name:        Capture_coords
Purpose:     This script capture coordinates from canvas
Created:     2017 by Cesc Masdeu Ferrer
Licence:     Free
------------------------------------------------------------------------------
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ..gnss_planning_dialog import GNSSplanningDialog

class CaptureCoords(QgsMapTool):
    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self.canvas = iface.mapCanvas()

        self.dlg = GNSSplanningDialog()


    def canvasReleaseEvent(self, event):
        #Get the click
        crsSrc = self.canvas.mapRenderer().destinationCrs()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.x_crs = event.pos().x()
        self.y_crs = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(self.x_crs, self.x_crs)

        #convert coords to EPSG:4326
        crsWGS = QgsCoordinateReferenceSystem(4326)
        xform_WGS84 = QgsCoordinateTransform(crsSrc, crsWGS)
        point_WGS84 = xform_WGS84.transform(QgsPoint(point.x(),point.y()))
        QApplication.restoreOverrideCursor()
        self.x_WGS = str(point_WGS84.x())
        self.y_WGS = str(point_WGS84.y())

        #convert coords to EPSG:25831
        crsETRS89 = QgsCoordinateReferenceSystem(25831)
        xform_ETRS89 = QgsCoordinateTransform(crsSrc, crsETRS89)
        point_ETRS89 = xform_ETRS89.transform(QgsPoint(point.x(),point.y()))
        QApplication.restoreOverrideCursor()
        self.x_UTM = str(point_ETRS89.x())
        self.y_UTM = str(point_ETRS89.y())


