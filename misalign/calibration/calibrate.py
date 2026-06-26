"""
Interactive Matplotlib Manual Calibration Module
"""
from typing import Any
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from ipympl.backend_nbagg import Canvas
from PIL import Image as PILImage
import json
from pathlib import Path
from logging import warning

class CalibrationManual():
    """
    Interactive matplotlib figure-based interface for manually specify calibration by providing a distance and selecting points.

    Uses `ipympl` to display in Jupyter Notebooks.
    """
    def __init__(self,calibration_image_path:Path|str|None=None)->None:
        """
        Initialize CalibrationManual.

        Parameters
        ----------
        calibration_image_path
            `Path` or path-like string to image file or `None` by default.

        Notes
        -----
        `calibration_image_path=None` skips the entire initialization.
        This is intended for accessing the non-GUI parts of the class with `load_calibration`.
        """
        #TODO split calibration into a GUI class and a data handling class
        if calibration_image_path is None:
            return
        if not plt.isinteractive():
            warning("Matplotlib is not running in interactive mode and point selection will not work. Please switch to an interactive mpl backend.")
        self.distances: dict[str,Any]=dict()
            # {"pixel":number,"length":number,"length_unit":str}
        self._fig=plt.figure()
        self._ax=self._fig.subplots()
        canvas:Canvas=self._fig.canvas # type: ignore
        canvas.toolbar_visible = False
        canvas.header_visible = False
        canvas.footer_visible = False
        self._fig.tight_layout()
        self._calibration_image=PILImage.open(calibration_image_path)
        self._ax.imshow(self._calibration_image)
        plt.show()
    def calibrate_setup(self)->None:
        """
        Setup or reset list of clicked points and button on axes.
        """
        self._click_button=Button(self._ax,label="")
        self._click_button_event=self._click_button.on_clicked(self._calibrate_callback)
        self._clicked_pts=[]
    def _calibrate_callback(self,event)->None:
        if (int(event.button))==1: #left click
            # print(event.xdata,event.ydata)
            self._ax.plot([event.xdata],[event.ydata],"1r")
            self._clicked_pts.append((event.xdata,event.ydata))
    def calibrate_resolve(self)->None:
        """
        Resolves user input points into average distance between all pairs of points.

        Notes
        -----
        Disconnects the button callback from `calibrate_setup`.
        Updates `self.distances["pixel"]` with mean distance.
        """
        self._click_button.disconnect(self._click_button_event)
        for pt in self._ax.lines:
            if pt.get_marker()=="1":
                pt.remove()
        points_a=self._clicked_pts[::2]
        points_b=self._clicked_pts[1::2]
        pixel_distances=[]
        for (ax,ay),(bx,by) in zip(points_a,points_b):
            plt.plot([ax,bx],[ay,by],".--")
            pixel_distance=((ax-bx)**2+(ay-by)**2)**0.5
            pixel_distances.append(pixel_distance)
            print(f"Pixel Distance:{pixel_distance:.2F}")
        pixel_distances_average : float = sum(pixel_distances)/len(pixel_distances)
        print(f"Average Pixel Distance: {pixel_distances_average:.2F}")
        self.distances["pixel"]=pixel_distances_average

    def calibrate_measurement(self,length:int|float,units:str)->None:
        """
        Set known distance for the pixel measurement.

        Parameters
        ----------
        length : int | float
            Length of reference measurement.
        units : str
            Units for length of reference measurement.
        """
        self.distances["length"]=length
        self.distances["length_unit"]=units

    def print_pixels_per_length(self)->None:
        """
        Prints scale in terms of pixel per length
        """
        print(f"Pixels: {self.distances['pixel']:.2F}")
        print(f"Length: {self.distances['length']} {self.distances['length_unit']}")
        print(f"Pixels/Length = {self.distances['pixel']/self.distances['length']:.2f} pixels/{self.distances['length_unit']}")
    def print_length_per_pixel(self)->None:
        """
        Prints scale in terms of length per pixel
        """
        print(f"Pixels: {self.distances['pixel']:.2F}")
        print(f"Length: {self.distances['length']} {self.distances['length_unit']}")
        print(f"length/pixel = {self.distances['length']/self.distances['pixel']:.4g} {self.distances['length_unit']}/pixels")
    def save_calibration(self,miscal_filepath:Path|str)->None:
        """
        Saves calibration as JSON in `.miscal.json` file
        
        Parameters
        ----------
        miscal_filepath : Path | str
            `Path` or path-like string for `.miscal.json` file.
        """
        json_object=json.dumps(self.distances,indent=4)
        with open(miscal_filepath,"w") as outfile:
            outfile.write(json_object)
    def load_calibration(self,cal_filepath:Path|str)->None:
        """
        Loads calibration from JSON in `.miscal.json` or `.mis.json` file
        
        Parameters
        ----------
        cal_filepath : Path | str
            `Path` or path-like string to `.miscal.json` or `.mis.json` file.
        """
        if ".miscal.json" in str(cal_filepath):
            self.distances=calibration_from_json(cal_filepath)
        if ".mis.json" in str(cal_filepath):
            self.distances=calibration_from_mis(cal_filepath)


def calibration_from_json(miscal_filepath:Path|str)->dict[str,Any]:
    """
    Returns calibration from JSON in `.miscal.json` file
    
    Parameters
    ----------
    miscal_filepath : Path | str
        `Path` or path-like string to `.miscal.json` file.
    
    Returns
    -------
    calibration_dict : dict[str,Any]
        calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}`
    """
    with open(miscal_filepath) as infile:
        return json.load(infile)

def calibration_from_mis(mis_filepath:Path|str)->dict[str,Any]:
    """
    Returns calibration from JSON in `.mis.json` file
    
    Parameters
    ----------
    mis_filepath : Path | str
        `Path` or path-like string to `.mis.json` file.

    Returns
    -------
    calibration_dict : dict[str,Any]
        calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}`
    """
    with open(mis_filepath) as infile:
        return json.load(infile)["calibration"]