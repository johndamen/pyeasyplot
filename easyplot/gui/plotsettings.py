from PyQt4 import QtGui, QtCore
from .settings import PlotSettings
from . import basewidgets as bw
from .. import datasets



def _marker_field(**kwargs):
    return bw.Dropdown(
        ['.', ',', 'o', '*',
         '+', 'x', 'd', 'D',
         'v', '^', '<', '>',
         's', 'p', '|', '_'], **kwargs)


def _label_field(*args, **kwargs):
    return bw.TextOrNone(*args, **kwargs)


def _linestyle_field(**kwargs):
    return bw.Dropdown(['-', '--', '-.', ':'], **kwargs)


def _linewidth_field(*args, **kwargs):
    return bw.Float(*args, **kwargs)


def _width_field(*args, **kwargs):
    return bw.Float(*args, **kwargs)


def _color_field(*args, **kwargs):
    return bw.Color(*args, **kwargs)


def _cmap_field(*args, **kwargs):
    return bw.Colormap(*args, **kwargs)


def _alpha_field(*args, **kwargs):
    return bw.Float(*args, **kwargs)


def _size_field(*args, **kwargs):
    return bw.Float(*args, **kwargs)


class TimeseriesPlotSettings(PlotSettings):

    DATA_CLS = datasets.Timeseries

    def build(self):
        super().build()
        self.fields['alpha'] = f = _alpha_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('alpha', f)

        self.fields['color'] = f = _color_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('color', f)

        self.fields['linewidth'] = f = _linewidth_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('linewidth', f)

        self.fields['linestyle'] = f = _linestyle_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('linestyle', f)

        self.fields['label'] = f = _label_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('label', f)

        self.fields['marker'] = f = _marker_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('marker', f)


class PointsPlotSettings(PlotSettings):

    DATA_CLS = datasets.Points

    def build(self):
        super().build()
        self.fields['color'] = f = _color_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('color', f)

        self.fields['s'] = f = _size_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('pointsize', f)

        self.fields['alpha'] = f = _alpha_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('alpha', f)



class ValuePointsPlotSettings(PlotSettings):

    DATA_CLS = datasets.ValuePoints

    def build(self):
        super().build()
        self.fields['cmap'] = f = _cmap_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('colormap', f)

        self.fields['s'] = f = _size_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('pointsize', f)

        self.fields['alpha'] = f = _alpha_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('alpha', f)


class GridPlotSettings(PlotSettings):

    DATA_CLS = datasets.Grid

    def build(self):
        super().build()
        self.fields['cmap'] = f = _cmap_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('colormap', f)


class IrregularGridPlotSettings(PlotSettings):

    DATA_CLS = datasets.IrregularGrid

    def build(self):
        super().build()
        self.fields['cmap'] = f = _cmap_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('colormap', f)


class VectorDataPlotSettings(PlotSettings):

    DATA_CLS = datasets.VectorData

    def build(self):
        super().build()
        self.fields['width'] = f = _width_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('width', f)

        self.fields['color'] = f = _color_field()
        f.value_changed.connect(self.change)
        self.layout.addRow('color', f)


def get_by_dataset(d):
    if not isinstance(d, datasets.Dataset):
        raise TypeError('argument must be a dataset')
    return globals()[d.__class__.__name__+'PlotSettings']