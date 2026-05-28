"""
Models for project data organization, data access, and file I/O.

Includes `Protocol` model: `MISProject`

MISProjects contain information about a set of images, relations, calibration.
MISProjects can also have additional JSON-dumpable information stored in them.
"""

from typing import Protocol, runtime_checkable, Any
from misalign.model.relation import MISRelation, setup_relation
from misalign.model.image import MISImage, MISImageFile,setup_image, MISImageHDF5
from misalign.calibration.calibrate import calibration_from_json
import json
from pathlib import Path
import h5py

# for runtime TYPE_CHECKING:
import numpy as np

@runtime_checkable
class MISProject(Protocol):
    """Protocol - Contains information about a set of images, relations, and a calibration"""
    data:dict[str,Any]
    _images:list[MISImage]
    _relations:list[MISRelation]
    _calibration:dict[str,Any]
    _file_path:Path|None
    def __init__(self,
        images:list[MISImage]|None = None,
        relations:list[MISRelation]|None = None,
        calibration:dict[str,Any]|None = None,
        file_path:Path|str|None = None,
        **mis_data)->None:
        """
        Initialize MISProject
        """
        self.data=mis_data
        
        if images is None:
            self._images=list()
        else:
            self._images=images

        if relations is None:
            self._relations=list()
        else:
            self._relations=relations

        if calibration is None:
            self._calibration=dict()
            #dictionary with 'pixel', 'length', and 'length_unit'
        else:
            self._calibration=calibration

        if file_path is None:
            self._file_path=None
            #dictionary with 'pixel', 'length', and 'length_unit'
        else:
            self._file_path=Path(file_path)

    def __str__(self)->str:
        if len(self._images)==0 and len(self._relations)==0 and len(self._calibration)==0 and self.get_project_path() is None:
            return "An empty misalign project."
        else:
            return "A misalign project with:\n"+"\n".join([
                "Images:\n"+"\n".join(["    "+x for x in self.get_image_names()]),
                "Relations:\n"+"\n".join(["    "+str(x.get_reference()) for x in self._relations]),
                "Calibration:\n"+"\n".join([f"    {key} : {self._calibration[key]}" for key in ['pixel','length','length_unit'] if key in self._calibration]),
                "Project Path:\n"+f"    {self.get_project_path()}"
            ])
    # relation methods
    def get_relations(self)->list[MISRelation]:
        """Get the list of MISRelations."""
        return self._relations
    def set_relations(self,relations:list[MISRelation]):
        """Set the list of relations."""
        self._relations=relations
    def set_relation(self,relation_index:int,relation:MISRelation):
        """Set a specific relation based on its index in the list of relations.
        - Replaces existing relation."""
        self._relations[relation_index]=relation
    def index_relation(self,relation:MISRelation)->int:
        """Get the index of a relation."""
        return [i for i,x in enumerate(self._relations) if x==relation][0]
    def add_relation(self,relation:MISRelation)->int:
        """Append a relation to the list of relations and return it's index."""
        self._relations.append(relation)
        return len(self._relations)-1
    def remove_relation(self,relation:MISRelation):
        """Remove a relation from the list of relations."""
        self._relations.remove(relation)
    def find_relations(self,image_name:str)->list[MISRelation]:
        """Find all relations which include a specific image."""
        return [x for x in self._relations if image_name in x.get_reference()]
    def rename_image_relations(self, old_image_name:str,new_image_name:str):
        """Rename an image in all relations.
        - Does not modify images."""
        for i,r in enumerate(self._relations):
            if old_image_name in r.get_reference():
                relation_data=r.for_json()
                relation_data["image_pair"]=tuple([new_image_name if x==old_image_name else x for x in relation_data["image_pair"]])
                self.set_relation(
                    relation_index=i,
                    relation=setup_relation(**relation_data))

    
    # image methods
    def get_image_names(self)->list[str]:
        """Get the list of image names."""
        return [x.name for x in self._images]
    def get_image(self,image_name:str)->MISImage:
        """Get the image for an image name."""
        return [x for x in self._images if x.name==image_name][0]
    def set_image(self,image_name:str,image:MISImage):
        """Set the image for an image name.
        - If `image_name` is already in images, replaces.
        - If `image_name` is not in images, appends."""
        if image_name in self.get_image_names():
            # replace an image
            image_index=[i for i,name in enumerate(self.get_image_names()) if name==image_name][0]
            self._images[image_index]=image
        else:
            # add the image
            self._images.append(image)
    def set_images(self,images:list[MISImage]):
        """Replaces all the current images with the given images."""
        self._images=images
    def remove_image(self, image_name:str):
        """Remove the image for an image name.
        - Does not modify/delete the image file.
        - Does not modify/delete relations."""
        for name in self.get_image_names():
            if name==image_name:
                self._images.remove(self.get_image(image_name=name))
    def find_image_paths(self,mis_filepath,update=True):
        """Finds and optionally updates all image names using stored paths and mis_filepath."""
        return {image.name:image.find_image_path(mis_fp=mis_filepath,update=update) for image in self._images}

    # calibration methods
    def set_calibration(self,calibration:dict):
        """Set the calibration."""
        self._calibration=calibration
    def get_calibration(self)->dict:
        """Get the calibration."""
        return self._calibration
    
    # project methods
    def set_project_path(self,project_file_path:str|Path):
        """Set path for project save file."""
        self._file_path=Path(project_file_path)
    def get_project_path(self)->Path|None:
        """Get path for project save file.
        - Returns `None` if project does not currently have save file."""
        try:
            return self._file_path
        except AttributeError:
            return None
    
    # save methods
    def for_json(self):
        if self._file_path is not None:
            file_path=Path(self._file_path).as_posix()
        else:
            file_path=None
        return {**self.data,
                "relations":[x.for_json() for x in self._relations],
                "images":[x.for_json() for x in self._images],
                "calibration":self._calibration,
                "file_path":file_path}

class MISProjectJSON(MISProject):
    """MISProject compatible with loading from/saving to JSON. Contains:
    - Image Filepaths
    - Relations
    - Calibration
    """
    @classmethod
    def load(cls,mis_filepath)->'MISProjectJSON':
        with open(mis_filepath) as f:
            mis_data=json.load(f)
        if "relations" in mis_data.keys() and mis_data['relations'] is not None:
            mis_data["relations"]=[setup_relation(**x) for x in mis_data["relations"]]
        if "images" in mis_data.keys() and mis_data['images'] is not None:
            mis_data["images"]=[setup_image(**x) for x in mis_data['images']]
        mis_data["file_path"]=mis_filepath
        loaded_project=cls(**mis_data)
        return loaded_project
    def save(self,mis_filepath):
        mis_data=self.for_json()
        mis_data["file_path"]=str(mis_filepath)
        with open(mis_filepath,"w") as f:
            f.write(json.dumps(mis_data,indent=4))
    @classmethod
    def build(cls,
                mis_filepath:Path|str|None=None,
                image_filepaths:list[Path]|list[str]|None=None,
                calibration_filepath:Path|str|None=None,
                **kwargs)->'MISProjectJSON':
        mis_data=dict()
        if image_filepaths is not None:
            mis_data["images"]=[MISImageFile(image_filepath=x) for x in image_filepaths]
        if calibration_filepath is not None:
            mis_data["calibration"]=calibration_from_json(calibration_filepath)
        if mis_filepath is not None:
            mis_data["file_path"]=mis_filepath
        for key,value in kwargs.items():
            mis_data[key]=value
        new_project=cls(**mis_data)
        return new_project

def convert_mis_project_json(mis_fp)->MISProjectJSON:
    """Convert an old `.mis` format file into a MISProjectJSON."""
    with open(mis_fp) as infile:
        mis_load = json.load(infile)
    mp=MISProjectJSON.build(
        image_filepaths=mis_load["image_fps"],
        )
    build_relations=list()
    for x in mis_load["relations"]:
        try:
            if type(x[2][0]) is int: # relation data is most likely rectangular offset
                relation_data=dict(rectangular=x[2])
            else: #relation data is most likely points
                relation_data=dict(points=x[2])
        except IndexError: # relation data is most likely None
            relation_data=dict()
        build_relations.append(setup_relation(
                image_pair=x[0],
                relation_type=x[1],
                **relation_data))
    mp.set_relations(build_relations)
    return mp

class MISProjectHDF5(MISProjectJSON):
    """Access image data and information from a HDF5."""
    @classmethod
    def load(cls,
            mis_filepath:Path|str,
            project_hdf5path:str="MISContainer0/project",)->'MISProjectHDF5':
        with h5py.File(mis_filepath) as f:
            mis_data=json.loads(f[project_hdf5path][()])
            mis_data["file_path"]=Path(mis_filepath).as_posix()
            mis_data["hdf5_path"]=project_hdf5path

            if "relations" in mis_data.keys() and mis_data['relations'] is not None:
                mis_data["relations"]=[setup_relation(**x) for x in mis_data["relations"]]
            if "images" in mis_data.keys() and mis_data['images'] is not None:
                mis_data["images"]=[setup_image(**x) for x in mis_data['images']]
        loaded_project=cls(**mis_data)
        return loaded_project
    def save(self,
             mis_filepath:Path|str|None=None,
             project_hdf5path:str|None=None,
             ):
        mis_data=self.for_json()
        if mis_filepath is not None:
            mis_data["file_path"]=Path(mis_filepath).as_posix()
        if project_hdf5path is not None:
            mis_data["hdf5_path"]=str(project_hdf5path)
        with h5py.File(mis_data["file_path"], "r+") as f:
            try:
                del f[mis_data["hdf5_path"]]
            except KeyError:
                pass
            f[mis_data["hdf5_path"]]=json.dumps(mis_data)
    @classmethod
    def build(cls,
                mis_filepath:Path|str,
                project_hdf5path:str="MISContainer0/project",
                images_hdf5path:str="MISContainer0/images",
                ingest_image_filepaths:list[Path|str]|None=None,
                include_image_filepaths:list[Path|str]|None=None,
                ingest_image_objects:list[MISImage]|None=None,
                include_image_objects:list[MISImage]|None=None,
                ingest_arrays:dict[str,np.ndarray]|None=None,
                calibration_filepath:Path|str|None=None,
                calibration_dict:dict|None=None,
                **kwargs)->'MISProjectHDF5':  # ty:ignore[invalid-method-override]
                # Violates Liskov Substitution Principle - I am okay with that as signficantly different build args are possible.
                #kwargs
                # `image_h5py_file_mode` h5py.File mode - Default: `'x'` Create file, fail if exists
                # `image_h5py_compression` h5py.File.create_dataset kwarg - Default: `'gzip'` compression algorithm.
                # `image_h5py_compression_opts` h5py.File.create_dataset kwarg - Default: `9` maximum compression.
        mis_data=dict()
        mis_data["file_path"]=Path(mis_filepath).as_posix()
        mis_data["hdf5_path"]=str(project_hdf5path)

        mis_data["images"]:list[MISImage]=list()
        if include_image_filepaths is not None:
            [mis_data["images"].append(MISImageFile(image_filepath=x)) for x in include_image_filepaths]
        if include_image_objects is not None:
            [mis_data["images"].append(x) for x in include_image_objects]
        
        if any([ingest_image_filepaths is not None,
                ingest_image_objects is not None,
                ingest_arrays is not None]
            ):
            try:
                image_h5py_file_mode:str=kwargs["image_h5py_file_mode"]
                del kwargs["image_h5py_file_mode"]
            except KeyError:
                image_h5py_file_mode='x'

            try:
                image_h5py_compression:str=kwargs["image_h5py_compression"]
                del kwargs["image_h5py_compression"]
            except KeyError:
                image_h5py_compression='gzip'

            try:
                image_h5py_compression_opts:int=kwargs["image_h5py_compression_opts"]
                del kwargs["image_h5py_compression_opts"]
            except KeyError:
                image_h5py_compression_opts=9
            with h5py.File(mis_filepath,mode=image_h5py_file_mode) as f:
                f.create_group(images_hdf5path)
                if ingest_image_filepaths is not None:
                    for image_filepath in ingest_image_filepaths:
                        image_file=MISImageFile(image_filepath=image_filepath)
                        image_hdf5path="/".join([images_hdf5path,image_file.name])
                        f.create_dataset(image_hdf5path,
                                 data=np.asarray(image_file),
                                 compression=image_h5py_compression,
                                 compression_opts=image_h5py_compression_opts)
                        mis_data["images"].append(
                            MISImageHDF5(
                                hdf5_filepath=mis_data["file_path"],
                                image_name=image_file.name,
                                hdf5path=image_hdf5path
                                ))
                if ingest_image_objects is not None:
                    for image in ingest_image_objects:
                        image_hdf5path="/".join([images_hdf5path,image.name])
                        f.create_dataset(image_hdf5path,
                                 data=np.asarray(image),
                                 compression=image_h5py_compression,
                                 compression_opts=image_h5py_compression_opts)
                        mis_data["images"].append(
                            MISImageHDF5(
                                hdf5_filepath=mis_data["file_path"],
                                image_name=image.name,
                                hdf5path=image_hdf5path
                                ))
                if ingest_arrays is not None:
                    for name,array in ingest_arrays.items():
                        image_hdf5path="/".join([images_hdf5path,name])
                        f.create_dataset(image_hdf5path,
                                 data=np.asarray(array),
                                 compression=image_h5py_compression,
                                 compression_opts=image_h5py_compression_opts)
                        mis_data["images"].append(
                            MISImageHDF5(
                                hdf5_filepath=mis_data["file_path"],
                                image_name=name,
                                hdf5path=image_hdf5path
                                ))
                #TODO shift compression parameters to kwargs

        if calibration_filepath is not None:
            mis_data["calibration"]=calibration_from_json(calibration_filepath)
        if calibration_dict is not None:
            # {"pixel":number,"length":number,"length_unit":str}
            if set(calibration_dict.keys())=={"pixel","length","length_unit"}:
                mis_data["calibration"]=calibration_dict
            else:
                raise KeyError(f"`calibration_dict` {calibration_dict} does not have expected keys `'pixel','length','length_unit'`")
        
        for key,value in kwargs.items():
            mis_data[key]=value
        
        new_project=cls(**mis_data)
        with h5py.File(mis_filepath,mode='a') as f:
            f[mis_data["hdf5_path"]]=json.dumps(new_project.for_json())
        return new_project

#TODO Add a project registry > uses file extension and/or keywords to identify project type when given file path.