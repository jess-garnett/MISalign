"""
Manual Alignment Module
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image as PILImage
from PIL import ImageTk
from ..model.project import Project
from ..model.offset import Offset
from ..model.image import Image

def ReturnProject(): pass

class ManualAlignWindow(tk.Toplevel):
    def __init__(self,parent,project,a:str,b:str,return_project : ReturnProject = None):
        super().__init__(parent)
        self.parent=parent
        self.return_project:ReturnProject = return_project
        self.project:Project = project
        self.a : str = a
        self.b : str = b
        self.offset = None
        self.otherframe=tk.Frame(self)
        self.otherframe.grid()
        self.otherlabel=tk.Label(self.otherframe,text="other label")
        self.otherlabel.grid()
        self.compare_frame=CompareFrame(parent=self,
            imga=self.project.images[self.a].image,
            imgb=self.project.images[self.b].image,
            offset_callback=self.update_offset
            )
        self.compare_frame.grid(row=0,column=0)
        self.controls_frame=ControlsFrame(self)
        self.controls_frame.grid(row=0,column=1)
    def update_compare(self,a,b):#can be called by the window level above it to update what is being compared
        self.a=a
        self.b=b
        self.controls_frame.reset_a_b()
        self.compare_frame.grid_forget() #would rather do this as an update method rather than this way.
        self.compare_frame=CompareFrame(self,
            imga=self.project.images[self.a].image,
            imgb=self.project.images[self.b].image,
            offset_callback=self.update_offset
            )
        self.compare_frame.grid(row=0,column=0)
    def update_offset(self,new_offset:tuple):
        self.offset=new_offset
        self.controls_frame.update_current_offset_label(new_offset=new_offset)
    def save_offset(self):
        self.project.update_offsets({self.b:[self.a,self.offset,0.0]})
    def close(self):
        self.destroy()
        self.update()

    
class CompareFrame(tk.Frame):
    def __init__(self,parent,imga:PILImage = None,imgb:PILImage = None,offset_callback=None):
        super().__init__(parent)
        self.offset_callback=offset_callback
        # imga.show()
        # imgb.show()
        self.a_scale=2.5 #will want to handle scaling better in the future - 640*2.5=1600
        self.b_scale=2.5
        imga_tk = ImageTk.PhotoImage(image=imga.resize((640,480)))
        imgb_tk = ImageTk.PhotoImage(image=imgb.resize((640,480)))
        a=tk.Label(self,image=imga_tk)
        a.image=imga_tk
        a.grid(row=0,column=0)
        a.bind("<Button 1>",self.click_a)
        b=tk.Label(self,image=imgb_tk)
        b.image=imgb_tk
        b.grid(row=1,column=0)
        b.bind("<Button 1>",self.click_b)
        self.a_coords=[]
        self.b_coords=[]
    def click_a(self,event):
        self.a_coords.append((self.a_scale*event.x,self.a_scale*event.y))
        self.update_offset()
    def click_b(self,event):
        self.b_coords.append((self.b_scale*event.x,self.b_scale*event.y))
        self.update_offset()
    def update_offset(self):
        x_offset = 0
        y_offset = 0
        if len(self.a_coords)==len(self.b_coords):
            for a_coord in self.a_coords:
                x_offset+=a_coord[0]
                y_offset+=a_coord[1]
            for b_coord in self.b_coords:
                x_offset-=b_coord[0]
                y_offset-=b_coord[1]
            self.offset_callback((int(x_offset/len(self.a_coords)),int(y_offset/len(self.a_coords))))
    
class ControlsFrame(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent:ManualAlignWindow = parent
        self.text_a=tk.StringVar()
        self.text_a.set(self.parent.a)
        label_a=ttk.Label(self,textvariable=self.text_a)
        label_a.grid()

        self.text_b=tk.StringVar()
        self.text_b.set(self.parent.b)
        label_b=ttk.Label(self,textvariable=self.text_b)
        label_b.grid()

        self.text_saved_offset=tk.StringVar()
        self.text_saved_offset.set(self.find_saved_offset())

        self.label_saved_offset=ttk.Label(self,textvariable=self.text_saved_offset)
        self.label_saved_offset.grid()

        self.current_offset=tk.StringVar()
        self.current_offset.set("No Offset")

        self.label_current_offset=ttk.Label(self,textvariable=self.current_offset)
        self.label_current_offset.grid()

        button_save = ttk.Button(self,text="Save",command=self.click_save_offset)
        button_save.grid()

        button_reset = ttk.Button(self,text="Reset",command=self.click_reset_offset)
        button_reset.grid()
        #Displays currently compared images, previous offset, current coordinate pairs, current offset, and buttons for interacting/selecting new.
        button_next=ttk.Button(self,text="Next Pair",command=self.click_next)
        button_next.grid()

        self.image_keys=list(self.parent.project.images.keys())
        self.image_keys.sort() #brings them to alphaneumeric order
        self.combobox_a=ttk.Combobox(self,values=self.image_keys)
        self.combobox_a.current(self.image_keys.index(self.parent.a))
        self.combobox_a.grid()
        self.combobox_b=ttk.Combobox(self,values=self.image_keys)
        self.combobox_b.grid()
        self.combobox_b.current(self.image_keys.index(self.parent.b))

        button_update=ttk.Button(self,text="Update",command=self.click_update_select)
        button_update.grid()

        button_end=ttk.Button(self,text="End & Close",command=self.click_end_alignment)
        button_end.grid()


    def click_save_offset(self):
        self.parent.save_offset()
        self.text_saved_offset.set(self.find_saved_offset())
    def click_reset_offset(self):
        self.update_current_offset_label()#running w/ no params will reset label
        self.parent.offset=None #resets the offset variable
        self.parent.compare_frame.a_coords=[] #resets the click lists
        self.parent.compare_frame.b_coords=[]
    def reset_a_b(self):
        self.click_reset_offset()
        self.text_a.set(self.parent.a)
        self.text_b.set(self.parent.b)
        self.text_saved_offset.set(self.find_saved_offset())
    def find_saved_offset(self):
        try:
            offset_a=self.parent.project.offsets[self.parent.a].get_ref()
            offset_b=self.parent.project.offsets[self.parent.b].get_ref()
        except KeyError:
            return "No Saved Offset"    
        if offset_a==self.parent.b:
            x=self.parent.project.offsets[self.parent.a].get_x()
            y=self.parent.project.offsets[self.parent.a].get_y()
            rect=(-x,-y)
            return "Saved Offset: "+str(rect)
        elif offset_b==self.parent.a:
            return "Saved Offset: "+str(self.parent.project.offsets[self.parent.b].get_rect())
        else:
            return "No Saved Offset"
    def update_current_offset_label(self,new_offset:tuple = None):
        if new_offset is not None:
            self.current_offset.set("Current Offset: "+str(new_offset))
        else:
            self.current_offset.set("No Offset")
    def click_next(self):
        if self.image_keys.index(self.parent.b)!=len(self.image_keys)-1:
            self.parent.update_compare(self.image_keys[self.image_keys.index(self.parent.a)+1],self.image_keys[self.image_keys.index(self.parent.b)+1])
    def click_update_select(self):
        select_a=self.combobox_a.get()
        select_b=self.combobox_b.get()
        not_empty=select_a!="" and select_b!=""
        not_same=select_a!=select_b
        if not_empty and not_same:
            self.parent.update_compare(a=select_a,b=select_b)
    def click_end_alignment(self):
        self.parent.return_project(self.parent.project)
        self.parent.close()