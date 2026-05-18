from PIL import Image as PILImage
import numpy as np
from typing import Protocol, runtime_checkable, Any
from pathlib import Path
import h5py

@runtime_checkable
class MISImage(Protocol):
    """Access image data and information."""
    def __init__(self,**image_data)->None:
        self.name:str
    def __str__(self)->str:
        ...
    def __array__(self)->np.ndarray:
        """Get a ndarray of the image."""
        ...
    @property
    def shape(self)->tuple[int, ...]:
        """Get the size of the image."""
        ...
    def for_json(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        ...
    def find_image_path(self,mis_fp,update=True)->Path|None:
        """Find path to the image either in its original file path or in the same folder as the mis filepath."""
        ...

class MISImageFile():
    """Access image data and information for an image file.
    - Expects image_filepath:str|Path"""
    _image_type="file"
    def __init__(self,**image_data)->None:
        self.image_filepath=Path(image_data["image_filepath"])
        self.name:str=self.image_filepath.name
        self._dict:dict=image_data
    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self.shape)
    def __array__(self)->np.ndarray:
        """Get a ndarray of the image."""
        PIL_image=PILImage.open(self.image_filepath)
        array=np.asarray(PIL_image)
        self._shape:tuple[int, ...]=array.shape
        return array
    @property
    def shape(self)->tuple[int, ...]:
        """Get the size of the image."""
        try: # if image has already been opened just get the size that was stored.
            return self._shape
        except AttributeError: # if image hasn't been opened then open it and grab the size.
            self.__array__()
            return self._shape
    def for_json(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":"file",
            "image_filepath":self.image_filepath.as_posix(),
            }
    def check_image_path(self)->bool:
        """Checks if image filepath is a file."""
        return self.image_filepath.is_file()
    def find_image_path(self,mis_fp,update=True)->Path|None:
        """Find, and optionally update, image paths.
        - Checks stored location.
        - Checks mis filepath folder for matching name."""
        filepath=Path(mis_fp)
        if self.check_image_path():
            return_path=self.image_filepath
        else:
            check_path=filepath.parent.joinpath(self.name)
            if check_path.is_file():
                return_path=check_path
        if update and return_path!=Path(""):
            self.image_filepath=return_path
            return return_path
        else:
            return None

class MISImageHDF5(MISImage):
    _image_type="hdf5"
    """Access image data and information from a HDF5."""
    def __init__(self,**image_data)->None:
        self.hdf5_filepath=Path(image_data["hdf5_filepath"])
        self.name:str=image_data["image_name"]
        self.hdf5path:str=image_data["hdf5path"]
        self._dict:dict=image_data
    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self.shape)
    def __array__(self)->np.ndarray:
        """Get a nparray of the image."""
        with h5py.File(self.hdf5_filepath, "r") as f:
            return np.squeeze(f[self.hdf5path][()])
        #TODO option for passing a currently open h5py.File rather than requiring opening a new one.
    @property
    def shape(self)->tuple[int, ...]:
        """Get the size of the image."""
        with h5py.File(self.hdf5_filepath, "r") as f:
            shape=tuple([int(dimension) for dimension in f[self.hdf5path].shape if dimension!=1])
        return shape
    def for_json(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":self._image_type,
            "hdf5_filepath":self.hdf5_filepath.as_posix(),
            "hdf5path":self.hdf5path,
            "image_name":self.name
            }
    def check_image_path(self)->bool:
        """Checks if image filepath is a file."""
        return self.hdf5_filepath.is_file()
    def find_image_path(self,mis_fp,update=True)->Path|None:
        """Find, and optionally update, image paths.
        - Checks stored location.
        - Checks mis filepath folder for matching name."""
        filepath=Path(mis_fp)
        return_path=Path("")
        if self.check_image_path():
            return_path=self.hdf5_filepath
        else:
            check_path=filepath.parent.joinpath(self.hdf5_filepath.name)
            if check_path.is_file():
                return_path=check_path
        if update and return_path!=Path(""):
            self.hdf5_filepath=return_path
            return return_path
        else:
            return None

image_types:dict[str,Any]={
    MISImageFile._image_type:MISImageFile,
    MISImageHDF5._image_type:MISImageHDF5
}
def setup_image(**image_data)->MISImage:
    return image_types[image_data["image_type"]](**image_data)