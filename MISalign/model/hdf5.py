"""Plugin module that implements support for storing an entire project in a single hdf5."""
import h5py
from pathlib import Path
from json import dumps, loads
from PIL import Image as PILImage
import numpy as np

from misalign.model.project import MISProject, MISProjectJSON
from misalign.model.relation import MISRelation, setup_relation
from misalign.model.image import MISImage, setup_image, image_types


class MISProjectHDF5(MISProjectJSON):
    """Access image data and information from a HDF5."""
    @classmethod
    def load(cls,hdf5_filepath,project_hdf5path): # type: ignore
        with h5py.File(hdf5_filepath) as f:
            mis_data=loads(f[project_hdf5path][()]) # type: ignore
            mis_data["file_path"]=hdf5_filepath

            if "relations" in mis_data.keys() and mis_data['relations'] is not None:
                mis_data["relations"]=[setup_relation(**x) for x in mis_data["relations"]]
            if "images" in mis_data.keys() and mis_data['images'] is not None:
                mis_data["images"]=[setup_image(**x) for x in mis_data['images']]
            loaded_project=MISProjectHDF5(**mis_data)
            return loaded_project
        return cls(**mis_data)
    def save(self, # type: ignore
             hdf5_filepath:Path|str,
             project_hdf5path:str,
             ):
        mis_data=self.save_dict()
        mis_data["file_path"]=hdf5_filepath
        with h5py.File(hdf5_filepath, "r+") as f:
            f[project_hdf5path]=dumps(mis_data)
    @classmethod
    def build(cls,  # type: ignore
                hdf5_filepath:Path|str,
                project_hdf5path:str,
                image_filepaths:list[Path|str]|None=None,
                image_objects:list[MISImage]|None=None,
                calibration_filepath:Path|str|None=None,
                **kwargs):
        ...


class MISImageHDF5(MISImage):
    _image_type="hdf5"
    """Access image data and information from a HDF5."""
    def __init__(self,**image_data)->None:
        self.hdf5_filepath=Path(image_data["hdf5_filepath"])
        self.name:str=image_data["image_name"]
        self.hdf5path:str=image_data["hdf5path"]
        self._dict:dict=image_data
        self._PIL_mode=image_data["PIL_mode"]
    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self.get_image_size())
    def get_image_array(self,PIL_mode:str="RGB")->np.ndarray:
        """Get a nparray of the image."""
        if self._PIL_mode==PIL_mode:
            with h5py.File(self.hdf5_filepath, "r") as f:
                return f[self.hdf5path][()] # type: ignore
        else:
            with h5py.File(self.hdf5_filepath, "r") as f:
                PIL_image=PILImage.fromarray(f[self.hdf5path][()]) # type: ignore
            PIL_image=PIL_image.convert(PIL_mode)
            return np.asarray(PIL_image)
        #TODO option for not keeping the array in memory when working with very large objects.
        #TODO option for getting the exact array as stored without modification > default behavior?
        #TODO option for passing a currently open h5py.File rather than requiring opening a new one.
    def get_image_size(self)->tuple[int,int]:
        """Get the size of the image."""
        with h5py.File(self.hdf5_filepath, "r") as f:
            shape=f[self.hdf5path].shape  # type: ignore
        return (shape[1],shape[0]) # PIL size and numpy shape have first two flipped.
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":self._image_type,
            "hdf5_filepath":self.hdf5_filepath.as_posix(),
            "hdf5path":self.hdf5path,
            "image_name":self.name
            }


image_types[MISImageHDF5._image_type]=MISImageHDF5


def save_mis_project_hdf5(mis_fp,misfile:MISProjectHDF5) -> None:
    save_dict=misfile.save_dict()
    #TODO update this save function to match the new MISProjectHDF5 format
        # Consider avoiding saving/modifying any datasets other than the project scalar without getting explicit direction to do so.
        # Plan around save method for saving an existing project(with some updates) and a build method for creating either a new project, and a new HDF5 if needed.
    with h5py.File(mis_fp,"a") as f:
        try:
            f.create_group("images")
        finally:
            for image_name in misfile.get_image_names():
                if image_name not in f["images"]:  # type: ignore
                    f["images"].create_dataset(image_name,dtype="f") # type: ignore #empty placeholder 
                for key,value in misfile.get_image(image_name).save_dict().items():
                    f["images"][image_name].attrs[key]=value  # type: ignore
        try:
            f.create_dataset("relations")
        finally:
            f["relations"]=[dumps(x) for x in save_dict["relations"]]
        try:
            f.create_group("calibration")
        finally:
            for key,value in misfile.get_calibration().items():
                f["calibration"].attrs[key]=value
        try:
            f.create_group("project")
        finally:
            for key in save_dict:
                if key in ["images","relations","calibration"]: continue
                f["project"].attrs[key]=dumps(save_dict[key])

def build_mis_project_json(
        image_filepaths:list[str],
        calibration_filepath:str|None=None,
        project_filepath:str|None=None,
    )->MISProjectHDF5:
    ...
    #TODO create build method
        # handle images as filepath images, filepath images to ingest into hdf5, or existing hdf5 images