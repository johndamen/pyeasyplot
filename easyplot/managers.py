from matplotlib import pyplot as plt, axes
import numpy as np
from math import ceil
from collections import ChainMap
from . import datasets


class FigureManager(object):
    """
    object to simplify editing figure settings
    """

    def __init__(self, fig):
        self.fig = fig
        self.fig.clear()
        self.axes = [AxesManager(fig.add_subplot(111))]
        self._current_index = 0
        self._axrow_count = 1

    @property
    def current_index(self):
        if self._current_index >= len(self.axes):
            self._current_index = 0
        return self._current_index
    @current_index.setter
    def current_index(self, val):
        self._current_index = val

    def clear_figure(self):
        self.fig.clear()

    def ax_count(self):
        return len(self.axes)

    def axrow_count(self):
        return self._axrow_count

    def set_ax_count(self, val, reset=True):
        if not reset:
            data = [(a.layers, a.settings) for a in self.axes]
            data += [(None, dict())]*(val - len(self.axes))
        else:
            data = [(None, dict())]*val

        self.axes = []
        self.fig.clear()
        for i in range(val):
            ax = self.fig.add_subplot(self.axrow_count(), ceil(val/self.axrow_count()), i+1)
            layers, settings = data[i]
            axman = AxesManager(ax, layers=layers, **settings)
            self.axes.append(axman)

    def set_axrow_count(self, i, reset=True):
        self._axrow_count = i
        self.set_ax_count(self.ax_count(), reset=reset)

    def ax2index(self, ax):
        if isinstance(ax, AxesManager):
            ax = ax.ax

        for i, a in enumerate(self.axes):
            if a.ax is ax:
                return i

        raise ValueError('could not identify axes')

    def format_axes(self, i, reset=False, **settings):
        """
        apply settings to axes object
        :param i: index of the axes or axes instance
        :param reset: update existing settings or reset all to defaults
        :param settings: settings to apply
        """
        if not isinstance(i, int):
            i = self.ax2index(i)

        self.axes[i].format(**settings)

    def set_style(self, s):
        """
        apply style and recreate axes
        :param s: style name from plt.style.available
        """
        old_data = [(a.position, a.layers, a.settings) for a in self.axes]
        print(old_data)
        self.fig.clear()
        self.axes = []
        plt.style.use(s)
        for p, l, s in old_data:
            self.axes.append(AxesManager(self.fig.add_axes(p), layers=l, **s))

    def draw(self):
        self.fig.canvas.draw()

    def gca(self):
        return self.axes[self.current_index]


class AxesManager(object):

    def __init__(self, ax, layers=None, **settings):
        if not isinstance(ax, axes.Axes):
            raise TypeError('first argument not an instance of matplotlib.axes.Axes')
        self.ax = ax

        self.settings = dict()
        self.format(**settings)

        self.layers = layers or LayersContainer()

    def set_position(self, *args):
        if len(args) == 1:
            pos, = args
        else:
            x, y, w, h = args
            pos = [x, y, w, h]
        self.ax.set_position(pos)

    @property
    def position(self):
        x1, y1, x2, y2 = tuple(self.ax._position._points.flatten())
        return [x1, y1, x2 - x1, y2 - y1]

    def format(self, reset=False, **settings):
        if reset:
            self.settings = settings
        else:
            self.settings.update(settings)
        self.apply_settings()

    def check_limits(self, xlim, ylim):
        self._check_limit('xlim', *xlim)
        self._check_limit('ylim', *ylim)
        self.apply_settings()

    def _check_limit(self, name, vmin, vmax):
        try:
            vmin_old, vmax_old = self.settings[name]
        except KeyError:
            self.settings[name] = np.array([vmin, vmax])
        else:
            self.settings[name] = np.array([min(vmin_old, vmin), max(vmax_old, vmax)])

    def apply_settings(self):
        for k, v in self.settings.items():
            try:
                setter = getattr(self.ax, 'set_{}'.format(k))
            except AttributeError:
                raise AttributeError('{} not a valid axes setting'.format(k))
            else:
                setter(v)

    def plot(self):
        self.ax.clear()
        self.apply_settings()
        self.ax.hold(True)
        self.ax.set_prop_cycle(None)
        self.layers.plot(self.ax)
        self.ax.hold(False)

    def __str__(self):
        return '<{}.{} [{:.2f}, {:.2f}, {:.2f}, {:.2f}]>'.format(__name__, self.__class__.__name__, *self.position)


class LayersContainer(list):

    def __init__(self, *layers):
        super().__init__()
        for l in layers:
            if isinstance(l, dict):
                self.add(l['data'], **l['kwargs'])
            else:
                self.add(l)

        self._current_index = len(self) - 1

    def __str__(self):
        indent = ' '*8
        items = []
        for item in self:
            kwargstr = 'dict({})'.format(', '.join('{!s}={!r}'.format(*i) for i in item['kwargs'].items()))
            items.append('{dataset} {kwargs}'.format(
                indent=indent,
                dataset=item['data'],
                kwargs=kwargstr))
        return 'Layers([{}])'.format(('\n'+indent).join(items))

    @property
    def current_index(self):
        return self._current_index
    @current_index.setter
    def current_index(self, val):
        if not isinstance(val, int):
            raise TypeError('index must be an integer')
        if val < 0 or val >= len(self):
            raise IndexError(val)
        self._current_index = val

    def gcl(self):
        return self[self.current_index]

    def add(self, d, **kwargs):
        if not isinstance(d, datasets.Dataset):
            raise TypeError('invalid value for dataset')
        kwargs = dict(ChainMap(kwargs, d.PLOT_DEFAULTS))
        self.append(dict(data=d, kwargs=kwargs))
        self.current_index = len(self) - 1

    def edit(self, i, **kwargs):
        self[i]['kwargs'].update(kwargs)

    def edit_current(self, reset=False, **kwargs):
        if reset:
            self.gcl()['kwargs'] = kwargs
        else:
            self.gcl()['kwargs'].update(kwargs)

        print(self)

    def order(self, indices):
        if sorted(list(indices)) != list(range(len(self))):
            raise IndexError('indices not valid, all layers must be included once')
        self[:] = [self[i] for i in indices]
        self.current_index = len(self) - 1

    def delete(self, i):
        del self[i]

    def plot(self, ax):
        r = []
        for l in self:
            r.append(l['data'].plot(ax, **l['kwargs']))
        return r


if __name__ == '__main__':
    fig = plt.figure()
    figman = FigureManager(fig)
    figman.format_axes(0,
                       xlim=(0, 10),
                       ylim=(5, 6),
                       yticks=np.linspace(5, 6, 6),
                       ylabel='y',
                       xlabel='x',
                       xticks=np.arange(0, 11, 2),
                       title='test')
    figman.set_style('ggplot')
    plt.show()
