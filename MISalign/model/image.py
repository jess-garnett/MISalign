from PIL import Image as PILImage
import numpy as np
from os.path import split, isfile
from typing import Protocol, runtime_checkable, Any
from pathlib import Path

class Image():
    """Store image data and generates numpy arrays for image and distance from edge(DFE)
    - DFE's are used for image blending.
    """
    def __init__(self,image_fp:str):
        self.image_fp=image_fp
        self.name=split(image_fp)[1]
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
    
    def img_arr(self,**kwargs) -> np.ndarray: # type: ignore
        if 'rotation' in kwargs:
            #TODO handle rotation - 0, 90, 180, 270 special cases.
            pass
        else:
            return self._img

    def dfe_arr(self,**kwargs) -> np.ndarray:  # type: ignore
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
    def __init__(self,**image_data)->None:
        self.name:str
    def __str__(self)->str:
        ...
    def get_image_array(self,PIL_mode:str="RGB")->np.ndarray:
        """Get a nparray of the image."""
        ...
    def get_image_size(self)->tuple[int,int]:
        """Get the size of the image."""
        ...
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        ...

class MISImageFile():
    """Access image data and information for an image file.
    - Expects image_filepath:str|Path"""
    _image_type="file"
    def __init__(self,**image_data)->None:
        self.image_filepath=Path(image_data["image_filepath"])
        self.name:str=self.image_filepath.name
        self._dict:dict=image_data
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
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":"file",
            "image_filepath":self.image_filepath.as_posix(),
            }
    def check_image_path(self)->bool:
        """Checks if image filepath is a file."""
        return isfile(self.image_filepath)
    def find_image_path(self,mis_fp,update=True)->Path|None:
        """Find, and optionally update, image paths.
        - Checks stored location.
        - Checks mis filepath folder for matching name."""
        filepath=Path(mis_fp)
        return_path=Path("")
        if self.check_image_path():
            return_path=self.image_filepath
        else:
            check_path=filepath.parent.joinpath(self.name)
            if isfile(check_path):
                return_path=check_path
        if update and return_path!=Path(""):
            self.image_filepath=return_path
            return return_path
        else:
            return None


image_types:dict[str,Any]={
    MISImageFile._image_type:MISImageFile
}
def setup_image(**image_data)->MISImage:
    return image_types[image_data["image_type"]](**image_data)