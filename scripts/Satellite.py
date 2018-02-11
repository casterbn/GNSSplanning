"""
-------------------------------------------------------------------------------
Name:        Satellite
Purpose:     This script define satellites propieties.
Created:     2017 by Cesc Masdeu Ferrer
Licence:     Free
------------------------------------------------------------------------------
"""


import math
import os
from numpy import array, cross, einsum, zeros_like
from sgp4.earth_gravity import wgs84    # python-sgp4 (Copyright ? 2012?2016 Brandon Rhodes)
from sgp4.io import twoline2rv          # python-sgp4 (Copyright ? 2012?2016 Brandon Rhodes)
from transform import julian_date, TEME_to_ITRF, ITRF_to_geographic, ITRF_to_horizontal
#import ephem
from commonfun import convert, getCurrentPath

#-------------------------------------------------------------------------------
# SATELLITE OBJECT:
#

class Satellite_class():
    def __init__(self, satNum):
        self.satNum = satNum  # NORAD NUM

    def getSatParameters(self):
        '''(satNum)-> Satellite parameters
        Get satellites parameters from .sat (files with TLE format).
        >>>Satellite.getSatParameters('41586')
        BsiDou      # constellation
        G7          # nickname
        41586       # NORAD number
        U           # unclassified
        etc...
        '''
        # get the plugin path from this file path
        pluginPath = str(getCurrentPath())

        # open TLE file for reading
        satfile = open(pluginPath + 'sat\\' + self.satNum + '.sat', 'r')

        # read 3 lines at a time; strip trailing whitespaces
        self.line0 = satfile.readline().strip()
        self.line1 = satfile.readline().strip()
        self.line2 = satfile.readline().strip()
        self.line3 = satfile.readline().strip()
        self.listIDsat = self.line3.split(" ")
        a = math.pow(3,3)

        # create a SDP4 object
        self.satSDP4 = twoline2rv(self.line1, self.line2, wgs84)

        # create a ephem object
        #self.satEphem = ephem.readtle(self.line0, self.line1, self.line2)

        # define satellites parameters
        self.constellation = self.listIDsat[5]
        self.block = self.listIDsat[6]
        self.name = self.listIDsat[4]
        self.nickname = self.listIDsat[1]
        self.prn = self.listIDsat[2]
        self.sv = self.listIDsat[3]
        self.norad = self.line1[2:7]
        self.clasUnclas = self.line1[7]
        self.launchYear = self.line1[9:11]
        self.launchNumber = self.line1[11:14]
        self.launchPice = self.line1[14:17]
        self.epochYear = self.line1[18:20]
        self.epochDay = self.line1[20:32]
        self.firstDMM = self.line1[33:43]
        self.secondDMM = self.line1[44:52]
        self.dragBSTAR = self.line1[53:61]
        self.ephemType = self.line1[62]
        self.elementSet = self.line1[64:68]
        self.checksum1 = self.line1[68]
        self.inclination = self.line2[8:16]
        self.raan = self.line2[17:25]
        self.eccentricity = "0." + self.line2[26:33]
        self.augPerigee = self.line2[34:42]
        self.meanAnomaly = self.line2[43:51]
        self.meanMotion = self.line2[52:63]
        self.revolution = self.line2[63:68]
        self.checksum2 = self.line2[68]



    def getPosition_TEME(self, dateTime):
        '''(dateTime)-> position and velocity
        Get position and velocity from satellite object into TEME frame
        >>>Satellite("29601").getPosition_TEME([2017, 01, 03, 0, 0, 0.0])
        (-26237.73044512979, 4795.304682136226, 413.75989340053593)       # position
        (-0.44695695555351667, -2.0707587248243144, -3.2234138176852225)  # velocity
        '''
        # propagate position and velocity (TEME)
        self.position_TEME, self.velocity_TEME = self.satSDP4.propagate(*dateTime)
        self.X_TEME = self.position_TEME[0]
        self.Y_TEME = self.position_TEME[1]
        self.Z_TEME = self.position_TEME[2]

        return self.position_TEME, self.velocity_TEME



    def getPosition_ITRF(self, dateTime):
        '''(dateTime)-> position and velocity
        Get position and velocity from satellite object into ITRF frame
        >>>Satellite("29601").getPosition_ITRF([2017, 01, 03, 0, 0, 0.0])
        (-26237.73044512979, 4795.304682136226, 413.75989340053593)       # position
        (-0.44695695555351667, -2.0707587248243144, -3.2234138176852225)  # velocity
        '''
        # first, get poition into TEME frame
        position_from_TEME, velocity_from_TEME = self.getPosition_TEME(dateTime)

        # transform TEME into ITRF
        year, month, day     = dateTime[0], dateTime[1], dateTime[2]
        hour, minute, second = dateTime[3], dateTime[4], dateTime[5]
        jday = julian_date(year, month, day, hour, minute, second)

        position_ITRF_KM, velocity_ITRF_KM = TEME_to_ITRF(jday, position_from_TEME, velocity_from_TEME)

        self.X_ITRF = position_ITRF_KM[0] * 1000
        self.Y_ITRF = position_ITRF_KM[1] * 1000
        self.Z_ITRF = position_ITRF_KM[2] * 1000
        self.i_ITRF = velocity_ITRF_KM[0]
        self.j_ITRF = velocity_ITRF_KM[1]
        self.k_ITRF = velocity_ITRF_KM[2]
        self.position_ITRF = [self.X_ITRF, self.Y_ITRF, self.Z_ITRF]
        self.velocity_ITRF = [self.i_ITRF, self.j_ITRF, self.k_ITRF]

        return self.position_ITRF, self.velocity_ITRF



    def getPosition_geo(self, dateTime):
        '''(dateTime)-> position
        Get position and velocity from satellite object in geographic sr
        >>>Satellite("29601").getPosition_geo([2017, 01, 03, 0, 0, 0])
        (47.869896160692306, -8.005048373017335, 20034419.68723937)  # lat, lon, alt(elip)
        '''
        # first, get poition into ITRF frame
        position_from_ITRF = self.getPosition_ITRF(dateTime)[0]
        # transform ITRF(XYZ) into geographic
        self.position_geo = ITRF_to_geographic(position_from_ITRF)
        self.lon = self.position_geo[0]
        self.lat = self.position_geo[1]
        return self.position_geo



    def getPosition_azalt_op2(self, geo_observer, dateTime):
        '''(observer_geo, dateTime)-> Satellite position
        Get satellite position (altitude and azimut) from observer
        situation (geographic coord: longitude, latitude and elevation)
        at a specific date and time, by using TLE files.
        >>>Satellite.getPosition([2.2399, 41.4451, 5.14], [2017, 01, 01, 20, 00, 00.0])
        40.6438611111, 16.1937222222      # decimal degrees
        '''
        observer = ephem.Observer()
        observer.lon = geo_observer[0]
        observer.lat = geo_observer[1]
        observer.elevation = geo_observer[2]
        date_time = str(dateTime[0]) + "/" + str(dateTime[1]) + "/" + str(dateTime[2]) + " " + str(dateTime[3]) + ":" + str(dateTime[4])
        observer.date = date_time

        # compute observer
        self.satEphem.compute(observer)

        self.altitude = convert(self.satEphem.alt)
        self.azimut = convert(self.satEphem.az)
        self.nameEphem = self.satEphem.name

        return  self.azimut, self.altitude



    def getPosition_azalt(self, geo_observer, XYZ_observer, dateTime):
        '''(geo_observer, XYZ_observer, dateTime)-> az, alt, D
        Get satellite position from observer situation at a specific date and time
        by using TLE files.
        Observer position:
            - geographic coord (longitude, latitude and elevation),
            - UTM projection (x, y, H) #TODO
            - Geocentric ITRF
        satellite position:
            - hotizontal coord (azimut, altitude)

        >>>Satellite.getPosition_azalt([41.5996, 1.40113, 853.3707],
                                       [4775849.592, 116814.09, 4213018.69],
                                       [2017, 01, 01, 20, 00, 00.0])
        287.678319329999, 76.5702066161654     # decimal degrees
        '''

        # get satellite position into ITRF frame
        XYZ_sat = self.getPosition_ITRF(dateTime)[0]

        # transform sat position into hoizontal coordenates
        self.position_azalt = ITRF_to_horizontal(geo_observer, XYZ_observer, XYZ_sat)
        self.az = self.position_azalt[0]
        self.alt = self.position_azalt[1]
        self.D = self.position_azalt[2]
        return self.az, self.alt, self.D

