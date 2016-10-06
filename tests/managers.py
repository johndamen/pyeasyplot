import unittest
from easyplot import datasets, managers
from matplotlib import pyplot as plt
import numpy as np


def create_grid_dataset():
    x = np.linspace(0, 1, 100)
    y = np.linspace(0, 1, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X)+np.cos(Y)+.2*np.random.rand(100, 100)
    return datasets.Grid(x, y, Z)


def create_timeseries_dataset():
    t = np.linspace(0, 1, 100)
    v = np.random.rand(100)**2
    return datasets.Timeseries(t, v)


class TestLayerContainer(unittest.TestCase):

    def setUp(self):
        self.fig = plt.figure()
        self.ax = self.fig.gca()

    def create_container(self):
        items = [create_grid_dataset(), create_timeseries_dataset()]
        self.container = managers.LayersContainer(*items)
        self.assertEqual(len(self.container), 2)
        self.assertEqual(items[0], self.container[0]['data'])
        self.assertEqual(items[1], self.container[1]['data'])
        self.assertNotEqual(self.container[0], self.container[1])
        self.assertEqual(list(self.container), [
            dict(data=items[0], kwargs=datasets.Grid.PLOT_DEFAULTS),
            dict(data=items[1], kwargs=datasets.Timeseries.PLOT_DEFAULTS)])

    def testCreate(self):
        c = managers.LayersContainer()
        self.assertIsInstance(c, list)
        self.assertEqual(len(c), 0)
        d = create_grid_dataset()
        c.add(d, vmax=2)
        self.assertEqual(list(c), [dict(data=d, kwargs=dict(vmax=2, cmap=datasets.Grid.PLOT_DEFAULTS['cmap']))])
        c.edit(0, cmap='jet', vmin=-2)
        self.assertEqual(list(c), [dict(data=d, kwargs=dict(cmap='jet', vmax=2, vmin=-2))])

    def testCreateWithItems(self):
        d1, d2 = create_grid_dataset(), create_timeseries_dataset()
        c = managers.LayersContainer(d1, dict(data=d2, kwargs=dict(color='k')))
        self.assertEqual(len(c), 2)
        self.assertEqual(list(c), [dict(data=d1, kwargs=datasets.Grid.PLOT_DEFAULTS),
                                   dict(data=d2, kwargs={**datasets.Timeseries.PLOT_DEFAULTS, 'color': 'k'})])

    def testEdit(self):
        self.create_container()

        items = list(self.container)
        kw = items[1]['kwargs']
        self.container.edit(1, lw=2)
        kw['lw'] = 2
        self.assertEqual(self.container[1], dict(data=items[1]['data'], kwargs=kw))

    def testDelete(self):
        self.create_container()

        items = list(self.container)
        self.container.delete(0)
        self.assertNotIn(items[0], list(self.container))
        self.assertEqual([items[1]], list(self.container))

    def testOrder(self):
        self.create_container()
        old_items = list(self.container)
        self.container.order([1, 0])
        items = list(self.container)
        self.assertEqual(items, [old_items[1], old_items[0]])
        with self.assertRaises(IndexError):
            self.container.order([2, 0])
        with self.assertRaises(IndexError):
            self.container.order([0, -1])
        with self.assertRaises(IndexError):
            self.container.order([0, 0, 1])
        with self.assertRaises(IndexError):
            self.container.order([0, 1, 2])


    def tearDown(self):
        plt.close(self.fig)


class TestAxesManager(unittest.TestCase):

    def setUp(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_axes([0, 0, 1, 1])

    def create_axmanager(self):
        self.m = managers.AxesManager(self.ax)
        self.assertIs(self.m.ax, self.ax)

    def testCreate(self):
        m = managers.AxesManager(self.ax)
        self.assertIs(m.ax, self.ax)
        self.assertIsInstance(m.layers, managers.LayersContainer)

    def testFormat(self):
        self.create_axmanager()
        self.m.format(xlabel='x', ylabel='y')
        self.assertEqual(self.ax.get_xlabel(), 'x')
        self.assertEqual(self.ax.get_ylabel(), 'y')

        self.assertEqual(self.m.position, [0, 0, 1, 1])

        self.m.set_position(.1, .1, .8, .8)
        self.assertEqual(self.m.position, [.1, .1, .8, .8])


class TestFigManager(unittest.TestCase):

    def setUp(self):
        self.fig = plt.figure()

    def testCreate(self):
        m = managers.FigureManager(self.fig)
        self.assertIs(m.fig, self.fig)
        self.assertEqual(m.current_index, 0)
        self.assertEqual(len(m.axes), 1)
        self.assertIsInstance(m.gca(), managers.AxesManager)
        for a in m.axes:
            self.assertIsInstance(a, managers.AxesManager)