from matplotlib import pyplot as plt
from matplotlib import axes
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from PIL import Image as PILImage
from quantiphy import Quantity
from calibrate import CalibrationManual

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
def image_with_scale_bar(image_fp:str,
                  scale_measurement:str,
                  calibration:dict,
                  **AnchoredSizeBar_kwargs:dict
                  ):
    plt.figure()
    plt.imshow(PILImage.open(image_fp))
    add_scale_bar(plt.gca(),scale_measurement,calibration,**AnchoredSizeBar_kwargs)
    plt.show()