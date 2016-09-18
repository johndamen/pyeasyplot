from matplotlib import pyplot as plt, figure
import numpy as np


class FigureManager(object):

    def __init__(self, fig):
        self.fig = fig
        self.fig.clear()
        self.ax = fig.gca()
        self.ax_settings = dict()

    def points2pos(self, pnt):
        x1, y1, x2, y2 = tuple(pnt.flatten())
        return [x1, y1, x2-x1, y2-y1]

    def ax_count(self):
        return len(self.get_axes())

    def set_ax_count(self, val):
        self.fig.clear()
        for i in range(val):
            self.fig.add_subplot(1, val, i+1)

    def edit_axes(self, i, pos):
        self.get_axes()[i].set_position(pos)

    def get_axes(self):
        return self.fig.get_axes()

    def get_axpositions(self):
        return [self.points2pos(a._position._points) for a in self.get_axes()]

    def format_axes(self, i, reset=False, **settings):
        if i not in self.ax_settings:
            self.ax_settings[i] = dict()
        if reset:
            self.ax_settings[i] = settings
        else:
            self.ax_settings[i].update(settings)
            settings = self.ax_settings[i]

        axes = self.get_axes()

        for k, v in settings.items():
            setter = getattr(axes[i], 'set_{}'.format(k))
            setter(v)

    def set_style(self, s):
        positions = self.get_axpositions()
        self.fig.clear()
        plt.style.use(s)
        for p in positions:
            self.fig.add_axes(p)
        for i, settings in self.ax_settings.items():
            self.format_axes(i, reset=True, **settings)


if __name__ == '__main__':
    fig = plt.figure()
    figman = FigureManager(fig)
    figman.format_axes(0, xlim=(0, 10), ylim=(5, 6), yticks=np.linspace(5, 6, 6), ylabel='y', xlabel='x', xticks=np.arange(0, 11, 2), title='test')
    figman.set_style('ggplot')
    plt.show()
