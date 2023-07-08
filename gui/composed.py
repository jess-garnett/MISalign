"""Assorted gui elements that are intended to be re-used across multiple areas"""
import tkinter as tk
from tkinter import ttk


class ButtonGrid():
    def __init__(self,frame_kwargs,bg_kwargs,**kwargs):
        #kwargs contain optional grid configurations dictionaries
        self.init_frame(frame_kwargs)
        self.init_buttons(bg_kwargs)
    
    def init_frame(self,kwargs):
        self.frame=ttk.Frame(**kwargs)
    
    def init_buttons(self,bg_kwargs:dict[str,dict]):
        self.buttons:dict[str,ttk.Button] = dict()
        for button_key in bg_kwargs:
            bg_kwargs[button_key]['master']=self.frame
            self.buttons[button_key]=ttk.Button(**bg_kwargs[button_key])
    
    def button_grid(self,ordered_list,kwargs:dict = dict()):
        for button_key in ordered_list:
            if kwargs.get(button_key,None) is None:
                self.buttons[button_key].grid()
            else:
                self.buttons[button_key].grid(**kwargs.get(button_key))

    # def _build_button(self,button_kwargs:dict)->ttk.Button:
    #     """Pass a dict of button configurations, will return new button"""
    #     return ttk.Button(**button_kwargs)
    def config_buttons(self,button_configs: dict[str,dict])->None:
        """Pass a dict of button_keys:button_configs, will config each one"""
        for button_key in button_configs:
            self.config_button(button_key,button_configs[button_key])
    def config_button(self,button_key,button_config:dict)->None:
        """Pass a button key and a set of configurations, will config the button"""
        for config_key in button_config:
            self.buttons[button_key][config_key]=button_config[config_key]