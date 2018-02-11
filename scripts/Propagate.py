

"""
-------------------------------------------------------------------------------
Name:        Propagate
Purpose:     This script is used by get satellites positions.
Created:     2017 by Cesc Masdeu Ferrer
Licence:     Free
------------------------------------------------------------------------------
"""

import os, shutil
import numpy as np
from Satellite import Satellite_class
from Polarplot import PolarChart_class
from DOP import getDOP_values
from commonfun import truncate, getCurrentPath


def propagate(geo_observer, XYZ_observer, epoch, epochNum, mask, skyline, constellations):

    # --------------------------------------------------------------------------
    # INICIALIZATION PROCES
    # get the module path from getCurrentPath()
    modulePath = str(getCurrentPath())
    s = -18.13
    resultats = []

    # get skyline from txt files
    if skyline == "on":
        skyL = np.genfromtxt(modulePath + "profiles\\" + 'horizon.txt', delimiter=',')

    # --------------------------------------------------------------------------
    # READ SATELLITES EFEMERIDES
    listSat = []
    for file in os.listdir(modulePath + 'sat\\'):
        try:
            if file[-1] == "t":
                fileName = file.split(".")[0]
                listSat.append(fileName)
        except Exception as e:
            pass

    #---------------------------------------------------------------------------
    # PROPAGATE SATELLITES POSITION FOR THE EPOCH
    overMask_sats_AzAlt = []
    overMask_sats_XYZ= {}

    plotSat_List = []  # list with 2 items: #1 number of epoch; #2 list of all satellite's coordinates (Az, Alt, NORAD num).
    XYZSat_List = []   # list with 2 items: #1 number of epoch; #2 dicctionary with: key = nickname, value = coordinates (X, Y, Z); for all satellites.


    # search wich satellites are in constelation list and over the masks:
    for satellite in listSat:
        # define satellite like a object:
        ve = Satellite_class(satellite)
        ve.getSatParameters()

        # is the satellite constellation in the constellations list that user has selected?:
        if ve.constellation in constellations:
            # if yes, let's to propagate its position on the epoch
            # and get the azimute and altitude from user position:
            ve.getPosition_azalt(geo_observer, XYZ_observer, epoch )          # with sgp4
            # now, is this sat at this epoch overs the mask that user has marked?:
            if ve.alt > mask:
                # then, search if it is over the skyline:
                if skyline == "on":
                    azSat_Trunc = truncate(ve.az)  # truncate azimute value to multip-5 to comapre witn skylines points
                    for skyL_point in skyL:
                        if skyL_point[0] == azSat_Trunc:   # compare only the skyline-point with the same azimute as sat's one
                            altDif =  ve.alt - skyL_point[1]   # altDif = (skyline altitude) - (sat altitude)
                            # if sat is over the skyline, then put it into a list with sats that will be ploted:
                            if altDif >= 0:
                                overMask_sats_AzAlt.append([ve.az, ve.alt, ve.norad])
                                overMask_sats_XYZ[ve.nickname] =  [ve.X_ITRF, ve.Y_ITRF, ve.Z_ITRF]
                else:
                    overMask_sats_AzAlt.append([ve.az, ve.alt, ve.norad])
                    overMask_sats_XYZ[ve.nickname] =  [ve.X_ITRF, ve.Y_ITRF, ve.Z_ITRF]
    # --------------------------------------------------------------------------

    # packed everything for plotting:
    plotSat_List.append(epochNum)
    plotSat_List.append(overMask_sats_AzAlt)
    # packed everything for DOP:
    XYZSat_List.append(epochNum)
    XYZSat_List.append(overMask_sats_XYZ)

    return plotSat_List, XYZSat_List, resultats





#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

##if __name__ == '__main__':
##    # Example:
##    geo_observer = [1.40113711458437, 41.5996152901421, 853.37078135088]
##    XYZ_observer = [4775849.592, 116814.09, 4213018.694]
##    epoch = [2017, 01, 29, 20, 00, 0.0]
##    mask = 10.0
##    skyline = "on"
##    constellations = ["GPS", "Glonass", "Galileo", "BeiDou"]
##
##    results = propagate(geo_observer, XYZ_observer, epoch, 1, mask, skyline, constellations)
##    plotSat_List = results[0]
##    XYZSat_List = results[1]
##
##    print "DOP:", getDOP_values(XYZ_observer, XYZSat_List[1])
##
##
##    plot = PolarChart_class()
##    plot.plot_results(plotSat_List, mask, skyline)
