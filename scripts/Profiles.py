#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      cesc
#
# Created:     12/02/2017
# Copyright:   (c) cesc 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import qgis
from qgis.core import *
from qgis.gui import *
from math import sin, cos, radians

def linesProfiles(x, y):
    x0 = 470677.5
    y0 = 4659112.5
    node_list = []

    for angle in list(range(0, 360, 5)):
        xi = x0 + 200 * sin(radians(angle))
        yi = y0 + 200 * cos(radians(angle))
        node_list.append([xi, yi])


    vectorLayer = QgsVectorLayer("C:\Users\cesc\.qgis2\python\plugins\GNSSplanning\scripts\profiles\Lines_to_horizon.shp", "Profiles", "ogr")
    vectorLayer.isValid()
    vrp = vectorLayer.dataProvider()
    for node in node_list:
        points = []
        points.append(QgsPoint(x0, y0))
        points.append(QgsPoint(node[0],node[1]))
        line = QgsGeometry.fromPolyline(points)
        f = QgsFeature()
        f.setGeometry(line)
        vrp.addFeatures([f])
        vectorLayer.updateExtents()


    return node_list

##
##print lines_profile()

