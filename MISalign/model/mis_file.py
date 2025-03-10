""" Mis File Model
- Holds image models and relation models
- Has associated helper functions for load/save
- Store as json
"""
import json
from os.path import split, isfile, join
from MISalign.model.relation import Relation

class MisFile():
    """Stores all the information about a set of images
    -Image filepaths
    -Relation objects
    -Calibration information
    """
    def __init__(self,**mis_data):
        if 'image_fps' in mis_data:
            self.image_fps=mis_data['image_fps']#list of filepaths
        else:
            self.image_fps=list()
        
        if 'relations' in mis_data:
            self._relations=mis_data['relations']#list of relation objects
        else:
            self._relations=list()


        if 'calibration' in mis_data:
            self.calibration=mis_data['calibration']#dictionary with 'pixel', 'length', and 'length_unit'
        else:
            self.calibration=dict()
        if 'calibration_fp' in mis_data:
            if mis_data['calibration_fp'] is not None:
                with open(mis_data['calibration_fp']) as infile:
                    self.calibration = json.load(infile)#dictionary with 'pixel', 'length', and 'length_unit'
    def __str__(self):
        if len(self.image_fps)==0 and len(self._relations)==0:
            return "An empty MISalign project."
        else:
            return "A MISalign project with:"+str([self.image_fps,self.get_rels(),self.calibration])
    
    def get_rels(self,relation=None):
        if self._relations is []:
            return []
        elif relation is None:
            return [x.get_rel() for x in self._relations]
        else:
            return [[x.get_rel(),x.get_rel(relation)] for x in self._relations]
    def save_rels(self):
        if self._relations is None:
            return None
        else:
            return [x.save_rel() for x in self._relations]
    def find_all_rel(self,name):
        return [[x.ref,x._relation] for x in self._relations if name in x.ref]
    
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


def load_mis(mis_fp) -> MisFile:
    with open(mis_fp) as infile:
        mis_object = json.load(infile)
    if "relations" in mis_object.keys() and mis_object['relations'] is not None:
        mis_object["relations"]=[Relation(x[0][0],x[0][1],x[1],x[2]) for x in mis_object["relations"]]
    return MisFile(**mis_object)
def save_mis(mis_fp,misfile:MisFile) -> None:
    mis_save=dict()
    mis_save["image_fps"]=misfile.image_fps
    mis_save["relations"]=misfile.save_rels()
    mis_save["calibration"]=misfile.calibration
    json_object=json.dumps(mis_save,indent=4)
    with open(mis_fp,"w") as outfile:
        outfile.write(json_object)