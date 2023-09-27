import json
import pprint
from .project import Project

def save_to_mis(mis_filepath:str,project:Project) -> Project:
    project_save=dict()
    project_save["name"]=project.name
    project_save["calibration"]=project.cal
    project_save["image:offset"]=project.get_image_offset_pairs()
    json_object=json.dumps(project_save,indent=4)
    with open(mis_filepath,"w") as outfile:
        outfile.write(json_object)

def load_from_mis(mis_filepath:str) -> Project:
    with open(mis_filepath) as infile:
        json_object = json.load(infile)
    calibration=json_object["calibration"]
    img_off_pairs=dict()
    for key in json_object["image:offset"]:
            img_off_pairs[key]=json_object["image:offset"][key]
    loaded_project=Project(mis_filepath,calibration,img_off_pairs)
    return loaded_project
