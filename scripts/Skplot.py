# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNSSplanning

 Predict GNSS satellites situation from users position
                              -------------------
        begin                : 2017-01-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Cesc Masdeu
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
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

import numpy as np
from math import pi


class PolarChart_class(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_mainDialog()
        self.ui.setupUi(self)

        self.plot(plotSat_List=[])


    def plot(self, plotSat_List):


        fig = Figure()

        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_title("Satellites positions", va='bottom')
        ax.set_rticks([15, 30, 45, 60, 75, 90])
        ax1f1.plot(np.random.rand(5))


        self.canvas = FigureCanvas(fig)
        self.ui.mplvl.addWidget(self.canvas)
        self.canvas.draw()





if __name__ == "__main__":
    import sys
    from PyQt4 import QtGui
    import numpy as np

    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot(np.random.rand(5))

    app = QtGui.QApplication(sys.argv)
    myapp = GNSSplanning()
    #myapp.addmpl(fig1)
    myapp.show()
    sys.exit(app.exec_())


