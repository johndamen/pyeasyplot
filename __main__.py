import sys

argv = sys.argv[1:]
if argv and argv[0] == 'test':
    from . import tests
    tests.run()
else:
    from PyQt4 import QtGui
    from . import gui
    import sys

    from .datasets import interpret_datatype
    import numpy as np

    app = QtGui.QApplication([])

    dataset = interpret_datatype(np.arange(10), np.arange(10), np.random.rand(10, 10), np.random.rand(10, 10))
    w = gui.EasyPlotWidget(dataset)
    w.show()

    exit_code = app.exec_()

    w.deleteLater()

    sys.exit(exit_code)