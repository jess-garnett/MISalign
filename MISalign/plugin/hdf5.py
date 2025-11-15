"""Plugin module that implements support for storing an entire project in a single hdf5."""

from MISalign.model.project import MISProject
from MISalign.model.relation import MISRelation
from MISalign.model.image import MISImage


class MISProjectHDF5(MISProject):
    """Access image data and information from a HDF5."""


class MISImageHDF5(MISImage):
    """Access image data and information from a HDF5."""