from PIL import Image as PILImage
import numpy as np

class Image():
    # Class Variables
    _known_dfe:dict[tuple[int,int],np.ndarray] = dict()
    def __init__(self,image_fp:str):
        self.image_fp=image_fp
        PIL_image=PILImage.open(image_fp)
        self.file_mode=PIL_image.mode
        self.image=PIL_image.convert("RGB")
        self.size=self.image.size
        self.image_array=np.asarray(self.image)
        self.dfe_array=self.dfe_rectangular()
    
    # No set options. Should create new and replace rather than modify existing.
    def dfe_rectangular(self) -> np.ndarray:
        if self.size in self._known_dfe:
            return self._known_dfe[self.size]
        else:
            np_size=(self.size[1],self.size[0]) #converts from (Max X, Max Y) to (#rows, #columns)
            dfe_array=np.fromfunction(lambda x, y: np.minimum.reduce([x+1,y+1,np_size[0]-x,np_size[1]-y]),np_size,dtype=int)
            self._known_dfe[self.size]=dfe_array
            return dfe_array