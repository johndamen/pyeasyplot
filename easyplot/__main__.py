from PyQt4 import QtGui
from . import gui
import sys

from .datasets import interpret_datatype
import numpy as np

app = QtGui.QApplication([])

w = gui.EasyPlotWidget(
    interpret_datatype(
        np.arange(10),
        5*np.random.rand(10)),
    interpret_datatype(
        np.arange(10),
        np.arange(10),
        np.random.rand(10, 10),
        np.random.rand(10, 10)))
w.show()

exit_code = app.exec_()

w.deleteLater()

sys.exit(exit_code)