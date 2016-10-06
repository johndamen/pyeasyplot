import numpy as np
from collections import ChainMap
from matplotlib import cm


class InvalidAxes(Exception):
    """
    Exception raised when an invalid data array is given for a dataset as an axis
    """


class Dataset(object):
    """
    object for handling a set of numpy arrays that together form a dataset
    """

    # a tuple specifying the number of dimensions for each subsequent array of the dataset
    DIMENSIONS = ()

    # default arguments for plotting; may be used by other libraries to retrieve sensible  defaults
    PLOT_DEFAULTS = dict()

    # settings that specify how the limit (min, max) of an axis is determined (see also dataset._limits)
    LIMIT_SETTINGS = dict()

    # names of the axes if not specified explicitly
    DEFAULT_NAMES = ()

    def __init__(self, *args, names=None):
        # store the axes as a list of numpy arrays
        axes = []
        for a in args:
            if not isinstance(a, np.ndarray):
                a = np.array(a)
            axes.append(a)

        # check the axes against this dataset type
        self.check_axes(axes)

        self.axes = axes
        self.names = names or self.DEFAULT_NAMES


    def plot(self, **kwargs):
        """plot the data"""
        kwargs = ChainMap(kwargs, self.PLOT_DEFAULTS)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.axes[i]
        elif isinstance(item, str):
            try:
                i = self.names.index(item)
            except IndexError:
                raise KeyError(item)
            return self.axes[i]
        else:
            raise TypeError('unknown type for indexing')

    def limits(self, **kwargs):
        """calculate the limits of a dataset"""
        return self._limits(**ChainMap(kwargs, self.LIMIT_SETTINGS))

    def _limits(self, xunit=None, yunit=None, xmargin=None, ymargin=None):
        """
        calculate the limits from the given configuration arguments
        :param xunit: if set to auto, a sensible xmin and xmax are chosen from the data
        :param yunit: if set to auto, a sensible xmin and xmax are chosen from the data
        :param xmargin: margin at left and right of the data to prevent values on the edge of the figure axes
                        overruled by xunit=auto
        :param ymargin: margin at top and bottom of the data to prevent values on the edge of the figure axes
                        overruled by yunit=auto
        :return: (np.array([xmin, xmax]), np.array([ymin, ymax])
        """
        x, y = self.axes[0], self.axes[1]
        xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()

        if xunit is not None:
            if xunit == 'auto':
                # get largest decimal as unit
                # this is based on one third of the span along x
                xunit = self.largest_decimal((xmax - xmin)*.3)
                # move data away from edges
                xmargin = 0.5*xunit

            # round the limits to a unit
            xmin, xmax = self._round_limits(xmin, xmax, xunit, margin=xmargin or 0)

        if yunit is not None:
            if yunit == 'auto':
                # get largest decimal as unit
                # this is based on one third of the span along y
                yunit = self.largest_decimal((ymax - ymin)*.3)
                # move data away from edges
                ymargin = 0.5*yunit

            # round the limits to a unit
            ymin, ymax = self._round_limits(ymin, ymax, yunit, margin=ymargin or 0)

        return np.array([xmin, xmax]), np.array([ymin, ymax])

    def largest_decimal(self, v):
        """
        calculate the largest decimal number in the value
        1.4    -> 1
        0.351  -> 0.1
        0.0023 -> 0.001
        """
        return 10**np.floor(np.log10(v))

    def _round_limits(self, vmin, vmax, target, margin=0):
        """
        round limit values to a nearest unit including a possible margin
        :param vmin: lower limit
        :param vmax: upper limit
        :param target: unit to round to (floor for lower, ceil for upper)
        :param margin: values are increased/decreased by the margin
        :return: new x and y limits
        """
        vmin = vmin - margin
        vmax = vmax + margin
        return np.floor(vmin/target) * target, np.ceil(vmax/target) * target

    @classmethod
    def is_valid(cls, axes):
        try:
            cls.check_axes(axes)
            return True
        except InvalidAxes:
            return False

    @classmethod
    def check_axes(cls, axes):
        """
        check all specified axes to be valid
         - compare axes to dataset.DIMENSIONS
         - check if all axes are numpy arrays
        """
        if len(axes) != len(cls.DIMENSIONS):
            raise InvalidAxes('{} axes required for {}'.format(len(cls.DIMENSIONS), cls.__name__))

        for i, a in enumerate(axes):
            if not isinstance(a, np.ndarray):
                raise InvalidAxes('axes {} not a numpy.ndarray'.format(i))
            if a.ndim != cls.DIMENSIONS[i]:
                raise InvalidAxes('axes {} does not have {} dimensions'.format(i, cls.DIMENSIONS[i]))

    @classmethod
    def likelihood(cls, axes):
        """
        returns a float between 0 and 1 which indicates likelihood of a dataset being of this dataset type
        for each condition, the value is increased or decreased from .5 depending on the outcome
        :param axes: list of axes (ndarray) for the dataset
        :return: float between 0 and 1
        """
        return .5

    @staticmethod
    def is_equidistant(v, margin=1e-5):
        return v.ndim == 1 and (v.min() - np.diff(v) < margin).all()

    @staticmethod
    def is_increasing(v):
        return v.ndim == 1 and (np.diff(v) > 0).all()

    def __iter__(self):
        for i, a in enumerate(self.axes):
            yield self.names[i], a


class Timeseries(Dataset):

    DIMENSIONS = (1, 1)
    LIMIT_SETTINGS = dict(yunit='auto')
    PLOT_DEFAULTS = dict()
    DEFAULT_NAMES = ('t', 'v')
    LAYER_NAME = 'timeseries.plot'

    def plot(self, ax, **kwargs):
        return ax.plot(self.axes[0], self.axes[1], **ChainMap(kwargs, self.PLOT_DEFAULTS))

    @classmethod
    def is_valid(cls, axes):
        if not super().is_valid(axes):
            return False

        if axes[0].shape != axes[1].shape:
            return False

        return True

    @classmethod
    def likelihood(cls, axes):
        if cls.is_increasing(axes[0]):
            return .75
        return .25


class Points(Dataset):

    DIMENSIONS = (1, 1)
    LIMIT_SETTINGS = dict(xunit='auto', yunit='auto')
    PLOT_DEFAULTS = dict(color='k', alpha=1., s=20)
    DEFAULT_NAMES = ('x', 'y')
    LAYER_NAME = 'points.scatter'

    def plot(self, ax, **kwargs):
        return ax.scatter(self.axes[0], self.axes[1], **ChainMap(kwargs, self.PLOT_DEFAULTS))

    @classmethod
    def is_valid(cls, axes):
        if not super().is_valid(axes):
            return False

        if axes[0].shape != axes[1].shape:
            return False

        return True


class ValuePoints(Dataset):

    DIMENSIONS = (1, 1, 1)
    LIMIT_SETTINGS = dict(xunit='auto', yunit='auto')
    PLOT_DEFAULTS = dict(cmap=cm.inferno, lw=0, alpha=1., s=20)
    DEFAULT_NAMES = ('x', 'y', 'z')
    LAYER_NAME = 'valuepoints.scatter'

    def plot(self, ax, valuetype='c', **kwargs):
        kwargs[valuetype] = self.axes[2]
        return ax.scatter(self.axes[0], self.axes[1], **ChainMap(kwargs, self.PLOT_DEFAULTS))

    @classmethod
    def is_valid(cls, axes):
        if not super().is_valid(axes):
            return False
        s = axes[0].shape
        if axes[1].shape != s:
            return False
        if axes[2].shape != s:
            return False
        return True


class Grid(Dataset):

    DIMENSIONS = (1, 1, 2)
    LIMIT_SETTINGS = dict()
    PLOT_DEFAULTS = dict(cmap=cm.viridis)
    DEFAULT_NAMES = ('x', 'y', 'z')
    LAYER_NAME = 'grid.pcolormesh'

    def plot(self, ax, **kwargs):
        return ax.pcolormesh(self.axes[0], self.axes[1], self.axes[2], **ChainMap(kwargs, self.PLOT_DEFAULTS))

    @classmethod
    def is_valid(cls, axes):
        if not super().is_valid(axes):
            return False
        if axes[2].shape != (axes[1].size, axes[0].size):
            return False
        return True

    @classmethod
    def likelihood(cls, axes):
        if cls.is_equidistant(axes[0]) and cls.is_equidistant(axes[1]):
            return .75
        else:
            return .25


class IrregularGrid(Dataset):

    DIMENSIONS = (2, 2, 2)
    LIMIT_SETTINGS = dict(xunit='auto', yunit='auto')
    PLOT_DEFAULTS = dict(cmap=cm.viridis)
    DEFAULT_NAMES = ('x', 'y', 'z')
    LAYER_NAME = 'irregulargrid.pcolor'

    def plot(self, ax, **kwargs):
        return ax.pcolor(self.axes[0], self.axes[1], self.axes[2], **ChainMap(kwargs, self.PLOT_DEFAULTS))

    @classmethod
    def is_valid(cls, axes):
        if not super().is_valid(axes):
            return False
        s = axes[0].shape
        if axes[1].shape != s or axes[2].shape != s:
            return False
        return True


class VectorData(Dataset):

    DIMENSIONS = (1, 1, 2, 2)
    LIMIT_SETTINGS = dict(xunit='auto', yunit='auto')
    PLOT_DEFAULTS = dict()
    DEFAULT_NAMES = ('x', 'y', 'U', 'V')
    LAYER_NAME = 'vectordata.quiver'

    def plot(self, ax, **kwargs):
        return ax.quiver(self.axes[0], self.axes[1], self.axes[2], self.axes[3], **ChainMap(kwargs, self.PLOT_DEFAULTS))

    @classmethod
    def is_valid(cls, axes):
        if not super().is_valid(axes):
            return False
        if axes[2].shape != (axes[1].size, axes[0].size):
            return False
        if axes[3].shape != (axes[1].size, axes[0].size):
            return False
        return True

    @classmethod
    def likelihood(cls, axes):
        if cls.is_equidistant(axes[0]) and cls.is_equidistant(axes[1]):
            return .75
        else:
            return .25


DATATYPES = []
for v in dict(locals()).values():
    if isinstance(v, type) and issubclass(v, Dataset) and v is not Dataset:
        DATATYPES.append(v)


def interpret_datatype(*datavars, **kwargs):
    axes = []
    for d in datavars:
        if not isinstance(d, np.ndarray):
            d = np.array(d)
        axes.append(d)

    options = []
    for d in DATATYPES:
        if d.is_valid(axes):
            options.append(d)

    options = sorted(options, key=lambda x: x.likelihood(axes))
    return options[-1](*axes, **kwargs)

