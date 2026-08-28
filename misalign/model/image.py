"""
Models for image data access.

Includes `Protocol` model: `MISImage`
"""

from PIL import Image as PILImage
import numpy as np
from typing import Protocol, runtime_checkable, Any
from collections.abc import Callable
from pathlib import Path
import h5py

@runtime_checkable
class MISImage(Protocol):
    """Protocol - Access image data and information."""
    def __init__(self,**image_data)->None:
        """
        Initialize a MISImage.

        Parameters
        ----------
        **image_data : kwargs
            Required kwargs vary depending on class of MISImage.
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """
        self.name:str
        self._filter:None|Callable[[np.ndarray],np.ndarray]
    def __str__(self)->str:
        """
        String representation of the Image.

        Returns
        -------
        str
            Description including image name and shape.
        """
        ...
    def __array__(self)->np.ndarray:
        """
        Get image array.
        
        Returns
        -------
        array : np.ndarray
            Numpy array of the image.
        """
        ...
    @property
    def shape(self)->tuple[int]:
        """
        Get the shape of the image.
        
        Returns
        -------
        shape : tuple[int]
            Tuple of ints describing the shape in numpy order - row, col, depth - (1200,1600,3).

        Notes
        -----
        Shape should behave cache-like.
        It may be expensive the first time a `MISImage` has to get the shape but after that it should be very fast.
        """
        ...
    def set_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None)->None:
        """
        Sets a default filter for the image array.

        Applies when `.__array__` or `.shape` are used.

        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
            `None` removes the default filter.
        """
        ...
    def get_filter(self)->None|Callable[[np.ndarray],np.ndarray]:
        """
        Gets the default filter of the image array.

        The default filter is applied when `.__array__` or `.shape` are used.

        Returns
        -------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter being applied to the image array or `None` if no default filter is set.
        """
        ...
    def with_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None,apply_default=True)->np.ndarray:
        """
        Returns the image array with a filter applied.
        
        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
        apply_default : None | Callable[[np.ndarray],np.ndarray]
            Whether to use the default filter before the parameter filter. `True` by default.
        """
        ...
    def for_json(self)->dict:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        image_data : dict
            JSON dump-able representation of image information.
        """
        ...
    def find_image_path(self,
            mis_fp:Path|str,
            update:bool=True
            )->Path|None:
        """
        Find, and optionally update, filepaths.
        
        Checks stored location. Checks mis filepath folder for matching name.

        Parameters
        ----------
        mis_fp:Path|str,
            Filepath to MISProject, expected to be in the same folder as the file with the image data.
        update:bool=True
            If true when a matching file is found it will update the filepath property.

        Returns
        -------
        return_path : Path | None
            If a matching path is found it is returned, else `None` is returned.
        """

class MISImageFile():
    """
    Access image data and information from an image file.
    """
    _image_type="file"
    def __init__(self,
        image_filepath:Path|str|None=None,
        **image_data):
        """
        Initialize a MISImageFile from an image filepath.

        Parameters
        ----------
        image_filepath : Path | str | None
            File path to an image file.
        **image_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """
        if image_filepath is None:
            raise ValueError("`image_filepath` cannot be None.")
        self.image_filepath=Path(image_filepath)
        self.name:str=self.image_filepath.name
        self._dict:dict=image_data
        self._shape:None|tuple[int, ...]=None
        self._filter:None|Callable[[np.ndarray],np.ndarray]=None
        self._filter_changed:bool=False
    def __str__(self):
        """
        String representation of the Image.

        Returns
        -------
        str
            Description including image name and shape.
        """
        return "Image '"+self.name+"' with shape:"+str(self.shape)
    def __array__(self)->np.ndarray:
        """
        Get image array.
        
        Returns
        -------
        array : np.ndarray
            Numpy array of the image file.
        """
        PIL_image=PILImage.open(self.image_filepath)
        array=np.asarray(PIL_image)
        if self._filter is not None:
            array=self._filter(array)
            self._filter_changed=False
        self._shape=array.shape
        return array
    @property
    def shape(self)->tuple[int, ...]:
        """
        Get the shape of the image.
        
        Returns
        -------
        shape : tuple[int]
            Tuple of ints describing the shape in numpy order - row, col, depth - (1200,1600,3).

        Notes
        -----
        `shape` acts cache-like and can be accessed on-demand without needing to store it separately.
        Changing the default filter will reset the shape cache.
        """
        
        if self._shape is None or self._filter_changed is True:
            self._shape=self.__array__().shape
            self._filter_changed=False
        return self._shape
    def set_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None)->None:
        """
        Sets a default filter for the image array.

        Applies when `.__array__` or `.shape` are used.

        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
            `None` removes the default filter.
        """
        self._filter=filter
        self._filter_changed=True
        self._shape=None # Resets self._shape as the filter may have changed the default shape.
    def get_filter(self)->None|Callable[[np.ndarray],np.ndarray]:
        """
        Gets the default filter of the image array.

        The default filter is applied when `.__array__` or `.shape` are used.

        Returns
        -------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter being applied to the image array or `None` if no default filter is set.
        """
        return self._filter
    def with_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None,apply_default=True)->np.ndarray:
        """
        Returns the image array with a filter applied.
        
        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
        apply_default : None | Callable[[np.ndarray],np.ndarray]
            Whether to use the default filter before the parameter filter. `True` by default.
        """
        if apply_default is False:
            default_filter=self.get_filter()
            default_shape=self._shape
            self.set_filter(filter=None)
        
        array=self.__array__()
        if filter is not None:
            array=filter(array)

        if apply_default is False:
            self.set_filter(filter=default_filter)
            self._shape=default_shape
            self._filter_changed=False
        
        return array
    def for_json(self)->dict:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        image_data : dict
            JSON dump-able representation of image information.
        """
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":"file",
            "image_filepath":self.image_filepath.as_posix(),
            }
    def check_image_path(self)->bool:
        """
        Checks if image filepath is a file.

        Returns
        -------
        bool
            True if `self.image_filepath` is a file.
        """
        return self.image_filepath.is_file()
    def find_image_path(self,
            mis_fp:Path|str,
            update:bool=True
            )->Path|None:
        """
        Find, and optionally update, image filepaths.
        
        Checks stored location. Checks mis filepath folder for matching name.

        Parameters
        ----------
        mis_fp:Path|str,
            Filepath to MISProject, expected to be in the same folder as the image file.
        update:bool=True
            If true when a matching file is found it will replace `self.image_filepath`.

        Returns
        -------
        return_path : Path | None
            If a matching path is found it is returned, else `None` is returned.
        """
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

class MISImageHDF5():
    """
    Access image data and information from an HDF5 file.
    """
    _image_type="hdf5"
    """Access image data and information from a HDF5."""
    def __init__(self,
        hdf5_filepath:Path|str|None=None,
        hdf5path:str|None=None,
        image_name:str|None=None,
        **image_data)->None:
        """
        Initialize a MISImageHDF5 from a HDF5 filepath, HDF5 path, and image name.

        Parameters
        ----------
        hdf5_filepath : Path | str | None
            File path to an HDF5 file.
        hdf5path : str | None
            Path inside the hdf5 to the image dataset.
        image_name : str | None
            Name for the image.
        **image_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """
        if hdf5_filepath is None:
            raise ValueError("`hdf5_filepath` cannot be None.")
        if hdf5path is None:
            raise ValueError("`hdf5path` cannot be None.")
        if image_name is None:
            raise ValueError("`image_name` cannot be None.")
        self.hdf5_filepath=Path(hdf5_filepath)
        self.hdf5path:str=hdf5path
        self.name:str=image_name
        self._dict:dict=image_data
        self._shape:None|tuple[int, ...]=None
        self._filter:None|Callable[[np.ndarray],np.ndarray]=None
        self._filter_changed:bool=False
    def __str__(self):
        """
        String representation of the Image.

        Returns
        -------
        str
            Description including image name and shape.
        """
        return "Image '"+self.name+"' with shape:"+str(self.shape)
    def __array__(self)->np.ndarray:
        """
        Get image array.
        
        Returns
        -------
        array : np.ndarray
            Numpy array of the hdf5 dataset with 1-length axes squeezed.
        """
        with h5py.File(self.hdf5_filepath, "r") as f:
            array= np.squeeze(f[self.hdf5path][()])
        if self._filter is not None:
            array=self._filter(array)
        return array
        #TODO option for passing a currently open h5py.File rather than requiring opening a new one.
    @property
    def shape(self)->tuple[int, ...]:
        """
        Get the shape of the image.
        
        Returns
        -------
        shape : tuple[int]
            Tuple of ints describing the shape in numpy order - row, col, depth - (1200,1600,3).

        Notes
        -----
        If a filter is not applied then `shape` is taken from the hdf5 dataset shape attribute and does not require accessing the full array.
        """
        
        if self._filter is None:
            with h5py.File(self.hdf5_filepath, "r") as f:
                shape=tuple([int(dimension) for dimension in f[self.hdf5path].shape if dimension!=1])
        else:
            if self._shape is None or self._filter_changed is True:
                self._shape=self.__array__().shape
                self._filter_changed=False
            shape=self._shape
        return shape
    def set_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None)->None:
        """
        Sets a default filter for the image array.

        Applies when `.__array__` or `.shape` are used.

        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
            `None` removes the default filter.
        """
        self._filter=filter
        self._filter_changed=True
        self._shape=None # Resets self._shape as the filter may have changed the default shape.
    def get_filter(self)->None|Callable[[np.ndarray],np.ndarray]:
        """
        Gets the default filter of the image array.

        The default filter is applied when `.__array__` or `.shape` are used.

        Returns
        -------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter being applied to the image array or `None` if no default filter is set.
        """
        return self._filter
    def with_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None,apply_default=True)->np.ndarray:
        """
        Returns the image array with a filter applied.
        
        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
        apply_default : None | Callable[[np.ndarray],np.ndarray]
            Whether to use the default filter before the parameter filter. `True` by default.
        """
        if apply_default is False:
            default_filter=self.get_filter()
            default_shape=self.shape
            self.set_filter(filter=None)
        
        array=self.__array__()
        if filter is not None:
            array=filter(array)

        if apply_default is False:
            self.set_filter(filter=default_filter)
            self._shape=default_shape
            self._filter_changed=False
        
        return array
    def for_json(self)->dict:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        image_data : dict
            JSON dump-able representation of image information.
        """
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":self._image_type,
            "hdf5_filepath":self.hdf5_filepath.as_posix(),
            "hdf5path":self.hdf5path,
            "image_name":self.name
            }
    def check_hdf5_path(self)->bool:
        """
        Checks if hdf5 filepath is a file.

        Returns
        -------
        bool
            True if `self.hdf5_filepath` is a file.
        """
        return self.hdf5_filepath.is_file()
    def find_image_path(self,
            mis_fp:Path|str,
            update:bool=True
            )->Path|None:
        """
        Find, and optionally update, hdf5 filepaths.
        
        Checks stored location. Checks mis filepath folder for matching name.

        Parameters
        ----------
        mis_fp:Path|str,
            Filepath to MISProject, expected to be in the same folder as the hdf5 file.
        update:bool=True
            If true when a matching file is found it will replace `self.hdf5_filepath`.

        Returns
        -------
        return_path : Path | None
            If a matching path is found it is returned, else `None` is returned.
        """
        filepath=Path(mis_fp)
        return_path=Path("")
        if self.check_hdf5_path():
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


class MISImageNPZ():
    """
    Access image data and information from a numpy file.
    """
    _image_type="npz"
    def __init__(self,
        npz_filepath:Path|str|None=None,
        npz_key:str|None=None,
        image_name:str|None=None,
        **image_data)->None:
        """
        Initialize a MISImageNPZ from an NPZ filepath, NPZ key, and image name.

        Parameters
        ----------
        npz_filepath : Path | str | None
            File path to a `.npz` file.
        npz_key : str | None
            Key inside the npz to the image dataset.
        image_name : str | None
            Name for the image.
        **image_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """
        if npz_filepath is None:
            raise ValueError("`npz_filepath` cannot be None.")
        if npz_key is None:
            raise ValueError("`npz_key` cannot be None.")
        if image_name is None:
            raise ValueError("`image_name` cannot be None.")
        self.npz_filepath=Path(npz_filepath)
        self.npz_key:str=npz_key
        self.name:str=image_name
        self._dict:dict=image_data
        self._shape:None|tuple[int, ...]=None
        self._filter:None|Callable[[np.ndarray],np.ndarray]=None
        self._filter_changed:bool=False
    def __str__(self):
        """
        String representation of the Image.

        Returns
        -------
        str
            Description including image name and shape.
        """
        return "Image '"+self.name+"' with shape:"+str(self.shape)
    def __array__(self)->np.ndarray:
        """
        Get image array.
        
        Returns
        -------
        array : np.ndarray
            Numpy array of the npz dataset with 1-length axes squeezed.
        """
        with np.load(self.npz_filepath, "r",allow_pickle=False) as f:
            array= np.squeeze(f[self.npz_key])
        if self._filter is not None:
            array=self._filter(array)
        return array
    @property
    def shape(self)->tuple[int, ...]:
        """
        Get the shape of the image.
        
        Returns
        -------
        shape : tuple[int]
            Tuple of ints describing the shape in numpy order - row, col, depth - (1200,1600,3).

        Notes
        -----
        If a filter is not applied then `shape` is taken from the npz object shape and does not require accessing the full array.
        """
        
        if self._filter is None:
            with np.load(self.npz_filepath, "r",allow_pickle=False) as f:
                shape=tuple([int(dimension) for dimension in f[self.npz_key].shape if dimension!=1])
        else:
            if self._shape is None or self._filter_changed is True:
                self._shape=self.__array__().shape
                self._filter_changed=False
            shape=self._shape
        return shape
    def set_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None)->None:
        """
        Sets a default filter for the image array.

        Applies when `.__array__` or `.shape` are used.

        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
            `None` removes the default filter.
        """
        self._filter=filter
        self._filter_changed=True
        self._shape=None # Resets self._shape as the filter may have changed the default shape.
    def get_filter(self)->None|Callable[[np.ndarray],np.ndarray]:
        """
        Gets the default filter of the image array.

        The default filter is applied when `.__array__` or `.shape` are used.

        Returns
        -------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter being applied to the image array or `None` if no default filter is set.
        """
        return self._filter
    def with_filter(self,filter:None|Callable[[np.ndarray],np.ndarray]=None,apply_default=True)->np.ndarray:
        """
        Returns the image array with a filter applied.
        
        Parameters
        ----------
        filter : None | Callable[[np.ndarray],np.ndarray]
            Filter to apply to the image array or `None` by default.
        apply_default : None | Callable[[np.ndarray],np.ndarray]
            Whether to use the default filter before the parameter filter. `True` by default.
        """
        if apply_default is False:
            default_filter=self.get_filter()
            default_shape=self.shape
            self.set_filter(filter=None)
        
        array=self.__array__()
        if filter is not None:
            array=filter(array)

        if apply_default is False:
            self.set_filter(filter=default_filter)
            self._shape=default_shape
            self._filter_changed=False
        
        return array
    def for_json(self)->dict:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        image_data : dict
            JSON dump-able representation of image information.
        """
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":self._image_type,
            "npz_filepath":self.npz_filepath.as_posix(),
            "npz_path":self.npz_key,
            "image_name":self.name
            }
    def check_npz_path(self)->bool:
        """
        Checks if npz filepath is a file.

        Returns
        -------
        bool
            True if `self.npz_filepath` is a file.
        """
        return self.npz_filepath.is_file()
    def find_image_path(self,
            mis_fp:Path|str,
            update:bool=True
            )->Path|None:
        """
        Find, and optionally update, npz filepaths.
        
        Checks stored location. Checks mis filepath folder for matching name.

        Parameters
        ----------
        mis_fp:Path|str,
            Filepath to MISProject, expected to be in the same folder as the npz file.
        update:bool=True
            If true when a matching file is found it will replace `self.npz_filepath`.

        Returns
        -------
        return_path : Path | None
            If a matching path is found it is returned, else `None` is returned.
        """
        filepath=Path(mis_fp)
        return_path=Path("")
        if self.check_npz_path():
            return_path=self.npz_filepath
        else:
            check_path=filepath.parent.joinpath(self.npz_filepath.name)
            if check_path.is_file():
                return_path=check_path
        if update and return_path!=Path(""):
            self.npz_filepath=return_path
            return return_path
        else:
            return None

image_types:dict[str,Any]={
    MISImageFile._image_type:MISImageFile,
    MISImageHDF5._image_type:MISImageHDF5,
    MISImageNPZ._image_type:MISImageNPZ
}

def setup_image(**image_data)->MISImage:
    """
    Construct `MISImage` from image data.

    Uses the `image_type` field in `image_data` to select the correct MISImage implementation to initialize.

    Parameters
    ----------
    image_data : dict
        JSON dump-able representation of image information. Must include `image_type`.

    Returns
    -------
    image : MISImage
        Returns a MISImage initialized from `image_data`. 
        MISImage implementation selection is based on `image_type` lookup in the `image_types` dictionary.
    """
    return image_types[image_data["image_type"]](**image_data)

#TODO add filters to unit tests.