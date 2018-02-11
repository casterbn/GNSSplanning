#-------------------------------------------------------------------------------
# Name:        commonfun
# Purpose:     define common funcions
#
# Author:      cesc
#
# Created:     27/01/2017
# Copyright:   (c) cesc 2017
# Licence:     Free
#-------------------------------------------------------------------------------

import math, os

def convert(valorIn):
    stringIn = str(valorIn)
    list = stringIn.split(":")
    decimal = float(list[0]) + (float(list[1]) + float(list[2])/60)/60
    return decimal

def gra_minu_sec(angle):
    rest_gra = angle - int(angle)
    gra = int(angle - rest_gra)

    minu_dec = rest_gra*60

    rest_minu = minu_dec - int(minu_dec)
    minu = int(minu_dec - rest_minu)

    sec = rest_minu*60

    angle_string = "%i, %i, %f" % (gra, minu, sec)

    return angle_string

def truncate(value):
    '''(value)-> value truncated multiple of 5
    Truncate a float number to his nearest upper or lower integer multiple of 5.
    >>>truncate(27.65)
    30
    >>>truncate(27.45)
    25
    '''
    b = math.trunc(value)
    c = (b - int(str(b)[-1]))
    d = value - c
    if d < 2.5:
        v_trun = c
    elif d >7.5:
        v_trun = c + 10
    else:
        v_trun = c + 5
    return v_trun

def getCurrentPath():
    '''()-> current path
    Get the current path where the python file are.
    >>>pluginPath()
    C:\Users\username\.qgis2\python\plugins\Myplugin\
    '''
    filePath = os.path.abspath(__file__)
    pluginPath = ""
    try:
        path_list = filePath.split("\\")
        path_list.pop(-1)

        for path in path_list:
            pluginPath= pluginPath + path + "\\"
    except:
        pluginPath = os.path.abspath(__package__)
        pluginPath = pluginPath + "\\"

    return pluginPath