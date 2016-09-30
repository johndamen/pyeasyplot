from PyQt4 import QtGui, QtCore
from collections import OrderedDict
import numpy as np
import re
from matplotlib import colors, cm


class InvalidColorError(Exception): pass


class SettingWidget(QtGui.QWidget):

    value_changed = QtCore.pyqtSignal(object)

    def __init__(self, val=None, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.build(**kwargs)
        if val is not None:
            self.set_value(val)

    def build(self, **kwargs):
        pass

    def value(self):
        pass

    def set_value(self, v):
        pass

    def is_empty(self):
        pass

    def changed(self, *args):
        self.value_changed.emit(self.value())


class Fieldset(SettingWidget):

    def __init__(self, ftype, val=(), parent=None, field_width=None, **fkwargs):
        self.ftype = ftype
        self.fkwargs = fkwargs
        val = tuple(val)
        self.fieldcount = len(val)
        super().__init__(val=val, parent=parent, field_width=field_width)

    def build(self, field_width=None):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)

        self.fields = []
        for i in range(self.fieldcount):
            field = self.ftype(val=None, **self.fkwargs)
            if field_width is not None:
                field.setFixedWidth(field_width)
            self.fields.append(field)
            field.value_changed.connect(self.changed)
            self.layout.addWidget(field)

    def value(self):
        return tuple(f.value() for f in self.fields)

    def set_value(self, v):
        if len(v) != self.fieldcount:
            raise ValueError('invalid value for fieldset of length {}'.format(self.fieldcount))
        for i, f in enumerate(self.fields):
            f.set_value(v[i])

    def __getitem__(self, item):
        return self.fields[item]


class Text(SettingWidget):

    def __init__(self, val, fmt='{}', parent=None, **kwargs):
        self.fmt = fmt
        super().__init__(val, parent=parent, **kwargs)

    def build(self, onchange=False):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.textfield = QtGui.QLineEdit()
        if onchange:
            self.textfield.textChanged.connect(self.changed)
        else:
            self.textfield.editingFinished.connect(self.changed)
        self.layout.addWidget(self.textfield)

    def value(self):
        return str(self.textfield.text())

    def set_value(self, v, ifempty=False):
        if ifempty and not self.is_empty():
            return
        self.textfield.setText(self._format_value(v))

    def is_empty(self):
        return str(self.textfield.text()) == ''

    def _format_value(self, v):
        return self.fmt.format(v)


class TextOrNone(Text):

    def value(self):
        s = str(self.textfield.text())
        if s == '':
            return None
        return self._cast(s)

    def _cast(self, v):
        return str(v)


class Int(TextOrNone):

    def _cast(self, v):
        return int(v)


class Float(TextOrNone):

    def _cast(self, v):
        return float(v)


class MinMax(SettingWidget):

    def __init__(self, v, fmt='{}', vtype=None, parent=None):
        vmin, vmax = v
        self.vmin = vmin
        self.vmax = vmax
        self.fmt = fmt
        self.vtype = vtype or vmin.__class__
        super().__init__(parent=parent)

    def build(self):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        vmin_str = self.fmt.format(self.vmin) if self.vmin is not None else ''
        self.vmin_field = QtGui.QLineEdit(vmin_str)
        self.vmin_field.editingFinished.connect(self.changed)
        self.layout.addWidget(self.vmin_field)

        vmax_str = self.fmt.format(self.vmax) if self.vmax is not None else ''
        self.vmax_field = QtGui.QLineEdit(vmax_str)
        self.vmax_field.editingFinished.connect(self.changed)
        self.layout.addWidget(self.vmax_field)

    def value(self):
        smin = str(self.vmin_field.text())
        vmin = self.vtype(smin) if smin else None
        smax = str(self.vmax_field.text())
        vmax = self.vtype(smax) if smax else None
        return vmin, vmax

    def setValue(self, v, ifempty=False):
        vmin, vmax = tuple(v)
        if not ifempty or str(self.vmin_field.text()) == '':
            self.vmin_field.setText(str(vmin))

        if not ifempty or str(self.vmax_field.text()) == '':
            self.vmax_field.setText(str(vmax))

    def isempty(self):
        return str(self.vmin_field.text()) == '' and str(self.vmax_field.text()) == ''


class ListedSlider(SettingWidget):

    def __init__(self, values, default=None, fmt='{:.2f}', parent=None):
        self.values = values
        if default is None:
            default = self.values.size // 2
        self.i = int(default)
        self.fmt = fmt
        super().__init__(parent=parent)

    def build(self):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.slider = QtGui.QSlider()
        self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.values.size-1)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        self.slider.setSliderPosition(self.i)
        self.slider.valueChanged.connect(self.changed)
        self.slider.setFixedWidth(100)

        self.layout.addWidget(self.slider)

        self.label = QtGui.QLabel(self.format_value())
        self.label.setFixedWidth(60)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.label)

    def changed(self, *args):
        self.set_from_slider(*args)
        super().changed(*args)

    def slider2value(self, v):
        return self.vmin + v * self.step

    def value2slider(self, v):
        return np.floor(1e-5+(v - self.vmin) / self.step)

    def set_from_slider(self, i):
        self.i = int(i)
        self.label.setText(self.format_value())

    def value(self):
        return self.values[self.i]

    def format_value(self):
        return self.fmt.format(self.value())


class RangeSlider(ListedSlider):

    def __init__(self, vmin, vmax, step, default=None, decimals=None, parent=None):
        values = np.arange(vmin, vmax+step, step)
        if decimals is None:
            decimals = int(max(0, np.ceil(-np.log10(step))))
        fmt = '{:.'+str(decimals)+'f}'
        super().__init__(values, default=default, fmt=fmt, parent=parent)


class Dropdown(SettingWidget):

    def __init__(self, opts, default_index=0, parent=None):
        if isinstance(opts, list):
            if opts and isinstance(opts[0], str):
                opts = [(o, o) for o in opts]
            opts = OrderedDict(opts)
        elif not isinstance(opts, OrderedDict):
            raise TypeError('invalid options')
        self.opts = opts
        self.default_index = default_index
        super().__init__(parent=parent)

    def build(self):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.dd = QtGui.QComboBox()
        self.dd.addItem('default')
        self.dd.addItems(list(self.opts.keys()))
        self.dd.setCurrentIndex(self.default_index)
        self.dd.currentIndexChanged.connect(self.changed)

        self.layout.addWidget(self.dd)

    def value(self):
        i = self.dd.currentIndex()
        if i == 0:
            return None
        else:
            return list(self.opts.values())[i-1]


class Color(SettingWidget):

    def __init__(self, color=None, **kwargs):
        self.colortuple_patterns = [
            (self.parse_int, re.compile(r'^\(?([0-9]+),\s*([0-9]+),\s*([0-9]+)\)?\s*$')),
            (self.parse_float, re.compile(r'^\(?([0-9\.]+),\s*([0-9\.]+),\s*([0-9\.]+)\)?\s*$'))]
        self.color = color
        super().__init__(**kwargs)

    def scale_colorvalue(self, v):
        scaled_v = float(v)/255
        return max(min(scaled_v, 1), 0)

    def build(self):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.textfield = QtGui.QLineEdit(self.format_color(self.color))
        self.textfield.editingFinished.connect(self.changed)
        self.textfield.setFixedWidth(120)
        self.layout.addWidget(self.textfield)

        self.pick_button = QtGui.QPushButton('...')
        self.pick_button.clicked.connect(self.pick)
        self.layout.addWidget(self.pick_button)

    def parse_int(self, v):
        scaled_v = float(v)/255
        return self.parse_float(scaled_v)

    def parse_float(self, v):
        v = float(v)

        if v > 1 or v < 0:
            raise ValueError(str(v))

        return v

    def parse_color_tuple(self, t):
        if len(t) != 3:
            raise InvalidColorError(str(t))

        if all(isinstance(v, int) for v in t):
            val_parser = self.parse_int
        elif all(isinstance(v, float) for v in t):
            val_parser = self.parse_float
        else:
            raise InvalidColorError(str(t))

        return tuple(val_parser(v) for v in t)

    def parse_color_str(self, s):
        for t, p in self.colortuple_patterns:
            m = p.match(s)
            if not m:
                continue
            try:
                return tuple(t(item) for item in m.groups())
            except ValueError:
                raise InvalidColorError(s)
        if colors.is_color_like(s):
            return s
        else:
            raise InvalidColorError(s)

    def parse_color(self, v):
        if v is None:
            return v
        try:
            if isinstance(v, str):
                return self.parse_color_str(v)
            elif isinstance(v, tuple):
                return self.parse_color_tuple(v)
        except InvalidColorError as e:
            QtGui.QMessageBox.warning(self, 'invalid color', 'invalid color value: {}'.format(e))
            self.textfield.setText(self.format_color(self.color))

    def format_color(self, c):
        if c is None:
            return ''
        if isinstance(c, tuple) and len(c) == 3:
            if all(isinstance(v, float) for v in c):
                return '({:.2f}, {:.2f}, {:.2f})'.format(*c)
            else:
                return '({}, {}, {})'.format(*c)
        return str(c)

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, v):
        self._color = self.parse_color(v)

    def pick(self):
        color = QtGui.QColorDialog.getColor()
        rgb = (self.scale_colorvalue(color.red()),
               self.scale_colorvalue(color.green()),
               self.scale_colorvalue(color.blue()))
        self.color = rgb
        self.textfield.setText(self.format_color(rgb))
        self.changed()

    def value(self):
        s = str(self.textfield.text())
        if s == '':
            return None
        else:
            self.color = s
            return self.color


class Colormap(Dropdown):

    def __init__(self, default, parent=None):
        opts = OrderedDict(self.list_colormaps())
        if isinstance(default, str):
            default_cmap = cm.get_cmap(default)
        elif isinstance(default, colors.Colormap):
            default, default_cmap = default.name, default
        opts[default] = default_cmap
        default_index = list(opts.keys()).index(default)
        super().__init__(opts, default_index=default_index, parent=parent)

    @classmethod
    def list_colormaps(cls):
        return [(name, c) for name, c in cm.__dict__.items() if isinstance(c, colors.Colormap)]


class Checkbox(SettingWidget):

    def __init__(self, checked):
        super().__init__(checked)

    def build(self):
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.cb = QtGui.QCheckBox()
        self.cb.setChecked(False)
        self.cb.toggled.connect(self.changed)
        self.layout.addWidget(self.cb)

    def set_value(self, b):
        self.cb.setChecked(bool(b))

    def value(self):
        return self.cb.isChecked()


class ClickableLabel(QtGui.QLabel):

    clicked = QtCore.pyqtSignal()

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()


class ToggleLabel(ClickableLabel):

    toggled = QtCore.pyqtSignal(bool)

    def __init__(self, *args, selected=False, toggle_internal=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_selected(selected)
        self.toggle_internal = toggle_internal
        self.clicked.connect(self.toggle)

    def toggle(self):
        print('toggled', self)
        if self.toggle_internal:
            self.set_selected(not self.selected)
            self.toggled.emit(self.selected)

    def set_selected(self, b):
        self.selected = b
        if b:
            self.setStyleSheet('''text-decoration: underline''')
        else:
            self.setStyleSheet('''''')