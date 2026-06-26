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
    """Protocol - Contains information about a set of images, relations, and a calibration
    
    MISProject implements primary project methods excluding build/save/load."""
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
        Initialize MISProject.

        Parameters
        ----------
        images : list[MISImage] | None
            list of `MISImage` or `None` by default.
        relations : list[MISRelation] | None
            list of `MISRelation` or `None` by default.
        calibration : dict[str,Any] | None
            calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}` or `None` by default.
        file_path : Path | str | None
            `Path` or path-like string to `.mis` file or `None` by default.
        **mis_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """
        self._dict=mis_data

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
        """
        String representation of the Project.

        Returns
        -------
        str
            Description of the project.
        """
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
        """
        Get the list of `MISRelation`.
        
        Returns
        -------
        relations : list[MISRelation]
            List of relations.
        """
        return self._relations
    def set_relations(self,relations:list[MISRelation])->None:
        """
        Set the list of `MISRelation`.

        Overrides any existing relations.
        
        Parameters
        ----------
        relations : list[MISRelation]
            List of relations.
        """
        self._relations=relations
    def set_relation(self,relation_index:int,relation:MISRelation)->None:
        """
        Replace an existing relation based on its index in the list of relations.

        Parameters
        ----------
        relation_index : int
            Index of the relation to replace.
        relation : MISRelation
            A relation.
        """
        self._relations[relation_index]=relation
    def index_relation(self,relation:MISRelation)->int:
        """
        Get the index of a relation.

        Parameters
        ----------
        relation : MISRelation
            A relation.

        Returns
        -------
        relation_index : int
            Index of the relation.
        """
        return [i for i,x in enumerate(self._relations) if x==relation][0]
    def add_relation(self,relation:MISRelation)->int:
        """
        Append a relation to the list of relations and get its index.

        Parameters
        ----------
        relation : MISRelation
            A relation.

        Returns
        -------
        relation_index : int
            Index of the relation.
        """
        self._relations.append(relation)
        return len(self._relations)-1
    def remove_relation(self,relation:MISRelation)->None:
        """
        Remove a relation from the list of relations.

        Parameters
        ----------
        relation : MISRelation
            A relation.
        """
        self._relations.remove(relation)
    def find_relations(self,image_name:str)->list[MISRelation]:
        """
        Find all relations which include a specific image.

        Parameters
        ----------
        image_name : str
            An image name.

        Returns
        -------
        relations : list[MISRelation]
            List of relations that include the image.
        """
        return [x for x in self._relations if image_name in x.get_reference()]
    def rename_image_relations(self, old_image_name:str,new_image_name:str)->None:
        """
        Rename an image in all relations.

        Parameters
        ----------
        old_image_name : str
            The image name to replace.
        new_image_name : str
            The new image name.
        
        Notes
        -----
        Does not modify images.
        """
        for i,r in enumerate(self._relations):
            if old_image_name in r.get_reference():
                relation_data=r.for_json()
                relation_data["image_pair"]=tuple([new_image_name if x==old_image_name else x for x in relation_data["image_pair"]])
                self.set_relation(
                    relation_index=i,
                    relation=setup_relation(**relation_data))

    
    # image methods
    def get_image_names(self)->list[str]:
        """
        Get the list of image names.

        Returns
        -------
        images : list[str]
            List of image names.
        """
        return [x.name for x in self._images]
    def get_image(self,image_name:str)->MISImage:
        """
        Get the image for an image name.

        Parameters
        ----------
        image_name : str
            An image name.

        Returns
        -------
        image : MISImage
            An image.
        """
        return [x for x in self._images if x.name==image_name][0]
    def set_image(self,image_name:str,image:MISImage)->None:
        """
        Get the image for an image name.

        Parameters
        ----------
        image_name : str
            An image name.
        image : MISImage
            An image.
        
        Notes
        -----
        If `image_name` is already in images, replaces.
        If `image_name` is not in images, appends.

        """
        if image_name in self.get_image_names():
            # replace an image
            image_index=[i for i,name in enumerate(self.get_image_names()) if name==image_name][0]
            self._images[image_index]=image
        else:
            # add the image
            self._images.append(image)
    def set_images(self,images:list[MISImage])->None:
        """
        Set the list of `MISImage`.

        Overrides any existing images.
        
        Parameters
        ----------
        images : list[MISImage]
            List of images.
        """
        self._images=images
    def remove_image(self, image_name:str)->None:
        """
        Remove an image from the list of images by image name.

        Parameters
        ----------
        image_name : str
            An image name.

        Notes
        -----
        Does not modify/delete the image file.
        Does not modify/delete relations.
        """
        for name in self.get_image_names():
            if name==image_name:
                self._images.remove(self.get_image(image_name=name))
    def find_image_paths(self,mis_filepath:Path|str,update=True)->dict:
        """
        Find and optionally update all image paths.

        Checks stored location. Checks mis filepath folder for matching name.

        Parameters
        ----------
        mis_fp : Path | str,
            Filepath to MISProject, expected to be in the same folder as the image files.
        update : bool = True
            If true when a matching file is found it will replace the stored filepath with the found filepath.

        Returns
        -------
        results : dict[str,Path|None]
            Returns a dictionary of image names and either the found `Path` or `None` if no file is found.
        """
        return {image.name:image.find_image_path(mis_fp=mis_filepath,update=update) for image in self._images}

    # calibration methods
    def set_calibration(self,calibration:dict)->None:
        """
        Set the calibration.

        Parameters
        ----------
        calibration : dict[str,Any]
            calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}`
        """
        self._calibration=calibration
    def get_calibration(self)->dict:
        """
        Get the calibration.

        Returns
        -------
        calibration : dict[str,Any]
            calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}`
        """
        return self._calibration
    
    # project methods
    def set_project_path(self,mis_filepath:Path|str):
        """
        Set the path for project save file.

        Parameters
        ----------
        mis_filepath : Path | str
            `Path` or path-like string to `.mis` file
        """
        self._file_path=Path(mis_filepath)
    def get_project_path(self)->Path|None:
        """
        Get path for project save file.

        Returns
        -------
        mis_filepath : Path | None
            `Path` to `.mis` file or `None` if project does not currently have save file.
        """
        try:
            return self._file_path
        except AttributeError:
            return None
    
    # save methods
    def for_json(self):
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        mis_data : dict
            JSON dump-able representation of project information.
        """
        if self._file_path is not None:
            file_path=Path(self._file_path).as_posix()
        else:
            file_path=None
        return {**self._dict,
                "relations":[x.for_json() for x in self._relations],
                "images":[x.for_json() for x in self._images],
                "calibration":self._calibration,
                "file_path":file_path}

class MISProjectJSON(MISProject):
    """
    MISProject for JSON.
    """
    @classmethod
    def load(cls,mis_filepath)->'MISProjectJSON':
        """
        Load a MISProjectJSON from `.mis.json` file.

        Parameters
        ----------
        mis_filepath : Path | str
            `Path` or path-like string to `.mis.json` file.
        
        Returns
        -------
        loaded_project : MISProjectJSON
            MISProjectJSON initialized from the data in the `.mis.json` file.
        """
        with open(mis_filepath) as f:
            mis_data=json.load(f)
        if "relations" in mis_data.keys() and mis_data['relations'] is not None:
            mis_data["relations"]=[setup_relation(**x) for x in mis_data["relations"]]
        if "images" in mis_data.keys() and mis_data['images'] is not None:
            mis_data["images"]=[setup_image(**x) for x in mis_data['images']]
        mis_data["file_path"]=mis_filepath
        loaded_project=cls(**mis_data)
        return loaded_project
    def save(self,mis_filepath)->None:
        """
        Save the MISProjectJSON to a `.mis.json` file.

        Parameters
        ----------
        mis_filepath : Path | str
            `Path` or path-like string to `.mis.json` file.
        """
        mis_data=self.for_json()
        mis_data["file_path"]=str(mis_filepath)
        with open(mis_filepath,"w") as f:
            f.write(json.dumps(mis_data,indent=4))
    @classmethod
    def build(cls,
                mis_filepath:Path|str|None=None,
                image_filepaths:list[Path|str]|None=None,
                calibration_filepath:Path|str|None=None,
                **kwargs)->'MISProjectJSON':
        """
        Build a MISProjectJSON.

        Parameters
        ----------
        mis_filepath : Path | str | None
            `Path` or path-like string for `.mis.json` file or `None` by default.
        image_filepaths : list[Path | str] | None
            List of `Path` or path-like strings or `None` by default.
        calibration_filepath : Path | str | None
            `Path` or path-like string for `.miscal.json` file or `None` by default.
        **kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        
        Returns
        -------
        new_project : MISProjectJSON
            MISProjectJSON initialized from the provided parameters.

        Notes
        -----
        This method does not create a file, that must be done with the `save` method.
        """
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

def convert_mis_project_json(mis_fp:Path|str)->MISProjectJSON:
    """
    Convert an old `.mis` format file into a MISProjectJSON.

    Converts from pre-2.0 `.mis` style JSON files to 2.0+ style `MISProjectJSON` / `.mis.json`.

    Parameters
    ----------
    mis_fp : Path | str
        `Path` or path-like string for `.mis` file.
    
    Returns
    -------
    converted_project : MISProjectJSON
        MISProjectJSON initialized from the data in the `.mis` file.

    Notes
    -----
    This function does not create a file, that must be done with the `save` method.

    This function includes some guesses as to what the most likely structure of the `.mis` file is.
    For `.mis` that weren't modified outside MISalign it should be quite straight forward to use.
    """
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
    """
    MISProject for HDF5.
    """
    @classmethod
    def load(cls,
            mis_filepath:Path|str,
            project_hdf5path:str="MISContainer0/project",)->'MISProjectHDF5':
        """
        Load a MISProjectHDF5 from `.mis.hdf5` file.

        Parameters
        ----------
        mis_filepath : Path | str
            `Path` or path-like string to `.mis.hdf5` file.
        project_hdf5path : str
            HDF5 path to project dataset.
            Default: `"MISContainer0/project"`
        
        Returns
        -------
        loaded_project : MISProjectHDF5
            MISProjectHDF5 initialized from the data in the `.mis.hdf5` file.
        """
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
             mis_filepath : Path | str,
             project_hdf5path : str = "MISContainer0/project",
             ):
        """
        Save the MISProjectHDF5 to a `.mis.hdf5` file.

        Parameters
        ----------
        mis_filepath : Path | str
            `Path` or path-like string to a `.mis.hdf5` file.
        project_hdf5path : str
            HDF5 path for project dataset.
            Default: `"MISContainer0/project"`
        
        Notes
        -----
        HDF5 file is opened in  "`r+` Read/write, file must exist" mode so the file must exist, however new HDF5 paths can be used inside existing files.
        """
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
                # Violates Liskov Substitution Principle - I am okay with that as signficantly different build args are really needed.
            
        """
        Build a MISProjectHDF5.

        Parameters
        ----------
        mis_filepath : Path | str | None
            `Path` or path-like string for `.mis.json` file or `None` by default.
        project_hdf5path : str
            HDF5 path for project dataset.
            Default: `"MISContainer0/project"`
        images_hdf5path : str
            HDF5 path for project dataset.
            Default: `"MISContainer0/images"`
            Note: Only used if `ingest_...` parameters are used.
        ingest_image_filepaths : list[Path | str] | None
            List of `Path` or path-like strings or `None` by default.
            Images will be added to the HDF5 as datasets and added to the project as MISImageHDF5.
        include_image_filepaths : list[Path | str] | None
            List of `Path` or path-like strings or `None` by default.
            Images will be included in the project but not added as an HDF5 dataset.
        ingest_image_objects : list[MISImage] | None
            List of `MISImage` or `None` by default.
            Images will be added to the HDF5 as datasets and added to the project as MISImageHDF5.
        include_image_objects : list[MISImage] | None
            List of `MISImage` or `None` by default.
            Images will be included in the project but not added as an HDF5 dataset.
        ingest_arrays : dict[str,array-like] | None
            Dictionary of `str:array-like` or `None` by default.
            Arrays will be added to the HDF5 as datasets and added to the project as MISImageHDF5.
            Array objects need to support `numpy.asarray()`
        calibration_filepath : Path | str | None
            `Path` or path-like string for `.miscal.json` file or `None` by default.
        calibration_dict : dict | None
            calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}` or `None` by default.
        **kwargs
            `image_h5py_file_mode` h5py.File mode - Default: `'x'` Create file, fail if exists
            `image_h5py_compression` h5py.File.create_dataset kwarg - Default: `'gzip'` compression algorithm.
            `image_h5py_compression_opts` h5py.File.create_dataset kwarg - Default: `9` maximum compression.
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        
        Returns
        -------
        new_project : MISProjectHDF5
            MISProjectHDF5 initialized from the provided parameters.

        Notes
        -----
        This method, by default, will create a new file.
        To modify an existing file `image_h5py_file_mode` kwarg must be prodivided.
        Building a MISProjectHDF5 without an actual HDF5 file is not currently implemented.
        """
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