from PIL import Image as PILImage
import numpy as np
from os.path import split

class Image():
    # Class Variables
    def __init__(self,image_fp:str):
        self.image_fp=image_fp
        self.name=split(image_fp)[1]
        PIL_image=PILImage.open(image_fp)
        self.image=PIL_image.convert("RGB")
        self.size=self.image.size
        self._img=np.asarray(self.image)
        self._dfe=self._dfe_rectangular()

    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self._img.shape)
    
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