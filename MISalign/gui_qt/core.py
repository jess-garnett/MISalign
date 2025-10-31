"""Core module for MISalign GUI based on QT."""

if __name__ == '__main__':
    from sys import path as syspath
    syspath.append(".")
from MISalign.model.mis_file import MisFile,load_mis

from pyqtgraph.Qt import QtCore

import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QMainWindow
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.parametertree import Parameter, parameterTypes, ParameterTree

class CoreModel(QtCore.QObject):
    """Model for Core of MISalign QT GUI"""
    sigMISFileChanged = QtCore.Signal(object,object) # self, value  emitted when MIS file has been changed.

    def __init__(self,misfile:MisFile=None):
        super().__init__()
        if misfile is not None:
            self.set_misfile(misfile)
        else:
            self.set_misfile(MisFile())
    def set_misfile(self,misfile:MisFile):
            self._misfile=misfile
            self.sigMISFileChanged.emit(self,misfile)
    def get_misfile(self):
            return self._misfile

class CoreView(QtCore.QObject):
    """View for Core of MISalign QT GUI"""
    def __init__(self):
        super().__init__()
        self.window:QMainWindow = QMainWindow()
        self.area:DockArea = DockArea()
        self.window.setCentralWidget(self.area)
        self.window.resize(1000,500)


        self.dock_misfile=Dock(name="MIS File")
        self.area.addDock(self.dock_misfile)
        self.tree_misfile=ParameterTree(parent=self.dock_misfile)




        self.dock_setup=Dock(name="Setup")
        self.add_tab(self.dock_setup)
        self.dock_alignment=Dock(name="Alignment")
        self.add_tab(self.dock_alignment)
        self.dock_render=Dock(name="Render")
        self.add_tab(self.dock_render)

    def add_tab(self,new_dock:Dock):
        self.area.addDock(dock=new_dock,
            position='below',relativeTo=self.dock_misfile)

class CorePresenter(QtCore.QObject):
    """Presenter for Core of MISalign QT GUI"""
    def __init__(self,
        model:CoreModel,
        view:CoreView):
        super().__init__()

        self.core_model=model
        self.core_view=view

        self.core_model.sigMISFileChanged.connect(self.change_misfile)

        self.core_view.window.show()

    def change_misfile(self,model,misfile:MisFile):
        self.core_view.tree_misfile.setParameters()
        #TODO figure out interchange between MisFile and pyqtgraph parameter tree

if __name__ == '__main__':
    app = pg.mkQApp(name="MISalign QT GUI")
    core_presenter=CorePresenter(
        model=CoreModel(),
        view=CoreView()
        )
    core_presenter.core_model.set_misfile(load_mis(r"C:\Users\drago\Documents\git_gh\MISalign\example\data\set_a\set_a2_calibrated.mis"))
    pg.exec()