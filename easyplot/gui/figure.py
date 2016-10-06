from matplotlib.backends.backend_qt4agg import FigureCanvas


class Canvas(FigureCanvas):

    def __init__(self, fig):
        super().__init__(fig)