"""
-------------------------------------------------------------------------------
Name:        DOP
Purpose:     This script calculate DOP values.
Created:     2017 by Cesc Masdeu Ferrer
Licence:     Free
------------------------------------------------------------------------------
"""

import numpy as np
from math import sqrt, pow
import itertools
from random import shuffle


def dop(XYZ_satGroup, XYZ_obs):

    x,  y,  z  = XYZ_obs[0], XYZ_obs[1], XYZ_obs[2]

    # measurement residual equations
    vector_list = []
    for sat in XYZ_satGroup:
        xsat, ysat, zsat = sat[0], sat[1], sat[2]
        R = sqrt(pow(xsat-x,2) + pow(ysat-y,2) + pow(zsat-z,2))
        i = -((xsat-x)/R)
        j = -((ysat-y)/R)
        k = -((zsat-z)/R)
        l = 1

        vector = [i,j,k,l]
        vector_list.append(vector)

    A = np.array(vector_list)

    # AT = transpose of A
    AT = A.transpose()

    # AT*A (AT is 4x4 matrix, A is 4x4 matrix, result is 4x4)
    ATA = [[0,0,0,0],
           [0,0,0,0],
           [0,0,0,0],
           [0,0,0,0]]

    # iterate through rows of AT
    for i in range(len(AT)):
       # iterate through columns of A
       for j in range(len(A[0])):
           # iterate through rows of A
           for k in range(len(A)):
               ATA[i][j] += AT[i][k] * A[k][j]

    # Q = (AT * A)^-1
    Q = np.linalg.inv(ATA)

    PDOP = sqrt(Q[0][0] + Q[1][1] + Q[2][2])
    TDOP = sqrt(Q[3][3])
    GDOP = sqrt(pow(PDOP,2) + pow(TDOP,2))
    HDOP = sqrt(Q[0][0] + Q[1][1])
    VDOP = sqrt(Q[2][2])

    return GDOP, PDOP, TDOP, HDOP, VDOP


def getDOP_values(XYS_obs, sat_dicc):

    pack_minGDOP_list = []
    all_minGDOP_list = []

    # list satellite's nicknames:
    sat_list = sat_dicc.keys()

    # uncomment next line if you want explore all possible combination --> minium pack:4 satellites, maximum pack: all satellites.
    #num_of_Sats_packs = range(4, len(sat_list)+1)
    num_of_Sats_packs = [len(sat_list)-1, len(sat_list)] # calclate DOP ussing pack of n and n-1 satellites (n = all visible satellites).

    for num_of_Sats in num_of_Sats_packs:

        # get all group of n satellites combinations
        combinations = list(itertools.combinations(sat_list, num_of_Sats))

        # calculate DOP values for each grup-of-satellites combination:
        DOP_dicc = {}


        for group in combinations:
            # get satellite coordinates from nickname
            XYZ_group = []
            position_in_group = 0
            for sat in group:
                name_Sat = group[position_in_group]
                coord_Sat = sat_dicc[name_Sat]
                XYZ_group.append(coord_Sat)
                position_in_group = position_in_group +1
            # calculate DOPs values and put into a dicctionary (key = list with nickname's sats of group).
            DOP_dicc[group] =  dop(XYZ_group, XYS_obs)

        # find the minium value of GDOP for this pack combination.
        pack_GDOP_list = []
        for key, value in DOP_dicc.items():
            #print key, value
            pack_GDOP_list.append(value[0])
        pack_GDOP_list.sort()   # sort from lowest to highest

        # get the winner group combination
        for key, value in DOP_dicc.items():
            if value[0] == pack_GDOP_list[0]:
                pack_min_GDOP = [key, value]
            else:
                pass
        pack_minGDOP_list.append(pack_min_GDOP[1])

    # find the minium value of GDOP of all packs combinations.
    for pack_minGDOP_value in pack_minGDOP_list:
        all_minGDOP_list.append(pack_minGDOP_value[0])
    all_minGDOP_list.sort()

    # get the absolutte winner combination
    for key, value in DOP_dicc.items():
        if value[0] == all_minGDOP_list[0]:
            winner_group = [key, value]
        else:
            pass

    return winner_group


if __name__ == '__main__':
    # Example:

    # reciver position:
    x,  y,  z  =  4775849.5920,   116814.0900,   4213018.6940
    XYS_obs = [x, y, z]

    # satellites positons from sp3.file (all them were over the sky at 00:00:00 UTC on February 6, 2017)
    #PG10  24264.678734   9943.249790  -4539.395528
    #PG16  16763.418913  -4645.178323  20083.661194
    #PG18  20421.590171  16049.488781   6646.723939
    #PG20    985.159617  17044.372504  20191.143319
    #PG21  14133.584242   9415.442157  21233.454960
    #PG26  22904.187847   1885.120659  13388.941241
    #PG27  12317.666972 -14483.095171  18422.147533
    #PG29   5318.333481  24202.920066   9606.370407
    #PG31  24084.045448  -5008.747792 -10431.348387

    sat_dicc = {"G10": [24264678.734, 9943249.790, -4539395.528],
            "G16": [16763418.913, -4645178.323, 20083661.194],
            "G18": [20421590.171, 16049488.781, 6646723.939],
            "G20": [985159.617, 17044372.504, 20191143.319],
            "G21": [14133584.242, 9415442.157, 21233454.960],
            "G26": [22904187.847, 1885120.659, 13388941.241],
            "G27": [12317666.972, -14483095.171, 18422147.533],
            "G29": [5318333.481, 24202920.066, 9606370.407],
            "G31": [24084045.448, -5008747.792, -10431348.387]}

    print getDOP_values(XYS_obs, sat_dicc)
