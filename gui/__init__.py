from PyQt4 import QtGui, QtCore
from . import settings
from .figure import FigureCanvas
from .. import datasets
import matplotlib.figure
import matplotlib.cm
from matplotlib import pyplot as plt
import numpy as np
from ..managers import FigureManager
from . import basewidgets as bw
from functools import partial


class EasyPlotWindow(QtGui.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setCentralWidget(EasyPlotWidget())


class EasyPlotWidget(QtGui.QWidget):

    def __init__(self, dataset, parent=None):
        super().__init__(parent=parent)
        self.build()

    def build(self):
        self.figure = matplotlib.figure.Figure(facecolor='none')
        self.figure_manager = FigureManager(self.figure)
        self.canvas = FigureCanvas(self.figure)

        self.layout = QtGui.QHBoxLayout(self)

        self.figure_layout = QtGui.QVBoxLayout()
        self.layout.addLayout(self.figure_layout)
        self.figure_layout.addWidget(self.canvas)

        # plot buttons
        self.plot_button_layout = QtGui.QHBoxLayout()
        self.plot_button_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_button = QtGui.QPushButton('plot')
        self.plot_button.clicked.connect(self.plot)
        self.plot_button_layout.addWidget(self.plot_button)
        self.figure_layout.addLayout(self.plot_button_layout)

        # settings
        self.settings_toolbox = QtGui.QToolBox()
        self.settings_toolbox.setFixedWidth(300)
        self.layout.addWidget(self.settings_toolbox)

        self.fig_settings_widget = settings.FigureSettings(self.figure_manager)
        self.fig_settings_widget.changed.connect(self.plot)
        self.fig_settings_widget.current_axes_changed.connect(self.change_current_axes)
        self.settings_toolbox.addItem(self.fig_settings_widget, 'Figure')

        self.ax_settings_widget = settings.AxesSettings()
        self.ax_settings_widget.changed.connect(self.set_axsettings)
        self.settings_toolbox.addItem(self.ax_settings_widget, 'Axes')

        self.plot_settings_widget = settings.PlotSettings()
        self.settings_toolbox.addItem(self.plot_settings_widget, 'Plot')

    def change_current_axes(self, i):
        old, new = i
        print(new, new.settings)
        old.format(**self.ax_settings_widget.kwargs)
        self.ax_settings_widget.set_kwargs(reset=True, **new.settings)
        self.canvas.draw()

    def set_axsettings(self, settings):
        self.figure_manager.gca().format(**settings)
        self.canvas.draw()

    def plot(self):
        for a in self.figure_manager.axes:
            a.plot()
        self.canvas.draw()