from sys import path
from os.path import dirname, realpath, abspath
current = dirname(realpath(__file__))
parent = dirname(current)
path.append(parent)


import model.project as m_proj
import service.project_file as s_proj_file
import gui.alignment as g_align
import service.canvas as s_canvas

import tkinter as tk
from tkinter.filedialog import asksaveasfilename


def setupMIS(mis_fp):
    cal=None
    img_list=[
        "a_myimages1.jpg",
        "a_myimages2.jpg",
        "a_myimages3.jpg",
        "a_myimages4.jpg",
        "a_myimages5.jpg",
        "a_myimages6.jpg",
        "a_myimages7.jpg",
        "a_myimages8.jpg"
    ]
    default_offset=[img_list[0],[0,0],0.0]
    img_names=dict()
    for img in img_list:
        img_names[img]=default_offset
    new_project=m_proj.Project(mis_fp,cal,img_names)
    s_proj_file.save_to_mis(mis_filepath=mis_fp,project=new_project)
def expandMIS(mis_fp):
    project:m_proj.Project=s_proj_file.load_from_mis(mis_filepath=mis_fp)
    new_img_names={
            "a_myimages9.jpg": ["a_myimages8.jpg",[0,0],0.0],
            "a_myimages10.jpg": ["a_myimages9.jpg",[0,0],0.0]
        }
    project.images.update(new_img_names) #currently adds new ones without the offset
    s_proj_file.save_to_mis(mis_filepath=mis_fp,project=project)
def manAlign(mis_fp):
    #Purpose: run manual alignment
    project:m_proj.Project=s_proj_file.load_from_mis(mis_filepath=mis_fp)

    root=tk.Tk()
    root.title("root")
    manualalignment=g_align.ManualAlignWindow(root,project,"a_myimages1.jpg","a_myimages2.jpg",return_project=saveManAlign)
    root.mainloop()
def saveManAlign(save_project:m_proj.Project):
    #purpose: Callback function saving the manual alignment results.
    s_proj_file.save_to_mis(mis_filepath=mis_fp,project=save_project) #uses global mis fp
def roughCanvas(mis_fp):
    project:m_proj.Project=s_proj_file.load_from_mis(mis_filepath=mis_fp)
    roughcanvas=s_canvas.Canvas(project=project)
    # save_fp=asksaveasfilename()
    # roughcanvas.canvas_image().save(fp=save_fp)
    roughcanvas.canvas_image().show()
def blendCanvas(mis_fp):
    project:m_proj.Project=s_proj_file.load_from_mis(mis_filepath=mis_fp)
    roughcanvas=s_canvas.Canvas(project=project)
    roughcanvas.blended_image().show()
    save_fp=asksaveasfilename()
    roughcanvas.blended_image().save(fp=save_fp)

def labelCanvas(mis_fp):
    project:m_proj.Project=s_proj_file.load_from_mis(mis_filepath=mis_fp)
    roughcanvas=s_canvas.Canvas(project=project)
    # save_fp=asksaveasfilename()
    # roughcanvas.mark(list(project.images.keys())).save(fp=save_fp)
    roughcanvas.mark(list(project.images.keys())).show()
def correct_offsets(mis_fp):
    #Convert from 1600x1200 offset to 800x600 offset
    project:m_proj.Project=s_proj_file.load_from_mis(mis_filepath=mis_fp)
    for off in project.offsets:
        x=int(project.offsets[off].get_x()/2)
        y=int(project.offsets[off].get_y()/2)
        project.offsets[off].set_rect([x,y])
    s_proj_file.save_to_mis(mis_filepath=mis_fp,project=project)
    

if __name__=="__main__":
    global mis_fp
    example_data="./data/a_myproject_4.mis"
    example_data_2="./data/a_myproject_4.mis"
    mis_fp = abspath(example_data)
    # setupMIS(mis_fp) #setup mis project for the first time
    # expandMIS(mis_fp) #add additional images
    # manAlign(mis_fp) #do manual alignment
    roughCanvas(mis_fp)
    blendCanvas(mis_fp)
    # labelCanvas(mis_fp)
    # correct_offsets(mis_fp=mis_fp)


    pass