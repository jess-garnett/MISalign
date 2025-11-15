from MISalign.plugin.hdf5 import MISProjectHDF5, MISImageHDF5
from MISalign.model.project import MISProject
from MISalign.model.image import MISImage

class TestMISProjectHDF5():
    def test_protocol_isinstance(self):
        assert isinstance(MISProjectHDF5,MISProject)

class TestMISImageHDF5():
    def test_protocol_isinstance(self):
        assert isinstance(MISImageHDF5,MISImage)