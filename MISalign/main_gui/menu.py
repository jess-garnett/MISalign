import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .composed import ButtonGrid
from ..model.project import Project
from ..model.project_service import load_from_mis, save_to_mis
from typing import Union
from os import getcwd
from copy import deepcopy

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        #setup button grid parameters
        self.project_label=ttk.Label(self,text="Project: None",padding=[0,10,0,0])
        self.project_label.grid()
        bg_frame_kwargs={
            'master':self,
            'padding':10
        }
        bg_bg_kwargs={
            "set":{"text":"Setup","command":self.setup},
            "ali":{"text":"Alignment","command":self.alignment},
            "cal":{"text":"Calibration","command":self.calibration},
            "ren":{"text":"Render","command":self.render},
            "adv":{"text":"Advanced","command":self.advanced},
            "ope":{"text":"Open","command":self.open},
            "sav":{"text":"Save","command":self.save},
            "saa":{"text":"Save As","command":self.save_as},
            "clo":{"text":"Close","command":self.close}
        }
        self.menu_bg=ButtonGrid(
            frame_kwargs=bg_frame_kwargs,
            bg_kwargs=bg_bg_kwargs
        )
        self.menu_bg.frame.grid()
        self.menu_bg.button_grid(["set","ali","cal","ren","adv","ope","sav","saa","clo"])
        #setup project
        self.current_project:Project = None #create the variable
        self.update_project(None) #run the update function to configure the menu state correctly.
            #must happen after initializing gui elements that are affected by self.update_project()
        self.project_saved=False

        self.mainloop()

#button press methods
    def setup(self):
        #TODO actually implement
        self.buttons_win_open()
        self.window=tk.Toplevel(self)
        self.window.winbutton=ttk.Button(self.window,text="Callback",command=self.setup_callback)
        self.window.winbutton.grid()
        # deepcopy(self.current_project)
    def setup_callback(self):
        #TODO actually implement
        self.project_saved=False
        self.label_project_unsaved()
        self.buttons_win_close()
    def alignment(self):
        #TODO actually implement
        pass
    def alignment_callback(self):
        #TODO actually implement
        pass
    def calibration(self):
        #TODO actually implement
        pass
    def calibration_callback(self):
        #TODO actually implement
        pass
    def render(self):
        #TODO actually implement
        pass
    def render_callback(self):
        #TODO actually implement
        pass
    def advanced(self):
        #TODO Decide what goes here
        pass
    def advanced_callback(self):
        #TODO actually implement
        pass
    def open(self):
        self.buttons_win_open()
        want_save=self.check_save()
        if want_save is True:
            self.save()
        elif want_save is None:
            self.buttons_win_close()
            return #if cancelled do nothing
        new_filepath=filedialog.askopenfilename(initialdir=getcwd(),filetypes=[("MISaligned Project", "*.mis")])
        if new_filepath=='':
            self.buttons_win_close() #open was cancelled, change nothing.
        else:
            self.project_saved=True
            self.update_project(load_from_mis(new_filepath))#includes reseting buttons/labels
    def save(self):
        save_to_mis(self.current_project.filepath,self.current_project)
        self.project_saved=True
        self.label_project_saved()
    def save_as(self):
        self.buttons_win_open()
        new_filepath=filedialog.asksaveasfilename(initialdir=self.current_project.folder,defaultextension=".mis",filetypes=[("MISaligned Project", "*.mis")])
        if new_filepath == '':
            self.buttons_win_close() #save as was cancelled, change nothing.
        else:
            self.current_project.update_mis_filepath(new_filepath)
            save_to_mis(self.current_project.filepath,self.current_project)
            self.project_saved=True
            self.label_project_saved()
    def close(self):
        want_save=self.check_save()
        if want_save is True:
            self.save()
            self.destroy()
        elif want_save is False:
            self.destroy()
        else:
            pass #if cancelled do nothing

    def check_save(self):
        if self.project_saved==False and self.current_project is not None:
            want_save=messagebox.askyesnocancel(title="Save Current Project", message="Do you want to save the current file?")
            #True if yes to saving, False if no to saving(but still continue w/ operations), None if cancelled or closed with the X i.e. don't do the thing.
            return want_save
        else:
            return False #if the project exists but is already saved or if it doesn't exist

            

#data handling methods
    def update_project(self,new_project:Union[Project,None]):
        if new_project is None:
            self.current_project = None
            self.buttons_no_project()
            self.label_no_project()
        elif isinstance(new_project,Project):
            self.current_project = new_project
            self.buttons_project()
            if self.project_saved==True:
                self.label_project_saved()
            else:
                self.label_project_unsaved()
            

#view state functions functions
    def buttons_no_project(self):
        e={"state":"enabled"}
        d={"state":"disabled"}
        button_configs = {
            "set":e,
            "ali":d,
            "cal":d,
            "ren":d,
            "adv":e,
            "ope":e,
            "sav":d,
            "saa":d,
            "clo":e
        }
        self.menu_bg.config_buttons(button_configs)
    def buttons_project(self):
        e={"state":"enabled"}
        # d={"state":"disabled"}
        button_configs = {
            "set":e,
            "ali":e,
            "cal":e,
            "ren":e,
            "adv":e,
            "ope":e,
            "sav":e,
            "saa":e,
            "clo":e
        }
        self.menu_bg.config_buttons(button_configs)
    def buttons_win_open(self):
        e={"state":"enabled"}
        d={"state":"disabled"}
        button_configs = {
            "set":d,
            "ali":d,
            "cal":d,
            "ren":d,
            "adv":e,
            "ope":d,
            "sav":d,
            "saa":d,
            "clo":e
        }
        self.menu_bg.config_buttons(button_configs)
    def buttons_win_close(self):
        if self.current_project is None:
            self.buttons_no_project()
        else:
            self.buttons_project()
    
    def label_no_project(self):
        self.project_label["text"]="Project: None"
    def label_project_saved(self):
        self.project_label["text"]="Project: " +self.current_project.name
    def label_project_unsaved(self):
        self.project_label["text"]="Project: " +self.current_project.name+"*"


#
        # Template for button config
        # button_configs = {
        #     "set",
        #     "ali",
        #     "cal",
        #     "ren",
        #     "adv",
        #     "ope",
        #     "sav",
        #     "saa",
        #     "clo"
        # }