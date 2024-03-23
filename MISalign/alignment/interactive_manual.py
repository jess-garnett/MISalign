"""
Interactive Matplotlib Manual Relation Module
"""
# Built around PyQt5 interface due to need for plt.ginput()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

from MISalign.model.relation import Relation
from MISalign.model.image import Image

class InteractiveManualRelation():
    """Allows user to manually specify relation between two images using interactive matplotlib interface."""
    def __init__(self):
        self._fig=plt.figure()
        self._ax=self._fig.subplots()
        self.points=None
        plt.show()
    def plot_clear(self):
        """Clears current IMR figure"""
        self._ax.clear()
        self.points=None
        #TODO
    def plot_points(self):
        """Plots the points of the current relation"""
        for pop in self.points:
            self._ax.plot([pop[0][0],pop[1][0]],[pop[0][1],pop[1][1]+self._height],"x:")
    def change_images(self,imga:Image,imgb:Image):
        """Replaces image in IMR figure"""
        self._imga=imga
        self._imgb=imgb
        self._height=imga.size[1]
        self.plot_clear()
        self._img_ax=self._ax.imshow(np.vstack([imga._img,imgb._img]))
    def manual(self):
        """Gets user input points from figure"""
        input_points=self._fig.ginput(7)
        rel_pts=[[],[]]
        for x,y in input_points:
            if y<self._height:
                rel_pts[0].append((x,y))
            else:
                rel_pts[1].append((x,y-self._height))
        if len(rel_pts[0]) == len(rel_pts[1]):
            self.points=[(a,b) for a,b in zip(rel_pts[0],rel_pts[1])]#convert from list of x,y sorted by image to pairs of x,y pairs
        else:
            raise ValueError("Mismatched number of selected points.")
    def manual_gen(self): #generalized using button widget so it can run on any interactive GUI.
        """Gets user input points from figure"""
        self._click_button=Button(self._ax,label="")
        self._click_button_event=self._click_button.on_clicked(self.manual_gen_callback)
        self._clicked_pts=[]
    def manual_gen_callback(self,event):
        if (int(event.button))==1: #left click #click_type:=
            print(event.xdata,event.ydata)
            self._clicked_pts.append((int(event.xdata),int(event.ydata)))
        # elif click_type==3: #right click
        #     print("Removing near:", event.xdata, event.ydata)
    def manual_gen_add(self): #resolve clicked points.
        self._click_button.disconnect(self._click_button_event)
        rel_pts=[[],[]]
        for x,y in self._clicked_pts:
            if y<self._height:
                rel_pts[0].append((x,y))
            else:
                rel_pts[1].append((x,y-self._height))
        if len(rel_pts[0]) == len(rel_pts[1]):
            self.points=[(a,b) for a,b in zip(rel_pts[0],rel_pts[1])]#convert from list of x,y sorted by image to pairs of x,y pairs
        else:
            raise ValueError("Mismatched number of selected points.")
    def get_rel(self):
        return Relation(self._imga.name,self._imgb.name,'p',self.points)