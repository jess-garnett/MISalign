"""
Interactive Matplotlib Manual Relation Module
"""
import numpy as np
from matplotlib import pyplot as plt

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
        self.points=None
    def plot_points(self):
        """Plots the points of the current relation"""
        for pop in self.points:
            plt.plot([pop[0][0],pop[1][0]],[pop[0][1],pop[1][1]+self._height],"x:")
    def change_images(self,imga:Image,imgb:Image):
        """Replaces image in IMR figure"""
        self._imga=imga
        self._imgb=imgb
        self._height=imga.size[1]
        self._ax=plt.imshow(np.vstack([imga._img,imgb._img]))
        self.points=None
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
    def get_rel(self):
        return Relation(self._imga.name,self._imgb.name,'p',self.points)