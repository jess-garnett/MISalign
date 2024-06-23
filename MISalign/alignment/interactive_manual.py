"""
Interactive Matplotlib Manual Relation Module
"""
# Built around PyQt5 interface due to need for plt.ginput()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import ipywidgets as widgets
from IPython.display import display

from MISalign.model.relation import Relation
from MISalign.model.image import Image
from MISalign.model.mis_file import MisFile

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

class IMRControls():
    def __init__(self,mis_project:MisFile):
        self._project=mis_project
        self._images=[Image(x) for x in self._project.get_image_paths()]
        self.names=[x.name for x in self._images]
        ## setup dropdowns
        self._dropdown_a=widgets.Dropdown(
            options=self.names,
            value=self.names[0],
            description='Image A:',
            disabled=False,
        )
        self._dropdown_b=widgets.Dropdown(
            options=self.names,
            value=self.names[1],
            description='Image B:',
            disabled=False,
        )
        self._dropdowns=widgets.HBox([self._dropdown_a,self._dropdown_b])
        ## setup buttons
        self._button_next = widgets.Button(description='Next',)
        self._button_next.on_click(self.click_next)
        
        self._button_jump = widgets.Button(description='Jump To',)
        self._button_jump.on_click(self.click_jump)
        
        self._button_prev = widgets.Button(description='Previous',)
        self._button_prev.on_click(self.click_prev)
        
        self._button_resolve = widgets.Button(description='Resolve Relation',)
        self._button_resolve.on_click(self.click_resolve)

        self._button_save = widgets.Button(description='Save Relation',)
        self._button_save.on_click(self.click_save)

        self._buttons_move=widgets.HBox([self._button_next,self._button_jump,self._button_prev])
        self._buttons_relate=widgets.HBox([self._button_resolve,self._button_save])
        ## combine and display
        self._full=widgets.VBox([self._dropdowns,self._buttons_move,self._buttons_relate])
        display(self._full)
        ## display IMR and set to first pair.
        self.imr=InteractiveManualRelation()
        self.update_imr()
    def click_next(self,event):
        if (current := self.names.index(self._dropdown_b.get_interact_value()))+1<len(self.names):
            self._dropdown_a.value=self.names[current]
            self._dropdown_b.value=self.names[current+1]
            self.update_imr()
    def click_jump(self,event):
            self.update_imr()
    def click_prev(self,event):
        if (current := self.names.index(self._dropdown_a.get_interact_value()))-1>=0:
            self._dropdown_a.value=self.names[current-1]
            self._dropdown_b.value=self.names[current]
            self.update_imr()
    def click_resolve(self,event):
        self.imr.relate_resolve()
        self.imr.plot_points()
    def click_save(self,event):
         if self.imr.points is not None:
           self._project._relations.append(self.imr.get_relation())
        #TODO store in meaningful way. - Maybe break into resolve relation and save/update relation. Also displaying current relation?
         #TODO replacing relations vs turning them on and off vs other?
         #TODO relation management interface
    def update_imr(self):
            self.imr.change(
                self._images[self.names.index(self._dropdown_a.get_interact_value())],
                self._images[self.names.index(self._dropdown_b.get_interact_value())],
                )
            self.imr.relate()
    def get_mis(self):
            return self._project