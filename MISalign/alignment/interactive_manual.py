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
    """Allows user to manually specify relation between two images using interactive matplotlib."""
    def __init__(self):
        self._fig=plt.figure()
        self._ax=self._fig.subplots()
        self._fig.canvas.toolbar_visible = False
        self._fig.canvas.header_visible = False
        self._fig.canvas.footer_visible = False
        self._fig.tight_layout()
        self.points=None
        plt.show()
    def plot_points(self):
        """Plots the points of the current relation"""
        for pop in self.points:#pair of pairs - pop
            self._ax.plot([pop[0][0],pop[1][0]],[pop[0][1],pop[1][1]+self._height],"x:")
    def change(self,imga:Image,imgb:Image,points=None):
        """Replaces images and resets points and lines of plot."""
        #setup new images
        self._imga=imga
        self._imgb=imgb
        self._height=imga.size[1]
        # clear current axis/data
        self._ax.clear()
        self.points=None
        # set new images and add provided points.
        self._img_ax=self._ax.imshow(np.vstack([imga._img,imgb._img]))
        if points is not None:
            self.points=points
    def relate(self):
        """Gets user input points from figure"""
        self._click_button=Button(self._ax,label="")
        self._click_button_event=self._click_button.on_clicked(self._relate_callback)
        self._clicked_pts=[]
    def _relate_callback(self,event):
        if (int(event.button))==1: #left click #click_type:=
            # print(event.xdata,event.ydata)
            self._ax.plot([event.xdata],[event.ydata],"1r")
            self._clicked_pts.append((int(event.xdata),int(event.ydata)))
        # elif click_type==3: #right click
        #     print("Removing near:", event.xdata, event.ydata)
    def relate_resolve(self): #resolve clicked points.
        """Resolves user input points into pairs of x,y pairs"""
        self._click_button.disconnect(self._click_button_event)
        for pt in self._ax.lines:
            if pt.get_marker()=="1":
                pt.remove()
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
    def get_relation(self):
        """Get the current image names and the pairs of x,y pairs as a Relation object"""
        return Relation(self._imga.name,self._imgb.name,'p',self.points)