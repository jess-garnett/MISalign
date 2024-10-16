from matplotlib import pyplot as plt
from matplotlib import axes
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from PIL import Image as PILImage
from quantiphy import Quantity

def add_scale_bar(axes:axes.Axes,
                  scale_measurement:str,
                  calibration:dict,
                  **AnchoredSizeBar_kwargs:dict
                  ):
    # Generate scale
    pixel_distance=calibration["pixel"]
    length_quantity=Quantity(f"{calibration['length']} {calibration['length_unit']}")
    scale_measure_quantity=Quantity(scale_measurement)
    scale_ratio=scale_measure_quantity/length_quantity
    pixels_scaled=scale_ratio*pixel_distance
    # AnchoredSizeBar arg setup
    asb_kwargs={
        "loc":'upper left',
        "pad":0.5,
        "borderpad":0.5,
        "sep":2,
        "frameon":True,
    }
    for key,value in AnchoredSizeBar_kwargs.items():
        asb_kwargs[key]=value
    # Creates and add scale bar to axes
    scale_bar=AnchoredSizeBar(
        axes.transData,
        int(pixels_scaled),
        scale_measurement,
        **asb_kwargs
    )
    axes.add_artist(scale_bar)
def image_with_scale_bar(image:str,
                  scale_measurement:str,
                  calibration:dict,
                  **AnchoredSizeBar_kwargs:dict
                  ):
    
    if type(image) is str:
        image=PILImage.open(image)
    
    fig=plt.figure()
    plt.imshow(image)
    add_scale_bar(plt.gca(),scale_measurement,calibration,**AnchoredSizeBar_kwargs)
    plt.gca().set_axis_off()
    plt.show()
def scale_bar_calibrate(scale_dpi:int):
    plt.tight_layout(pad=0)
    y_lim=plt.gca().get_ylim()
    y_size=abs(int(y_lim[0]-y_lim[1]))
    x_lim=plt.gca().get_xlim()
    x_size=abs(int(x_lim[0]-x_lim[1]))
    y_figsize=y_size/scale_dpi
    x_figsize=x_size/scale_dpi
    plt.gcf().set_size_inches(x_figsize,y_figsize)