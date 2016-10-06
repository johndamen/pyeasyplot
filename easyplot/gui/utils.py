from PyQt4 import QtGui


def clear_layout(l):
    while l.count():
        item = l.takeAt(0)
        if isinstance(item, QtGui.QWidgetItem):
            item.widget().deleteLater()
        elif isinstance(item, QtGui.QSpacerItem):
            pass
        else:
            clear_layout(item.layout())
        l.removeItem(item)


def delete_layout(l, parent):
    clear_layout(l)
    parent.removeItem(l)