""" Mis File Model
- Holds image models and relation models
- Has associated helper functions for load/save
- Store as json
"""
import json
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
            self.image_fps=None
        
        if 'relations' in mis_data:
            self._relations=mis_data['relations']#list of relation objects
        else:
            self._relations=None


        if 'calibration' in mis_data:
            self.calibration=mis_data['calibration']#dictionary with 'value' and 'units'
        else:
            self.calibration=None
    def __str__(self):
        if self.image_fps is None and self._relations is None:
            return "An empty MISalign project."
        else:
            return "A MISalign project with:"+str([self.image_fps,self.get_rels(),self.calibration])
    
    def get_rels(self,relation=None):
        if self._relations is None:
            return None
        elif relation is None:
            return [x.get_rel() for x in self._relations]
        else:
            return [[x.get_rel(),x.get_rel(relation)] for x in self._relations]
    def save_rels(self):
        if self._relations is None:
            return None
        else:
            return [x.save_rel() for x in self._relations]



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