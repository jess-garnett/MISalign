"""Core module for MISalign GUI based on QT."""

import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QMainWindow
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.dockarea.Dock import Dock

class CoreModel():
    """Model for Core of MISalign QT GUI"""
    def __init__(self):
        pass


class CoreView():
    """View for Core of MISalign QT GUI"""
    def __init__(self):
        self.window:QMainWindow = QMainWindow()
        self.area:DockArea = DockArea()
        self.window.setCentralWidget(self.area)
        self.window.resize(1000,500)


        self.dock_tabs={
            "MIS File":Dock(name="MIS File"),
            "Setup":Dock(name="Setup"),
            "Alignment":Dock(name="Alignment"),
            "Render":Dock(name="Render"),
        }
        self.area.addDock(dock=self.dock_tabs["MIS File"])
        self.area.addDock(dock=self.dock_tabs["Setup"],
            position='below',relativeTo=self.dock_tabs["MIS File"])
        self.area.addDock(dock=self.dock_tabs["Alignment"],
            position='below',relativeTo=self.dock_tabs["MIS File"])
        self.area.addDock(dock=self.dock_tabs["Render"],
            position='below',relativeTo=self.dock_tabs["MIS File"])

class CorePresenter():
    """Presenter for Core of MISalign QT GUI"""
    def __init__(self,
        model:CoreModel,
        view:CoreView):

        self.core_model=model
        self.core_view=view

        self.core_view.window.show()

if __name__ == '__main__':
    app = pg.mkQApp(name="MISalign QT GUI")
    core_presenter=CorePresenter(
        model=CoreModel(),
        view=CoreView()
        )
    pg.exec()