"""
Interactive Matplotlib Manual Relation Module
"""
# Built around PyQt5 interface due to need for plt.ginput()
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from ipympl.backend_nbagg import Canvas
import ipywidgets as widgets
from IPython.display import display

from misalign.model.project import MISProject
from misalign.model.relation import MISRelationPoints
from misalign.model.image import MISImage

class InteractiveManualRelation():
    """
    Interactive matplotlib figure-based interface for visualizing relations and selecting matching points.

    Do not use this class directly, use `IMRControls`.
    Uses `ipympl` to display in Jupyter Notebooks.

    Notes
    -----
    Currently images must have the same width.
    """
    def __init__(self)->None:
        """
        Initialize InteractiveManualRelation.
        """
        self._fig=plt.figure()
        self._ax=self._fig.subplots()
        canvas:Canvas=self._fig.canvas # type: ignore
        canvas.toolbar_visible = False
        canvas.header_visible = False
        canvas.footer_visible = False
        self._fig.tight_layout()
        self.points=None
        plt.show()
    def plot_points(self)->None:
        """
        Plots the points of the current relation.
        """
        for pop in self.points:# type: ignore #pair of pairs - pop
            self._ax.plot([pop[0][0],pop[1][0]],[pop[0][1],pop[1][1]+self._height],"x:")
    def change(self,
            image_a:MISImage,
            image_b:MISImage,
            points:list[tuple[tuple[int,int],tuple[int,int]]]|None=None
            )->None:
        """
        Replaces images and resets the points and lines on the plot.
        
        Parameters
        ----------
        image_a : MISImage
            Upper image.
        image_b : MISImage
            Lower image.
        points : list[tuple[tuple[int,int],tuple[int,int]]] | None
            Matching points to load in with images. In the form `[((xi,yi),(xj,yj)),...]`.
        """
        #setup new images
        self._image_a=image_a
        self._image_b=image_b
        self._height=image_a.shape[0]
        # clear current points/lines on axis
        [x.remove() for x in self._ax.get_lines()]
        # set new images and add provided points.
        self._image_stack=np.vstack([np.asarray(image_a),np.asarray(image_b)])
        try:
            self._image_axes.set_data(self._image_stack)
            self._fig.canvas.draw_idle()
        except AttributeError:
            self._image_axes=self._ax.imshow(self._image_stack)
        if points is not None:
            self.points=points
    def relate_setup(self)->None:
        """
        Setup or reset list of clicked points and button on axes.
        """
        self._click_button=Button(self._ax,label="")
        self._click_button_event=self._click_button.on_clicked(self._relate_callback)
        self._clicked_pts=[]
    def _relate_callback(self,event)->None:
        """
        Relate button callback method.

        Used by the button in `relate_setup` to store clicked points.

        Parameters
        ----------
        event
            Click event data with `event.xdata` and `event.ydata`.
            `event.button` must be `1` for left click.
        """
        if (int(event.button))==1: #left click #click_type:=
            # print(event.xdata,event.ydata)
            self._ax.plot([event.xdata],[event.ydata],"1r")
            self._clicked_pts.append((int(event.xdata),int(event.ydata)))
        # elif click_type==3: #right click
        #     print("Removing near:", event.xdata, event.ydata)
    def relate_resolve(self)->None: #resolve clicked points.
        """
        Resolves user input points into pairs of x,y pairs.

        Notes
        -----
        Disconnects the button callback from `relate_setup`.
        Updates `self.points` with clicked points.
        """
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
    def get_relation(self)->MISRelationPoints:
        """
        Get the current image names and the pairs of x,y pairs as a `MISRelationPoints`.
        
        Returns
        -------
        points : list[tuple[tuple[int,int],tuple[int,int]]] | None
            Matching points from `relate_resolve`. In the form `[((xi,yi),(xj,yj)),...]`.
        """
        return MISRelationPoints(image_pair=(self._image_a.name,self._image_b.name),points=self.points)

class IMRControls():
    """
    Widget assembly for controlling `InteractiveManualRelation`.

    Uses `ipywidgets` for controls in Jupyter Notebooks.
    """
    def __init__(self,mis_project:MISProject):
        """
        Initialize IMRControls object from MISProject.

        Parameters
        ----------
        mis_project : MISProject
            Source project for images.
        """
        self._project=mis_project
        # self._images=mis_project.get_image_names()
        self.names=mis_project.get_image_names()
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
        self._button_next.on_click(self._click_next)
        
        self._button_jump = widgets.Button(description='Jump To',)
        self._button_jump.on_click(self._click_jump)
        
        self._button_prev = widgets.Button(description='Previous',)
        self._button_prev.on_click(self._click_prev)
        
        self._button_resolve = widgets.Button(description='Resolve Relation',)
        self._button_resolve.on_click(self._click_resolve)

        self._button_save = widgets.Button(description='Save Relation',)
        self._button_save.on_click(self._click_save)

        self._buttons_move=widgets.HBox([self._button_next,self._button_jump,self._button_prev])
        self._buttons_relate=widgets.HBox([self._button_resolve,self._button_save])
        ## combine and display
        self._full=widgets.VBox([self._dropdowns,self._buttons_move,self._buttons_relate])
        display(self._full)
        ## display IMR and set to first pair.
        self.imr=InteractiveManualRelation()
        self._update_imr()
    def _click_next(self,event)->None:
        """
        Next button callback.

        Parameters
        ----------
        event
            Click event.

        Notes
        -----
        Only runs if the current 'image_b' index+1 is less than the total number of images.
        """
        if (current := self.names.index(self._dropdown_b.get_interact_value()))+1<len(self.names):
            self._dropdown_a.value=self.names[current]
            self._dropdown_b.value=self.names[current+1]
            self._update_imr()
    def _click_jump(self,event)->None:
        """
        Jump button callback.

        Parameters
        ----------
        event
            Click event.
        """
        self._update_imr()
    def _click_prev(self,event)->None:
        """
        Previous button callback.

        Parameters
        ----------
        event
            Click event.

        Notes
        -----
        Only runs if the current 'image_a' index-1 is greater than or equal to 0.
        """
        if (current := self.names.index(self._dropdown_a.get_interact_value()))-1>=0:
            self._dropdown_a.value=self.names[current-1]
            self._dropdown_b.value=self.names[current]
            self._update_imr()
    def _click_resolve(self,event)->None:
        """
        Resolve button callback.

        Parameters
        ----------
        event
            Click event.
        """
        self.imr.relate_resolve()
        self.imr.plot_points()
    def _click_save(self,event)->None:
        """
        Save button callback.

        Parameters
        ----------
        event
            Click event.
        
        Notes
        -----
        Adds `MISRelationPoints` to `MISProject` using `add_relation` method.
        """
        if self.imr.points is not None:
            self._project.add_relation(self.imr.get_relation())
        #TODO relation management interface - replace relations, prioritize relations, disable relations, etc.
    def _update_imr(self)->None:
        """
        Update InteractiveManualRelation using images from dropdowns.
        """
        self.imr.change(
            self._project.get_image(self._dropdown_a.get_interact_value()),
            self._project.get_image(self._dropdown_b.get_interact_value()),
            )
        self.imr.relate_setup()
    def get_mis(self)->MISProject:
        """
        Get MISProject with saved relations.

        Returns
        -------
        MISProject
            Project with saved relations added.
        """
        return self._project