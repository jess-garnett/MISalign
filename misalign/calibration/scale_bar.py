"""
Matplotlib-based Scale Bar Module
"""
from typing import Any
from matplotlib import pyplot as plt
from matplotlib import axes
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from PIL import Image as PILImage
from quantiphy import Quantity
from logging import warning
from pathlib import Path
import numpy as np

def add_scale_bar(axes:axes.Axes,
                  scale_measurement:str,
                  calibration:dict[str,Any],
                  **AnchoredSizeBar_kwargs
                  ):
    """
    Add scale bar to matplotlib axes.

    Parameters
    ----------
    axes : matplotlib.axes.Axes
        Axes to add the scale bar to.
    scale_measurement : str
        Label for scale bar. Must be interpretable by `quantiphy`.
    calibration : dict[str,Any]
        calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}`
    **AnchoredSizeBar_kwargs : kwargs
        All other kwargs are passed to `mpl_toolkits.axes_grid1.anchored_artists.AnchoredSizeBar`
        Defaults: `{"loc":'upper left', "pad":0.5, "borderpad":0.5, "sep":2, "frameon":True,}`
    """
    # Generate scale
    pixel_distance:int=calibration["pixel"]
    length_quantity=Quantity(f"{calibration['length']} {calibration['length_unit']}")
    scale_measure_quantity=Quantity(scale_measurement)
    scale_ratio=scale_measure_quantity/length_quantity
    pixels_scaled=scale_ratio*pixel_distance
    # AnchoredSizeBar arg setup
    asb_kwargs_defaults={
        "loc":'upper left',
        "pad":0.5,
        "borderpad":0.5,
        "sep":2,
        "frameon":True,
    }
    asb_kwargs = asb_kwargs_defaults | AnchoredSizeBar_kwargs
    # Creates and add scale bar to axes
    scale_bar=AnchoredSizeBar(
        axes.transData,
        int(pixels_scaled),
        scale_measurement,
        **asb_kwargs
    )
    axes.add_artist(scale_bar)

def image_with_scale_bar(image:Path|str|Any,
                  scale_measurement:str,
                  calibration:dict,
                  **AnchoredSizeBar_kwargs
                  ):
    """
    Show image with scale bar.

    Sets up matplotlib figure and axes then shows image with scale bar.

    Parameters
    ----------
    image : Path | str | Any
        Either `Path` or path-like string to image file or a `matplotlib.pyplot.imshow` compatible array.
    scale_measurement : str
        Label for scale bar. Must be interpretable by `quantiphy`.
    calibration : dict[str,Any]
        calibration dictionary of form `{"pixel":number,"length":number,"length_unit":str}`
    **AnchoredSizeBar_kwargs : kwargs
        All other kwargs are passed to `mpl_toolkits.axes_grid1.anchored_artists.AnchoredSizeBar`
        Defaults: `{"loc":'upper left', "pad":0.5, "borderpad":0.5, "sep":2, "frameon":True,}`
    """
    if not plt.isinteractive():
        warning("Matplotlib is not running in interactive mode and rescaling will not work. Please switch to an interactive mpl backend.")
    
    if type(image) is str or type(image) is Path:
        array=np.asarray(PILImage.open(image))
    else:
        array=np.asarray(image)
    
    plt.figure()
    if len(array.shape)==2:
        plt.imshow(array,cmap="gray",vmin=np.iinfo(array.dtype).min,vmax=np.iinfo(array.dtype).max)
    else:
        plt.imshow(array)
    add_scale_bar(plt.gca(),scale_measurement,calibration,**AnchoredSizeBar_kwargs)
    plt.gca().set_axis_off()
    plt.show()

def scale_bar_calibrate(scale_dpi:int):
    """
    Scale current matplotlib figure size relative to image size and desired DPI.

    Increasing the DPI for a set image size makes the effective image size smaller, resulting in fonts or other features being larger.

    Parameters
    ----------
    scale_dpi : int
        Scaled image DPI.
    """
    plt.tight_layout(pad=0)
    y_lim=plt.gca().get_ylim()
    y_size=abs(int(y_lim[0]-y_lim[1]))
    x_lim=plt.gca().get_xlim()
    x_size=abs(int(x_lim[0]-x_lim[1]))
    y_figsize=y_size/scale_dpi
    x_figsize=x_size/scale_dpi
    plt.gcf().set_size_inches(x_figsize,y_figsize)

def save_calibrated_image(image_filepath:Path|str,scale_dpi:int):
    """
    Save image with scale bar.

    When used with the same `scale_dpi` as `scale_bar_calibrate` will produce a 1:1 scale image.
    If `scale_dpi` is decreased for saving it will result in a scaled down image.

    Parameters
    ----------
    image_filepath : Path | str
        `Path` or path-like string for image file.
    scale_dpi : int
        Scaled image DPI.
    """
    plt.savefig(image_filepath,bbox_inches="tight",pad_inches=0,dpi=scale_dpi)

# Image Overlays

def add_image_overlays(
    image_names:list,
    canvas_relative_offsets:dict[str,tuple[int,int]],
    image_shapes,
    boundary=True,
    boundary_kwargs:dict|None=None,
    label=True,
    label_kwargs:dict|None=None,)->None:
    """
    Adds image-boundary overlays to a matplotlib imshow of a canvas.

    Parameters
    ----------
    image_names : list[str]
        List of image names.
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    image_shapes : dict
        Dictionary of the form `"image_name":(rows, columns, ...)`
    boundary : bool
        Wether to draw the image boundaries. `True` by default.
    boundary_kwargs : dict
        Keyword arguments to be passed to `matplotlib.patches.Rectangle`.
        Default: {'fill':False,'edgecolor':'r'}
    label : bool
        Wether to draw the image labels. `True` by default.
    label_kwargs : dict
        Keyword arguments to be passed to `matplotlib.pyplot.text`.
        Default: {'backgroundcolor':(1,1,1,0.25),'fontsize':'small'}
    """
    if boundary_kwargs is None:
        boundary_kwargs={'fill':False,'edgecolor':'r'}
    if label_kwargs is None:
        label_kwargs={'backgroundcolor':(1,1,1,0.25),'fontsize':'small'}
    for image_name in image_names:
        if boundary:
            rectangle=plt.Rectangle(
                xy=canvas_relative_offsets[image_name],
                width=image_shapes[image_name][1],
                height=image_shapes[image_name][0],
                **boundary_kwargs)
            plt.gca().add_artist(rectangle)
        if label:
            text=plt.Text(
                canvas_relative_offsets[image_name][0]+(0.5*image_shapes[image_name][1]),
                canvas_relative_offsets[image_name][1]+(0.5*image_shapes[image_name][0]),
                image_name,
                horizontalalignment='center',verticalalignment='center',
                **label_kwargs)
            plt.gca().add_artist(text)
def add_image_overlays_project(
    project, #:MISProject
    canvas_relative_offsets:dict[str,tuple[int,int]],
    image_names:list[str]|None=None,
    boundary=True,
    boundary_kwargs:dict|None=None,
    label=True,
    label_kwargs:dict|None=None,)->None:
    """
    Adds image-boundary overlays to a matplotlib imshow of a canvas.

    Parameters
    ----------
    project : MISProject
        A MISProject with images.
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    image_names : list[str] | None
        List of image names or `None` by default.
        If `None` all images in project will be used.
    boundary : bool
        Wether to draw the image boundaries. `True` by default.
    boundary_kwargs : dict
        Keyword arguments to be passed to `matplotlib.patches.Rectangle`.
        Default: {'fill':False,'edgecolor':'r'}
    label : bool
        Wether to draw the image labels. `True` by default.
    label_kwargs : dict
        Keyword arguments to be passed to `matplotlib.pyplot.text`.
        Default: {'backgroundcolor':(1,1,1,0.25),'fontsize':'small'}
    """
    if image_names is None:
        image_names=project.get_image_names()
    image_shapes={image_name:project.get_image(image_name).shape for image_name in image_names}
    add_image_overlays(
        image_names=image_names,
        canvas_relative_offsets=canvas_relative_offsets,
        image_shapes=image_shapes,
        boundary=boundary,
        boundary_kwargs=boundary_kwargs,
        label=label,
        label_kwargs=label_kwargs,)

# TODO add transpose handling to these