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

    def __init__(self, *datasets, parent=None):
        super().__init__(parent=parent)

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

        self.dataset_selector = DatasetSelectorWidget(datasets)
        self.dataset_selector.added.connect(self.add_datasets)
        self.settings_toolbox.addItem(self.dataset_selector, 'Datasets')

        self.fig_settings_widget = settings.FigureSettings(self.figure_manager)
        self.fig_settings_widget.changed.connect(self.plot)
        self.fig_settings_widget.current_axes_changed.connect(self.change_current_axes)
        self.settings_toolbox.addItem(self.fig_settings_widget, 'Figure')

        self.ax_settings_widget = settings.AxesSettings()
        self.ax_settings_widget.changed.connect(self.set_axsettings)
        self.settings_toolbox.addItem(self.ax_settings_widget, 'Axes')

        self.plot_stack = settings.PlotStack()
        self.plot_stack.changed.connect(self.set_plotsettings)
        self.settings_toolbox.addItem(self.plot_stack, 'Plot')

        self.plot_settings_widget = settings.LegendSettings()
        self.settings_toolbox.addItem(self.plot_settings_widget, 'Legend')

        self.plot_settings_widget = settings.ColorbarSettings()
        self.settings_toolbox.addItem(self.plot_settings_widget, 'Colorbar')

    def change_current_axes(self, i):
        old, new = i
        old.format(**self.ax_settings_widget.kwargs)
        self.ax_settings_widget.set_kwargs(reset=True, **new.settings)
        self.canvas.draw()

    def set_plotsettings(self, settings):
        self.figure_manager.gca().layers.edit_current(**settings)
        self.plot()

    def set_axsettings(self, settings):
        self.figure_manager.gca().format(**settings)
        self.canvas.draw()

    def plot(self):
        for a in self.figure_manager.axes:
            a.plot()
        self.canvas.draw()

    def add_datasets(self, datasets):
        for d in datasets:
            print('adding', d)
            ax = self.figure_manager.gca()
            ax.layers.add(d)
            xlim, ylim = d.limits()
            ax.check_limits(xlim=xlim, ylim=ylim)
            self.plot_stack.for_dataset(d)
            self.settings_toolbox.setCurrentWidget(self.plot_stack)
        self.plot()


class DatasetSelectorWidget(QtGui.QWidget):

    added = QtCore.pyqtSignal(list)

    def __init__(self, datasets):
        self.datasets = datasets
        super().__init__()
        self.build()

    def build(self):
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 0, 0)
        self.list_widget = QtGui.QTreeWidget()
        self.list_widget.setColumnCount(2)
        self.list_widget.setColumnWidth(0, 150)
        self.list_widget.setHeaderHidden(True)
        self.layout.addWidget(self.list_widget)
        for d in self.datasets:
            self.list_widget.addTopLevelItem(DatasetItem(d))
        self.layout.addItem(QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding))
        self.button = QtGui.QPushButton('add')
        self.button.clicked.connect(self.add)
        self.layout.addWidget(self.button)

    def add(self):
        self.added.emit([i.dataset for i in self.list_widget.selectedItems()])


class DatasetItem(QtGui.QTreeWidgetItem):

    def __init__(self, d):
        self.dataset = d
        super().__init__([self.dataset.LAYER_NAME])
        for n, a in self.dataset:
            self.addChild(QtGui.QTreeWidgetItem([n, str(a.shape)]))



