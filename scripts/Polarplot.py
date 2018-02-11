#-------------------------------------------------------------------------------
# Name:        Propagate
# Purpose:     This script is used by plot the satellites position in a skyplot.
#
# Author:      cesc
# Created:     24/01/2017
# Copyright:   (c) cesc 2017
# Licence:     Free
#-------------------------------------------------------------------------------

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, rc
import matplotlib.cbook as cbook
from math import pi
from Satellite import Satellite_class
from commonfun import getCurrentPath

class PolarChart_class ():
    def __init__(self):
        self.plt = plt

    def open_figure(self):
        pass



    def close_figure(self):
        self.plt.close()


    def plot_results(self, plotSat_List, mask, skyline_imput):
        # ----------------------------------------------------------------------
        # CONFIG POLAR CHART

        self.ax = self.plt.subplot(111, projection='polar')
        self.ax.set_theta_direction(-1)
        self.ax.set_theta_zero_location('N')
        self.ax.set_title("Satellites positions", va='bottom')
        self.ax.set_rticks([15, 30, 45, 60, 75, 90])

        theta = [np.pi * 2]
        radii = [90]
        width = [np.pi * 2]

        bars = self.ax.bar(theta, radii, width=width, bottom=0.0)

        # Use custom colors and opacity
        for r, bar in zip(radii, bars):
            if r == 90:
                bar.set_facecolor(plt.cm.jet(50))
            else:
                bar.set_facecolor(plt.cm.jet(r / 10.))

            bar.set_alpha(0.25)

    ##    # ----------------------------------------------------------------------
    ##    # CONFIG POLAR CHART
    ##
    ##    ax = plt.subplot(111, projection='polar')
    ##    ax.set_theta_direction(-1)
    ##    ax.set_theta_zero_location('N')
    ##    ax.set_title("Satellites positions", va='bottom')
    ##    ax.set_rticks([15, 30, 45, 60, 75, 90])
    ##
    ##    theta = [np.pi * 2]
    ##    radii = [90]
    ##    width = [np.pi * 2]
    ##
    ##    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    ##
    ##    # Use custom colors and opacity
    ##    for r, bar in zip(radii, bars):
    ##        if r == 90:
    ##            bar.set_facecolor(plt.cm.jet(50))
    ##        else:
    ##            bar.set_facecolor(plt.cm.jet(r / 10.))
    ##
    ##        bar.set_alpha(0.25)


        # ----------------------------------------------------------------------
        # GET OBJECTS TO PLOT

        # get satellites features calling Satellite_class. Get NORAD number back
        # from txt files.
        labels = []
        positions = []
        obsNum = plotSat_List[0]
        sat_to_plot_list = plotSat_List[1]
        for sat_to_plot in sat_to_plot_list:
            # get satellites NORAD number and get parameters back
            NORADnum = sat_to_plot[2]
            ve = Satellite_class(NORADnum)
            ve.getSatParameters()
            labels.append(ve.nickname)
            # get satellites position
            azSat = sat_to_plot[0] / 180 * pi
            altSat = 90 - sat_to_plot[1]
            positions.append([azSat, altSat])

        # put into array
        poitionsArray = np.array(positions)
        azP = poitionsArray[:, 0]
        altP = poitionsArray[:, 1]

        # plot satellites labels
    ##        c = plt.scatter(azP, altP, s=10 * 3, marker = '.')
    ##        c.set_alpha(0.75)
        for label, x, y in zip(labels, azP, altP):
            if label[0] == "R":   #Glonass
                color = 'yellow'
            elif label[0] == "G": # GPS
                color = 'red'
            elif label[0] == "C": # BeiDu
                color = "blue"

            self.plt.annotate(label, xy=(x, y), xytext=(10, -5),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.1', fc=color, alpha=0.4))


        # get skyline from txt files
        pluginPath = str(getCurrentPath())
        if skyline_imput == "on":
             horizon = np.genfromtxt(str(pluginPath) + "profiles\\" + 'horizon.txt', delimiter=',')
             horizon = horizon[1:, :]
            # plot skyline
             self.ax.plot((horizon[:, 0]) / 180 * np.pi , (90 - horizon[:, 1]))


        # make maskline
        maskList = []
        for angle in range(0, 361):
            maskList.append([float(angle), float(mask)])
        maskArray = np.array(maskList)
        # plot maskline
        self.ax.plot((360 - maskArray[:, 0]) / 180 * np.pi , (90 - maskArray[:, 1]))

        self.ax.set_title("Date" + str(obsNum), va='bottom')
        #colors = az


        # ----------------------------------------------------------------------
        # Plot chart

        return self.plt.show()

##
##if __name__ == '__main__':
##    mask = 10
##    plot_results(plotSat_List, mask)
