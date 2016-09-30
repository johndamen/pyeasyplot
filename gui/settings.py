from PyQt4 import QtGui, QtCore
from . import basewidgets as bw
from .utils import clear_layout
from functools import partial
from matplotlib import pyplot as plt
from collections import OrderedDict, ChainMap
import numpy as np


class SettingsWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.build()

    def build(self):
        pass


class FigureSettings(SettingsWidget):

    changed = QtCore.pyqtSignal()
    current_axes_changed = QtCore.pyqtSignal(tuple)

    def __init__(self, figure_manager, parent=None):
        self.figure_manager = figure_manager
        super().__init__(parent=parent)

    def build(self):
        self.layout = QtGui.QFormLayout(self)

        self.axnum_field = bw.Int(self.figure_manager.ax_count())
        self.axnum_field.value_changed.connect(self.set_ax_count)
        self.layout.addRow('axes', self.axnum_field)

        self.axrownum_field = bw.Int(self.figure_manager.axrow_count())
        self.axrownum_field.value_changed.connect(self.set_axrow_count)
        self.layout.addRow('rows', self.axrownum_field)

        self.ax_pos_layout = QtGui.QVBoxLayout()
        self.ax_pos_layout.setContentsMargins(10, 0, 0, 0)
        self.layout.addRow(self.ax_pos_layout)
        self.fill_ax_positions()

        self.style_dd = bw.Dropdown(plt.style.available, default_index=plt.style.available.index('ggplot'))
        self.style_dd.value_changed.connect(self.set_style)
        self.layout.addRow('style', self.style_dd)

    def fill_ax_positions(self):
        self.axfields = []
        current_axes = self.figure_manager.gca()
        for i, a in enumerate(self.figure_manager.axes):
            fs = AxPosField(i, a.position, selected=a is current_axes)
            self.axfields.append(fs)
            fs.toggled.connect(partial(self.set_current_axes, i))
            fs.value_changed.connect(partial(self.edit_axes, i))
            self.ax_pos_layout.addWidget(fs)

    def set_current_axes(self, i):
        prev = self.figure_manager.gca()
        if self.axfields[i].is_selected():
            self.figure_manager.current_index = i

        current_index = self.figure_manager.current_index
        for i, f in enumerate(self.axfields):
            if i == current_index:
                f.set_selected(True)
            else:
                f.set_selected(False)

        new = self.figure_manager.gca()
        self.current_axes_changed.emit((prev, new))

    def edit_axes(self, i, pos):
        w, h = pos[2:]
        if w == 0 or h == 0:
            return
        self.figure_manager.axes[i].set_position(pos)
        self.reload_ax_positions()
        self.changed.emit()

    def set_ax_count(self, v):
        if v is None:
            return

        elif v < 1:
            QtGui.QMessageBox.warning(self, 'invalid number of axes', 'at least 1 axes required')
            return

        elif v > 20:
            QtGui.QMessageBox.warning(self, 'invalid number of axes', 'number of axes larger than 20 not allowed')
            return

        self.figure_manager.set_ax_count(v)
        self.reload_ax_positions()
        self.changed.emit()

    def set_axrow_count(self, v):
        if v is None:
            return

        elif v < 1:
            QtGui.QMessageBox.warning(self, 'invalid number of rows', 'at least 1 row required')
            return
        elif v > 10:
            QtGui.QMessageBox.warning(self, 'invalid number of rows', 'number of rows larger than 10 not allowed')
            return

        self.figure_manager.set_axrow_count(v)
        self.reload_ax_positions()
        self.changed.emit()

    def set_style(self, s):
        self.figure_manager.set_style(s)
        self.changed.emit()

    def reload_ax_positions(self):
        clear_layout(self.ax_pos_layout)
        self.fill_ax_positions()


class AxesSettings(SettingsWidget):

    changed = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def get_defaults(self):
        return dict(title=self.ax.get_title(),
                    xlabel=self.ax.get_xlabel(),
                    ylabel=self.ax.get_ylabel(),
                    xlim=tuple(self.ax.get_xlim()),
                    ylim=tuple(self.ax.get_ylim()),
                    aspect=None)

    def build(self):
        self.fields = OrderedDict()
        self.layout = QtGui.QFormLayout(self)
        defaults = self.get_defaults()
        self.fields['title'] = bw.Text(defaults['title'])
        self.fields['xlabel'] = bw.Text(defaults['xlabel'])
        self.fields['ylabel'] = bw.Text(defaults['ylabel'])
        self.fields['xlim'] = bw.MinMax(defaults['xlim'])
        self.fields['ylim'] = bw.MinMax(defaults['ylim'])
        for k, v in self.fields.items():
            v.value_changed.connect(self.change)
            self.layout.addRow(k, v)
        self.aspect_field = bw.Checkbox(defaults['aspect'] == 'equal')
        self.aspect_field.value_changed.connect(self.change)
        self.layout.addRow('aspect equal', self.aspect_field)

    def change(self, *args):
        self.changed.emit(self.kwargs)

    @property
    def kwargs(self):
        data = {k: v.value() for k, v in self.fields.items()}
        if self.aspect_field.value():
            data['aspect'] = 'equal'
        return data

    def set_kwargs(self, reset=False, **kwargs):
        kwargs = ChainMap(kwargs, self.get_defaults())
        for k, v in kwargs.items():
            if k in self.fields:
                self.fields[k].set_value(v)
            if k == 'aspect':
                self.aspect_field.set_value(v == 'equal')

    @property
    def ax(self):
        return plt.gca()


class PlotSettings(SettingsWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def build(self):
        pass


class LegendSettings(SettingsWidget):

    pass


class ColorbarSettings(SettingsWidget):

    pass


class AxPosField(QtGui.QWidget):

    value_changed = QtCore.pyqtSignal(object)
    toggled = QtCore.pyqtSignal(bool)

    def __init__(self, i, pos, selected=False):
        super().__init__()

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)

        self.label = bw.ToggleLabel(str(i), selected=selected)
        self.label.setFixedWidth(30)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.label.toggled.connect(self.toggled)
        self.layout.addWidget(self.label)

        self.fields = bw.Fieldset(bw.Float, val=pos, fmt='{:.2f}', field_width=40, onchange=False)
        self.fields.value_changed.connect(self.value_changed.emit)
        self.layout.addWidget(self.fields)

    def set_selected(self, b):
        self.label.set_selected(b)

    def is_selected(self):
        return self.label.selected
