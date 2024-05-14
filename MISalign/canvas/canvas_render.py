""" Canvas Render
- Renders combined images.
"""
from PIL import Image as PILImage
import numpy as np
# Rectangular Render
    # Uses solution from rectangular_solve

## Find Extents
    ### Image Sizes
def find_image_sizes(image_filepaths:dict) -> dict:
    """ Gets image size from a dictionary of image filepaths.
    - Takes a dictionary: {image_name:image_filepath}
    - Returns a dictionary of image sizes: {image_name:(width,height)}"""
    return {img_name:PILImage.open(img_fp).size for img_name,img_fp in image_filepaths.items()}
    ### Generate Points
def find_relative_extents(
        image_names:list,
        origin_relative_offsets:dict,
        image_sizes:dict):
    """ Gets minimum and maximum x and y extents relative to the origin.
    - Takes:
        - A list of image names
        - A dictionary of origin relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of image sizes: {image_name:(width,height)}
    - Returns a dictionary of origin relative extents with keys `minx`,`maxx`,`miny`, and `maxy`"""
    x=[]
    y=[]
    for img in image_names:
        img_corner=origin_relative_offsets[img] #top left corner
        img_size=image_sizes[img]
        x.append(-img_corner[0])#left side 
        x.append(-img_corner[0]+img_size[0])#right side
        y.append(img_corner[1])#top side
        y.append(img_corner[1]-img_size[1])#bottom side
        # Top to bottom is in the negative direction which is why the -img_size[1] is needed.
        #TODO make sure this is in-line with numpy coordinate system.
    origin_relative_extents=dict()
    origin_relative_extents["minx"]=min(x)
    origin_relative_extents["maxx"]=max(x)
    origin_relative_extents["miny"]=min(y)
    origin_relative_extents["maxy"]=max(y)
    return origin_relative_extents
    ### Resolve Extents
def resolve_extents(origin_relative_extents:dict[str,int]):
    """ Gets canvas extents and offsets from origin relative extents.
    - Takes:
        - A dictionary of origin relative extents with keys `minx`,`maxx`,`miny`, and `maxy`.
    - Returns:
        - A dictionary of canvas extents with keys `width` and `height`
        - A dictionary of offsets with keys `x` and `y`."""
    canvas_extents={
        "width":origin_relative_extents["maxx"]-origin_relative_extents["minx"],
        "height":origin_relative_extents["maxy"]-origin_relative_extents["miny"]}
    canvas_offsets={
        "x":0-origin_relative_extents["minx"],
        "y":0-origin_relative_extents["miny"]}
    return canvas_extents, canvas_offsets
## Place In Canvas
def place_in_canvas(
        image_names:list,
        origin_relative_offsets:dict,
        canvas_extents:dict,
        canvas_offsets:dict):
    """ Converts origin relative offsets to canvas relative offsets.
    - Takes:
        - A list of image names
        - A dictionary of origin relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of canvas extents with keys `width` and `height`
        - A dictionary of offsets with keys `x` and `y`
    - Returns a dictionary of canvas relative offsets {image_name:(x-offset,y-offset)}"""
    canvas_relative_offsets={name:
        (-origin_relative_offsets[name][0]+canvas_offsets["x"],
        canvas_extents["height"]-(origin_relative_offsets[name][1]+canvas_offsets["y"])) 
        for name in image_names}
    return canvas_relative_offsets
## Rectangular Unblended Render
def render_unblended(
        image_names:list,
        image_filepaths:dict,
        image_sizes:dict,
        canvas_relative_offsets:dict,
        canvas_extents:dict):
    """ Renders a canvas without blending.
    - Takes:
        - A list of image names
        - A dictionary of image filepaths {image_name:image_filepath}
        - A dictionary of canvas relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of canvas extents with keys `width` and `height`
        - A dictionary of image sizes {image_name:(width,height)}
    - Returns a PIL Image of the canvas."""
    canvas=np.zeros((canvas_extents["height"],canvas_extents["width"],3))
    for img in image_names:
        img_size=image_sizes[img]
        img_place=canvas_relative_offsets[img]
        img_fp=image_filepaths[img]
        img_arr=np.array(PILImage.open(img_fp))
        canv_slice={
            "left":img_place[0],
            "right":img_place[0]+img_size[0],
            "top":img_place[1],
            "bottom":img_place[1]+img_size[1],
        }
        canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]=img_arr
    return PILImage.fromarray(canvas.astype(np.uint8))
## Rectangular Blended Render

    ### Distance-From-Edge Weight
def weight_dfe(img_size):
    """ Generates a distance-from-edge weight array for the given image size.
    - Takes a tuple: (width,height)
    - Returns a numpy array of distance-from-edge values"""
    img_width=img_size[0]
    img_height=img_size[1]
    dfe_array=np.fromfunction(function=lambda y,x: np.min([x+1,y+1,img_width-x,img_height-y],axis=0),shape=(img_height,img_width))
    return dfe_array
    ### Flat Weight
def weight_flat(img_size):
    """ Generates a flat weight array for the given image size.
    - Takes a tuple: (width,height)
    - Returns a numpy array of flat values"""
    img_width=img_size[0]
    img_height=img_size[1]
    flat_array=np.full(shape=(img_height,img_width),fill_value=1)
    return flat_array
    ### Normalization Array Building
def build_normalization(
        image_names:list,
        image_sizes:dict,
        canvas_relative_offsets:dict,
        canvas_extents:dict,
        weight):
    """ Builds a normalization array.
    - Takes:
        - A list of image names
        - A dictionary of canvas relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of canvas extents with keys `width` and `height`
        - A dictionary of image sizes {image_name:(width,height)}
        - A weight array function `weight(img_size)`
    - Returns a numpy array of the normalization values."""
    normalization_array=np.zeros((canvas_extents["height"],canvas_extents["width"]))
    for img in image_names:
        img_size=image_sizes[img]
        img_place=canvas_relative_offsets[img]
        weight_arr=weight(img_size)
        canv_slice={
            "left":img_place[0],
            "right":img_place[0]+img_size[0],
            "top":img_place[1],
            "bottom":img_place[1]+img_size[1],
        }
        normalization_array[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]+=weight_arr
    return normalization_array
    ### Summation Blending
def render_blended(
        image_names:list,
        image_filepaths:dict,
        image_sizes:dict,
        canvas_relative_offsets:dict,
        canvas_extents:dict,
        weight,
        normalizer:np.ndarray):
    """ Renders a canvas without blending.
    - Takes:
        - A list of image names
        - A dictionary of image filepaths {image_name:image_filepath}
        - A dictionary of canvas relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of canvas extents with keys `width` and `height`
        - A dictionary of image sizes {image_name:(width,height)}
        - A weight array function `weight(img_size)`
        - A numpy array of the normalization values
    - Returns a PIL Image of the canvas."""
    canvas=np.zeros((canvas_extents["height"],canvas_extents["width"],3))
    for img in image_names:
        img_size=image_sizes[img]
        img_place=canvas_relative_offsets[img]
        img_fp=image_filepaths[img]
        img_arr=np.array(PILImage.open(img_fp))
        canv_slice={
            "left":img_place[0],
            "right":img_place[0]+img_size[0],
            "top":img_place[1],
            "bottom":img_place[1]+img_size[1],
        }
        weight_arr=weight(img_size)
        normalizing_arr=normalizer[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]
        normed_arr=np.divide(weight_arr,normalizing_arr)
        weighted_img_arr=np.repeat(normed_arr[:,:,np.newaxis],3,axis=2)*img_arr
        canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]+=weighted_img_arr
    return PILImage.fromarray(canvas.astype(np.uint8))