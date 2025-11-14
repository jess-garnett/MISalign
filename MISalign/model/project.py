"""MIS Project Module
- MIS Projects contain information about a set of images, relations, and a calibration.
- Implements a ProjectJSON which contains image filepath, relations description, and calibration and can be saved to/loaded from JSON.
"""

from typing import Protocol, runtime_checkable
from MISalign.model.relation import MISRelation, setup_relation
from MISalign.model.image import MISImage
import json
from os.path import split, isfile, join
from pathlib import Path

@runtime_checkable
class MISProject(Protocol):
    """Contains information about a set of images, relations, and a calibration"""
    def __str__(self)->str:
        ...

    def get_relations(self)->list[MISRelation]:
        ...
    def set_relations(self,relations:list[MISRelation]):
        ...
    def set_relation(self,relation_index:int,relation:MISRelation):
        ...
    def index_relation(self,relation:MISRelation)->int:
        ...
    def add_relation(self,relation:MISRelation):
        ...
    def del_relation(self,relation:MISRelation):
        ...
    def find_relations(self,image_name:str)->list[MISRelation]:
        ...
    
    def get_image_names(self)->list[str]:
        ...
    def get_image(self,image_name:str)->MISImage:
        ...
    def set_image(self,image_name:str,image:MISImage):
        ...
    def del_image(self, image_name:str):
        ...
    def rename_image(self, old_image_name:str,new_image_name:str):
        ...
    
    def set_project_path(self,project_file_path:str|Path):
        ...
    def get_project_path(self)->Path:
        ...

class MISProjectJSON():
    """MISProject compatible with loading from/saving to JSON. Contains:
    - Image Filepaths
    - Relation Objects
    - Calibration Information
    """
    def __init__(self,**mis_data):
        if 'image_fps' in mis_data:
            self.image_fps:list[str]=mis_data['image_fps']#list of filepaths
        else:
            self.image_fps:list[str]=list()
        
        if 'relations' in mis_data:
            self._relations:list[MISRelation]=mis_data['relations']#list of relation objects
        else:
            self._relations:list[MISRelation]=list()

        if 'calibration' in mis_data:
            self.calibration:dict=mis_data['calibration']#dictionary with 'pixel', 'length', and 'length_unit'
        elif 'calibration_fp' in mis_data:
            if mis_data['calibration_fp'] is not None:
                with open(mis_data['calibration_fp']) as infile:
                    self.calibration:dict = json.load(infile)#dictionary with 'pixel', 'length', and 'length_unit'
        else:
            self.calibration:dict=dict()
    def __str__(self):
        if len(self.image_fps)==0 and len(self._relations)==0:
            return "An empty MISalign project."
        else:
            return "A MISalign project with:"+str([self.image_fps,[x.get_reference() for x in self._relations],self.calibration])
        
    def get_relations(self):
        return self._relations
    
    def set_relations(self,relations:list[MISRelation]):
        ...
    def set_relation(self,relation_index,relation:MISRelation):
        ...
    def index_relation(self,relation:MISRelation)->int:
        ...
    def add_relation(self,relation:MISRelation):
        ...
    def del_relation(self,relation:MISRelation):
        ...

    def save_relations(self):
        return [x.save_relation() for x in self._relations]
    
    def find_all_rel(self,name):
        return [x for x in self._relations if name in x.get_reference()]
    
    def get_image_names(self):
        return [split(image_filepath)[1] for image_filepath in self.image_fps] #takes tail of image filepath
    def get_image_paths(self):
        return {n:p for n,p in zip(self.get_image_names(),self.image_fps)} #takes tail of image filepath
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
        find_search={name:{"found":isfile(join(mis_head,name)),"path":join(mis_head,name)} for name in find_list}
        if update:
            for name in find_list:
                if find_search[name]["found"]:
                    self.image_fps[all_image_names.index(name)]=find_search[name]["path"]
        return find_search
    

def load_mis_project_json(mis_fp) -> MISProjectJSON:
    with open(mis_fp) as infile:
        mis_object = json.load(infile)
    if "relations" in mis_object.keys() and mis_object['relations'] is not None:
        mis_object["relations"]=[setup_relation(x[0],x[1],x[2]) for x in mis_object["relations"]]
    return MISProjectJSON(**mis_object)
def save_mis_project_json(mis_fp,misfile:MISProjectJSON) -> None:
    mis_save=dict()
    mis_save["image_fps"]=misfile.image_fps
    mis_save["relations"]=misfile.save_relations()
    mis_save["calibration"]=misfile.calibration
    json_object=json.dumps(mis_save,indent=4)
    with open(mis_fp,"w") as outfile:
        outfile.write(json_object)