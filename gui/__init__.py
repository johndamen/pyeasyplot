from PyQt4 import QtGui, QtCore
from . import settings
from .figure import FigureCanvas
from .. import datasets
import matplotlib.figure
import matplotlib.cm
import numpy as np
from ..figmanager import FigureManager


class EasyPlotWindow(QtGui.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setCentralWidget(EasyPlotWidget())



class EasyPlotWidget(QtGui.QWidget):

    def __init__(self, dataset, parent=None):
        super().__init__(parent=parent)
        self.build()
        self.layers_widget.add(self.figure.gca(), dataset)

    def build(self):
        self.layout = QtGui.QHBoxLayout(self)

        # figure
        self.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure_manager = FigureManager(self.figure)

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
        self.settings_widgets = []
        self.layout.addWidget(self.settings_toolbox)

        self.fig_settings_widget = settings.FigureSettings(self.figure_manager)
        self.settings_toolbox.addItem(self.fig_settings_widget, 'Figure')

        # self.ax_settings_widget = settings.AxesSettings()
        # self.settings_toolbox.addItem(self.ax_settings_widget, 'Axes')

        # self.plot_settings_widget = settings.PlotSettings()
        # self.settings_toolbox.addItem(self.plot_settings_widget, 'Plot')

        self.layers_widget = LayersWidget(self.figure)
        self.settings_toolbox.addItem(self.layers_widget, 'Layers')

    def plot(self, hold=False):
        self.figure.hold(True)

        for l in self.layers_widget.layers:
            ax = self.figure.gca()
            l.dataset.plot(ax, **l.kwargs)

        self.figure.hold(False)

        self.canvas.draw()


class LayersWidget(QtGui.QTreeWidget):

    def __init__(self, figure):
        self.figure = figure
        self.layers = []
        super().__init__()
        self.build()

    def build(self):
        self.setHeaderHidden(True)
        self.fill()

    def fill(self):
        for ax, ls in self._layers_per_axes():
            pnt = tuple(ax._position._points.flatten())
            axitem = QtGui.QTreeWidgetItem(['Axes@({:.2f}, {:.2f}, {:.2f}, {:.2f})'.format(*pnt)])
            self.addTopLevelItem(axitem)
            for l in ls:
                axitem.addChild(l.widget())

    def add(self, ax, dataset, **kwargs):
        if not isinstance(dataset, datasets.Dataset):
            raise TypeError('invalid layer content')
        self.layers.append(PlotLayer(ax, dataset, **kwargs))
        super().clear()
        self.fill()

    def _layers_per_axes(self):
        axes = self.figure.get_axes()
        axlayers = []
        for i, a in enumerate(axes):
            axlayers.append([])
            for l in self.layers:
                print(l.ax, a, l.ax is a)
                if l.ax is a:
                    print(i, l, l.ax, a)
                    axlayers[i].append(l)

        print('L', axes, axlayers)

        return zip(axes, axlayers)

    def clear(self):
        super().clear()
        self.layers = []
        self.fill()



class PlotLayer(object):

    def __init__(self, ax, dataset, **kwargs):
        self.ax = ax
        self.dataset = dataset
        self.kwargs = kwargs
        self.color_mappable = None

    def plot(self):
        r = self.dataset.plot(**self.kwargs)
        if isinstance(r, matplotlib.cm.ScalarMappable):
            self.color_mappable = r
        return r

    def widget(self):
        return PlotLayerWidget(self)

    def __str__(self):
        return '<{}.{} around {}>'.format(__name__, self.__class__.__name__, self.dataset)


class PlotLayerWidget(QtGui.QTreeWidgetItem):

    def __init__(self, layer):
        self.layer = layer
        super().__init__([self.layer.dataset.LAYER_NAME])

        for i, ax in enumerate(self.layer.dataset.axes):
            self.addChild(QtGui.QTreeWidgetItem([
                '{}: {}'.format(self.layer.dataset.names[i], ax.shape)]))
