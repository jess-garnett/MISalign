"""Plugin module that implements support for storing an entire project in a single hdf5."""
import h5py
from pathlib import Path
from json import dumps, loads
from PIL import Image as PILImage
import numpy as np

from MISalign.model.project import MISProject, MISProjectJSON
from MISalign.model.relation import MISRelation, setup_relation
from MISalign.model.image import MISImage, setup_image, image_types


class MISProjectHDF5(MISProjectJSON):
    """Access image data and information from a HDF5."""

class MISImageHDF5(MISImage):
    _image_type="hdf5"
    """Access image data and information from a HDF5."""
    def __init__(self,**image_data)->None:
        self.hdf5_filepath=Path(image_data["hdf5_filepath"])
        self.name:str=image_data["image_name"]
        self._dict:dict=image_data
        self._PIL_mode=image_data["PIL_mode"]
    def __str__(self):
        return "Image '"+self.name+"' with shape:"+str(self.get_image_size())
    def get_image_array(self,PIL_mode:str="RGB")->np.ndarray:
        """Get a nparray of the image."""
        if self._PIL_mode==PIL_mode:
            with h5py.File(self.hdf5_filepath, "r") as f:
                return f[f"images/{self.name}"][()] # type: ignore
        else:
            with h5py.File(self.hdf5_filepath, "r") as f:
                PIL_image=PILImage.fromarray(f["images"][self.name][()]) # type: ignore
            PIL_image=PIL_image.convert(PIL_mode)
            return np.asarray(PIL_image)
        #TODO option for not keeping the array in memory when working with very large objects.
    def get_image_size(self)->tuple[int,int]:
        """Get the size of the image."""
        with h5py.File(self.hdf5_filepath, "r") as f:
            shape=f["images"][self.name].shape  # type: ignore
        return (shape[1],shape[0]) # PIL size and numpy shape have first two flipped.
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()"""
        return {
            **self._dict, # loaded dict first and then get the current values
            "image_type":self._image_type,
            "hdf5_filepath":self.hdf5_filepath.as_posix(),
            }


image_types[MISImageHDF5._image_type]=MISImageHDF5

def load_mis_project_hdf5(mis_fp) -> MISProjectHDF5:
    with h5py.File(mis_fp) as f:
        mis_object=dict()
        try: # images
            mis_object["images"]=[setup_image(**x.attrs) for x in f["images"].values()]  # type: ignore
        except:
            mis_object["images"]=list()
        try: # relations
            mis_object["relations"]=[setup_relation(**loads(x)) for x in f["relations"]]  # type: ignore
        except:
            mis_object["relations"]=list()
        try: # calibration
            mis_object["calibration"]=dict(f["calibration"].attrs)  # type: ignore
        except:
            mis_object["calibration"]=dict()
        # project
        if "project" in f.keys():
            for key in f["project"].attrs:
                if key in ["images","relations","calibration"]: continue
                else: mis_object[key]=loads(f["project"].attrs[key])  # type: ignore

        mis_object["file_path"]=mis_fp

    return MISProjectHDF5(**mis_object)
    #     mis_object = json.load(infile)
    # if "relations" in mis_object.keys() and mis_object['relations'] is not None:
    #     mis_object["relations"]=[setup_relation(**x) for x in mis_object["relations"]]
    # if "images" in mis_object.keys() and mis_object['images'] is not None:
    #     mis_object["images"]=[MISImageFile(**x) for x in mis_object['images']]
    # mis_object["file_path"]=mis_fp
    # return MISProjectJSON(**mis_object)
def save_mis_project_hdf5(mis_fp,misfile:MISProjectHDF5) -> None:
    save_dict=misfile.save_dict()
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