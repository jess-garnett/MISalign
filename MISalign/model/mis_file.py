""" Mis File Model
- Holds image models and relation models
- Has associated helper functions for load/save
- Store as json
"""

class MisFile():
    def __init__(self,**mis_data):
        if 'image_fps' in mis_data:
            self._image_fps=mis_data['image_fps']#list of filepaths
        else:
            self._image_fps=None
        
        if 'relations' in mis_data:
            self._relations=mis_data['relations']#list of relation objects
        else:
            self._relations=None


        if 'calibration' in mis_data:
            self.calibration=mis_data['calibration']#dictionary with 'value' and 'units'
        else:
            self.calibration=None
    def __str__(self):
        if self._image_fps is None and self._relations is None:
            return "An empty MISalign project."
        else:
            return "A MISalign project with:"+str([self._image_fps,self.get_rels(),self.calibration])
    
    def get_rels(self):
        if self._relations is None:
            return None
        else:
            return [x.get_rel() for x in self._relations]
        
def load_mis(mis_fp) -> MisFile:
    pass
def save_mis(mis_fp,misfile:MisFile) -> None:
    pass