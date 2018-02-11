"""
-------------------------------------------------------------------------------
Name:        transform
Purpose:     This script transfor coordinates into diferents systems.
Created:     2017 by Cesc Masdeu Ferrer
Licence:     Free
------------------------------------------------------------------------------
"""

import numpy as np
from math import pi, pow, acos, asin, atan, sqrt, sin, cos, radians, atan2
import math
import os
from numpy import array, cross, einsum, zeros_like

# CONSTANTS:
# ----------
# Time:
DAY_S = 86400.0
T0 = 2451545.0
_second = 1.0 / (24.0 * 60.0 * 60.0)

# Angles.
tau = 6.283185307179586476925287  # lower case, for symmetry with math.pi

# WGS84
e2 = 0.0066943800
a = 6378137


# ------------------------------------------------------------------------------
# Rotation
def rot_x(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return array([(1.0, 0.0, 0.0), (0.0, c, -s), (0.0, s, c)])

def rot_y(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return array([(c, 0.0, s), (0.0, 1.0, 0.0), (-s, 0.0, c)])

def rot_z(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    zero = theta * 0.0
    one = zero + 1.0
    return array(((c, -s, zero), (s, c, zero), (zero, zero, one)))


# ------------------------------------------------------------------------------
def theta_GMST1982(jd_ut1):
    '''Return the angle of Greenwich Mean Standard Time 1982 given the JD.
    This angle defines the difference between the idiosyncratic True
    Equator Mean Equinox (TEME) frame of reference used by SGP4 and the
    more standard Pseudo Earth Fixed (PEF) frame of reference.
    From AIAA 2006-6753 Appendix C.
    '''
    t = (jd_ut1 - T0) / 36525 # One sidereal second is approximately 365.25/366.25

    g = 67310.54841 + 8640184.812866 * t + 0.093104 * math.pow(t,2) -(0.0000062) * math.pow(t,3) #GMST (in seconds at UT1=0)
    dg = 8640184.812866 * t + 0.093104 * 2 * math.pow(t,2) -(0.0000062) * math.pow(t,3)

    theta = (jd_ut1 % 1.0 + g * _second % 1.0) * tau
    theta_dot = (1.0 + dg * _second / 36525.0) * tau
    return theta, theta_dot


# ------------------------------------------------------------------------------
def julian_day(year, month, day):
    """Given a proleptic Gregorian calendar date, return a Julian day int."""
    janfeb = month
    return (day
            + 1461 * (year + 4800 - janfeb) // 4
            + 367 * (month - 2 + janfeb * 12) // 12
            - 3 * ((year + 4900 - janfeb) // 100) // 4
            - 32075)


# ------------------------------------------------------------------------------
def julian_date(year, month, day, hour, minute, second):
    """Given a proleptic Gregorian calendar date, return a Julian date float."""
    return julian_day(year, month, day) - 0.5 + (
        second + minute * 60.0 + hour * 3600.0) / DAY_S


# ------------------------------------------------------------------------------
def TEME_to_ITRF(jd_ut1, rTEME, vTEME, xp=0.0, yp=0.0):
    '''Convert TEME position and velocity into standard ITRS coordinates.
    This converts a position and velocity vector in the idiosyncratic
    True Equator Mean Equinox (TEME) frame of reference used by the SGP4
    theory into vectors into the more standard ITRS frame of reference.
    The velocity should be provided in units per day, not per second.
    From AIAA 2006-6753 Appendix C.
    '''
    theta, theta_dot = theta_GMST1982(jd_ut1)
    zero = theta_dot * 0.0
    angular_velocity = array([zero, zero, -theta_dot])
    R = rot_z(-theta)

    if len(rTEME) == 1:
        rPEF = (R).dot(rTEME)
        vPEF = (R).dot(vTEME) + cross(angular_velocity, rPEF)
    else:
        rPEF = einsum('ij...,j...->i...', R, rTEME)
        vPEF = einsum('ij...,j...->i...', R, vTEME) + cross(
            angular_velocity, rPEF, 0, 0).T

    if xp == 0.0 and yp == 0.0:
        rITRF = rPEF
        vITRF = vPEF
    else:
        W = (rot_x(yp)).dot(rot_y(xp))
        rITRF = (W).dot(rPEF)
        vITRF = (W).dot(vPEF)

    return rITRF, vITRF


# ------------------------------------------------------------------------------
def ITRF_to_geographic(XYZ_coordinates):   # WGS84
    '''Convert geocentric coordinates into geographics coordinates.
    '''
    X = XYZ_coordinates[0]
    Y = XYZ_coordinates[1]
    Z = XYZ_coordinates[2]

    D = sqrt((pow(X,2) + pow(Y,2)))
    lat0 = atan(Z/(D*(1-e2)))

    # iteration
    #1
    N = a/sqrt(1-e2*sin(pow(lat0,2)))
    lat0 = atan((Z+e2*N*sin(lat0))/D)
    #2
    N = a/sqrt(1-e2*pow(sin(lat0),2))
    lat0 = atan((Z+e2*N*sin(lat0))/D)
    #3
    N = a/sqrt(1-e2*pow(sin(lat0),2))
    lat0 = atan((Z+e2*N*sin(lat0))/D)


    lat = lat0*180/pi
    lon = atan(Y/X)*180/pi
    h = D/cos(radians(lat))-N

    return lon, lat, h

# ------------------------------------------------------------------------------
def geographic_to_ITRF (geo_coordinates):   # WGS84
    '''Convert geographic coordenates into geocentric coordinates.
    '''
    lon = geo_coordinates[0]
    lat = geo_coordinates[1]
    h = geo_coordinates[2]

    N = a/sqrt(1-e2*pow(sin(radians(lat)),2))

    X = (N+h)*cos(radians(lat))*cos(radians(lon))
    Y = (N+h)*cos(radians(lat))*sin(radians(lon))
    Z = (N*(1-e2)+h)*sin(radians(lat))

    return X, Y, Z


# ------------------------------------------------------------------------------
def ITRF_to_horizontal(geo_observer, XYZ_observer, XYZ_sat):

    # XYZ observer geocentric coordenates
    #print observer_XYZ
    Xobs = XYZ_observer[0]
    Yobs = XYZ_observer[1]
    Zobs = XYZ_observer[2]

    # lon,lat,h observer geographic coordinates
    lon = radians(geo_observer[0])
    lat = radians(geo_observer[1])
    h = geo_observer[2]

    # XYZ satellite geocentric coordenates
    Xsat = XYZ_sat[0]
    Ysat = XYZ_sat[1]
    Zsat = XYZ_sat[2]

    # Calculate increments
    dX = Xsat - Xobs
    dY = Ysat - Yobs
    dZ = Zsat - Zobs
    incr = [[dX],[dY],[dZ]]
    m_incr = np.matrix(incr) # convert to matrix notation

    # rotation matrix transposed (R)T
    rota = [[-sin(lat)*cos(lon) , -sin(lat)*sin(lon) , cos(lat)],
            [-sin(lon)          , cos(lon)           , 0],
            [cos(lat)*cos(lon)  , cos(lat)*sin(lon)  , sin(lat)]]

    m_rota = np.matrix(rota) # convert to matrix notation

    # transform to ENU coordanates (north, est, up)
    matrix = m_rota * m_incr

    north = matrix[0]
    est = matrix[1]
    up = matrix[2]

    # calculate horizontal coordenates
    D = sqrt(pow(north,2) + pow(est,2) + pow(up,2))
    alpha = atan(est/north)*180/pi
    beta = acos(up/D)*180/pi

    if north < 0:                # 2on and 3rd quadrant
        az = alpha + 180
    elif est < 0 and north >= 0: # 4th quadrant
        az = alpha + 360
    else:                        # 1st quadrant
        az = alpha

    alt = 90-beta

    return az, alt, D

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    # Example:
    geo_observer = [1.40113711458437, 41.5996152901421, 853.37078135088]
    XYZ_observer = [4775849.592, 116814.09, 4213018.694]
    XYZ_sat = [18601508.915, -4007872.905, 18296194.859]

    print "Satellite horizontal coordinates (azimut, altitude, distance):"
    print ITRF_to_horizontal(geo_observer, XYZ_observer, XYZ_sat)
    print
