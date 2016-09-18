import unittest
from .. import datasets
import numpy as np


class TestInterpret(unittest.TestCase):

    def test_timeseries(self):
        self.assertIsInstance(datasets.interpret_datatype(
                np.linspace(0, 7, 100),
                np.random.rand(100, 1000).mean(axis=1)),
            datasets.Timeseries)

    def test_valuepoints(self):
        self.assertIsInstance(datasets.interpret_datatype(
                np.random.rand(100),
                np.random.rand(100),
                np.random.rand(100)),
            datasets.ValuePoints)

    def test_points(self):
        self.assertIsInstance(datasets.interpret_datatype(
                np.random.rand(100),
                np.random.rand(100)),
            datasets.Points)

    def test_grid(self):
        self.assertIsInstance(datasets.interpret_datatype(
                np.linspace(0, 1, 100),
                np.linspace(0, 1, 100),
                np.random.rand(100, 100)),
            datasets.Grid)

    def test_irrgrid(self):
        self.assertIsInstance(datasets.interpret_datatype(
                np.random.rand(10, 10),
                np.random.rand(10, 10),
                np.random.rand(10, 10)),
            datasets.IrregularGrid)