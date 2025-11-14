from PIL import Image as PILImage
import numpy as np
from os.path import split
from typing import Protocol, runtime_checkable
from pathlib import Path

class Image():
    """Store image data and generates numpy arrays for image and distance from edge(DFE)
    - DFE's are used for image blending.
    """
    def __init__(self,image_fp:str):
        self.image_fp=image_fp
        self.name=split(image_fp)[1].split
        PIL_image=PILImage.open(image_fp)
        self.image=PIL_image.convert("RGB")
        self.size=self.image.size
        self._img=np.asarray(self.image)
        self._dfe=self._dfe_rectangular()

    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self.size)
    
    def _dfe_rectangular(self) -> np.ndarray:
        np_size=(self.size[1],self.size[0]) #converts from (Max X, Max Y) to (#rows, #columns)
        dfe_array=np.fromfunction(lambda x, y: np.minimum.reduce([x+1,y+1,np_size[0]-x,np_size[1]-y]),np_size,dtype=int)
        return dfe_array
    
    def img_arr(self,**kwargs) -> np.ndarray:
        if 'rotation' in kwargs:
            #TODO handle rotation - 0, 90, 180, 270 special cases.
            pass
        else:
            return self._img

    def dfe_arr(self,**kwargs) -> np.ndarray:
        if 'rotation' in kwargs:
            #TODO handle rotation - 0, 90, 180, 270 special cases.
            pass
        else:
            return self._dfe
        
#TODO move dfe generation out of the image class.
    # It already is? render.py has it's own dfe/weight generation. this code doesn't get used at all?
#TODO make render modules actually use the image array instead of just opening the image themselves.

@runtime_checkable
class MISImage(Protocol):
    """Access image data and information."""
    def __str__(self)->str:
        ...
    def get_image_array(self,PIL_Mode:str)->np.ndarray:
        """Get a nparray of the image."""
        ...
    def get_image_size(self)->tuple[int,int]:
        """Get the size of the image."""
        ...

class MISImageFile():
    """Access image data and information for an image file."""
    def __init__(self,image_filepath:str|Path):
        self.image_filepath=Path(image_filepath)
        self.name=self.image_filepath.stem
        self._PIL_mode=None
    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self.get_image_size())
    def get_image_array(self,PIL_mode:str="RGB")->np.ndarray:
        """Get a nparray of the image."""
        if self._PIL_mode==PIL_mode:
            return self._array
        else:
            PIL_image=PILImage.open(self.image_filepath)
            PIL_image=PIL_image.convert(PIL_mode)
            self._PIL_mode=PIL_mode
            self._array=np.asarray(PIL_image)
            self._size=PIL_image.size
            return self._array
        #TODO option for not keeping the array in memory when working with very large objects.
    def get_image_size(self)->tuple[int,int]:
        """Get the size of the image."""
        try: # if image has already been opened just get the size that was stored.
            return self._size
        except: # if image hasn't been opened then open it and grab the size.
            self.get_image_array()
            return self._size


class MISImageHDF5():
    """Access image data and information from a HDF5."""