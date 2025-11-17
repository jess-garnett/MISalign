"""MIS Project Module
- MIS Projects contain information about a set of images, relations, and a calibration.
- Implements a ProjectJSON which contains image filepath, relations description, and calibration and can be saved to/loaded from JSON.
"""

from typing import Protocol, runtime_checkable
from MISalign.model.relation import MISRelation, setup_relation
from MISalign.model.image import MISImage, MISImageFile,setup_image
from MISalign.calibration.calibrate import calibration_from_json
import json
from os.path import split, isfile, join
from pathlib import Path

@runtime_checkable
class MISProject(Protocol):
    """Contains information about a set of images, relations, and a calibration"""
    def __str__(self)->str:
        ...

    # relation methods
    def get_relations(self)->list[MISRelation]:
        """Get the list of relations."""
        ...
    def set_relations(self,relations:list[MISRelation]):
        """Set the list of relations."""
        ...
    def set_relation(self,relation_index:int,relation:MISRelation):
        """Set a specific relation based on its index in the list of relations.
        - Replaces existing relation."""
        ...
    def index_relation(self,relation:MISRelation)->int:
        """Get the index of a relation."""
        ...
    def add_relation(self,relation:MISRelation)->int:
        """Append a relation to the list of relations and return it's index."""
        ...
    def remove_relation(self,relation:MISRelation):
        """Remove a relation from the list of relations."""
        ...
    def find_relations(self,image_name:str)->list[MISRelation]:
        """Find all relations which include a specific image."""
        ...
    def rename_image_relations(self, old_image_name:str,new_image_name:str):
        """Rename an image in all relations.
        - Does not modify images."""
        ...
    
    # image methods
    def get_image_names(self)->list[str]:
        """Get the list of image names."""
        ...
    def get_image(self,image_name:str)->MISImage:
        """Get the image for an image name."""
        ...
    def set_image(self,image_name:str,image:MISImage):
        """Set the image for an image name."""
        ...
    def remove_image(self, image_name:str):
        """Remove the image for an image name.
        - Does not modify/delete relations."""
        ...

    # calibration methods
    def set_calibration(self,calibration:dict):
        """Set the calibration."""
        ...
    def get_calibration(self)->dict:
        """Get the calibration."""
        ...
    
    # project methods
    def set_project_path(self,project_file_path:str|Path):
        """Set path for project save file."""
        ...
    def get_project_path(self)->Path|None:
        """Get path for project save file.
        - Returns `None` if project does not currently have save file."""
        ...

class MISProjectJSON():
    """MISProject compatible with loading from/saving to JSON. Contains:
    - Image Filepaths
    - Relations
    - Calibration
    """
    def __init__(self,**mis_data):
        self._dict=mis_data
        if 'images' in mis_data:
            self._images:list[MISImage]=mis_data['images']#list of image objects
        else:
            self._images:list[MISImage]=list()
        
        if 'relations' in mis_data:
            self._relations:list[MISRelation]=mis_data['relations']#list of relation objects
        else:
            self._relations:list[MISRelation]=list()

        if 'calibration' in mis_data:
            self._calibration:dict=mis_data['calibration']#dictionary with 'pixel', 'length', and 'length_unit'
        else:
            self._calibration:dict=dict()
        
        if "file_path" in mis_data:
            self._file_path=Path(mis_data['file_path'])

    def __str__(self)->str:
        if len(self._images)==0 and len(self._relations)==0 and len(self._calibration)==0 and self.get_project_path()==None:
            return "An empty MISalign project."
        else:
            return "A MISalign project with:\n"+"\n".join([
                "Images:\n"+"\n".join(["    "+x for x in self.get_image_names()]),
                "Relations:\n"+"\n".join(["    "+str(x.get_reference()) for x in self._relations]),
                "Calibration:\n"+"\n".join([f"    {key} : {value}" for key,value in self._calibration.items()]),
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
                relation_data=r.save_dict()
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
        """Set the image for an image name."""
        for i,name in enumerate(self.get_image_names()):
            if image_name==name:
                self._images[i]=image
    def remove_image(self, image_name:str):
        """Remove the image for an image name.
        - Does not modify/delete the image file.
        - Does not modify/delete relations."""
        for name in self.get_image_names():
            if name==image_name:
                self._images.remove(self.get_image(image_name=name))


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
        except:
            return None

    # JSON/ImageFile specific - image checking methods
    def get_image_paths(self):
        return {x.name:x.image_filepath for x in self._images if isinstance(x,MISImageFile)} #takes tail of image filepath
    def check_image_paths(self):
        return {n:isfile(p) for n,p in self.get_image_paths().items()}
        #TODO add correction/relocation capability to this function/additional function.
    def find_image_paths(self,mis_fp,update=True,find_all=False):
        all_image_names=self.get_image_names()
        if find_all:
            find_list=all_image_names
        else:
            find_list=[name for name,found in self.check_image_paths().items() if not found]
        mis_head=split(mis_fp)[0]
        find_search={name:{
                            "found":isfile(join(mis_head,name)),
                            "path":join(mis_head,name)}
                     for name in find_list}
        if update:
            for name in find_list:
                if find_search[name]["found"]:
                    image_data=self.get_image(name).save_dict()
                    image_data["image_filepath"]=find_search[name]["path"]
                    self.set_image(
                        image_name=name,
                        image=setup_image(**image_data))
        return find_search
    
    # JSON specific - save methods
    def save_dict(self):
        try:
            file_path=str(self._file_path)
        except:
            file_path=None
        return {**self._dict,
                "relations":[x.save_dict() for x in self._relations],
                "images":[x.save_dict() for x in self._images],
                "calibration":self._calibration,
                "file_path":file_path}
    

def load_mis_project_json(mis_fp) -> MISProjectJSON:
    with open(mis_fp) as infile:
        mis_object = json.load(infile)
    if "relations" in mis_object.keys() and mis_object['relations'] is not None:
        mis_object["relations"]=[setup_relation(**x) for x in mis_object["relations"]]
    if "images" in mis_object.keys() and mis_object['images'] is not None:
        mis_object["images"]=[MISImageFile(**x) for x in mis_object['images']]
    mis_object["file_path"]=mis_fp
    return MISProjectJSON(**mis_object)

def build_mis_project_json(
        image_filepaths:list[str],
        calibration_filepath:str|None=None,
        project_filepath:str|None=None,
    )->MISProjectJSON:
    mis_kwargs=dict()
    mis_kwargs["images"]=[MISImageFile(image_filepath=image_filepath) for image_filepath in image_filepaths]
    if calibration_filepath is not None:
        mis_kwargs["calibration"]=calibration_from_json(calibration_filepath)
    if project_filepath is not None:
        mis_kwargs["file_path"]=project_filepath
    return MISProjectJSON(**mis_kwargs)



def save_mis_project_json(mis_fp,misfile:MISProjectJSON) -> None:
    mis_save=misfile.save_dict()
    json_object=json.dumps(mis_save,indent=4)
    with open(mis_fp,"w") as outfile:
        outfile.write(json_object)

def convert_mis_project_json(mis_fp)->MISProjectJSON:
    """Convert an old `.mis` format file into a MISProjectJSON."""
    with open(mis_fp) as infile:
        mis_load = json.load(infile)
    mp=build_mis_project_json(
        image_filepaths=mis_load["image_fps"],
        )
    build_relations=list()
    for x in mis_load["relations"]:
        try:
            if type(x[2][0])==int: # relation data is most likely rectangular offset
                relation_data=dict(rectangular=x[2])
            else: #relation data is most likely points
                relation_data=dict(points=x[2])
        except: # relation data is most likely None
            relation_data=dict()
        build_relations.append(setup_relation(
                image_pair=x[0],
                relation_type=x[1],
                **relation_data))
    mp.set_relations(build_relations)
    return mp