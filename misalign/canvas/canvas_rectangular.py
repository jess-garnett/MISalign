""" Canvas Rectangular
- Canvas Solve: Converts a set of relations into relative positions.
- Canvas Render: Renders combined images.
"""
from typing import runtime_checkable, Protocol
from PIL import Image as PILImage
import numpy as np
from misalign.model.project import MISProject
from misalign.model.image import MISImage
from misalign.model.relation import MISRelation

def rectangular_solve(relations:list[dict[str,tuple[str|int]]],image_names:list,origin:str):
    """Solves a set of relations rectangularly
    - Input is a list of rectangular relations[{'ref':(image_a,image_b),'rel':(x_offset,y_offset)}], a list of image names, and the image name of the origin.
    - Output is a dictionary of the form "image_name":(origin-relative x, origin-relative y)
    - Origin-relative x and y may be negative values.
    """
    relation_map=_relation_map(relations,image_names,origin)
    orig_rel_position={origin:(0,0)}
    solving=[origin]
    cansolve=[]
    solved=[]
    while len(solving)>0:
        for s in solving:
            for image_name,rel in relation_map[s]:
                cansolve.append(image_name)
                if rel["ref"][0]==s:
                    direction=1
                else:
                    direction=-1
                orig_rel_position[image_name]=(orig_rel_position[s][0]+direction*rel["rel"][0],orig_rel_position[s][1]+direction*rel["rel"][1])
        solved+=solving
        solving=cansolve
        cansolve=[]
    return orig_rel_position

def rectangular_solve_project(
        project:MISProject,
        image_names:list[str]|None=None,
        origin:str|None=None):
    """Solves a set of relations rectangularly given a MISProject
    - Input is a MISProject, optional: a list of image names(otherwise all images in project used), and optional: the image name of the origin(otherwise first image used).
    - Output is a dictionary of the form "image_name":(origin-relative x, origin-relative y)
    - Origin-relative x and y may be negative values.
    """
    
    relations:list[dict[str,tuple]]=[{"ref":r.get_reference(),"rel":r.get_relation('r')} for r in project.get_relations()]
    if image_names is None:
        image_names=project.get_image_names()
    if origin is None:
        origin=image_names[0]
    return rectangular_solve(
        relations=relations,
        image_names=image_names,
        origin=origin
    )

def _relation_map(relations:list[dict[str,tuple[str|int]]],image_names:list,origin:str):
    """Identify a map from origin to other images in a list of relations.
    - Input is a list of relations, a list of image names, and the image name of the origin.
    - Output is a dictionary of the form "image_name":[(image_name,relation) that reference to this image]
    """
    found=[image_names.index(origin)]
    matched=[]
    resolved=[]
    relation_map=dict({x:[] for x in image_names})

    while len(resolved)<len(relations):
        for i in found:
            for ii,x in enumerate(image_names):
                if (ii not in found) & (ii not in resolved) & (ii not in matched):
                    i_match=[image_names[i] in r["ref"] for r in relations]
                    ii_match=[image_names[ii] in r["ref"] for r in relations]
                    full_match=[im&iim for im,iim in zip(i_match,ii_match)]
                    if any(full_match):
                        relation_map[image_names[i]].append((image_names[ii],relations[full_match.index(True)]))
                        matched.append(ii)
            resolved.append(i)
        found=matched
        matched=[]
        #break if stuck
        if found==[]:
            break
    return relation_map

# Rectangular Render
    # Uses solution from rectangular_solve

## Find Extents
    ### Image Sizes
# Deprecated. Image Shapes are found using MISImage.shape
# def find_image_sizes(image_filepaths:dict) -> dict:
#     """ Gets image size from a dictionary of image filepaths.
#     - Takes a dictionary: {image_name:image_filepath}
#     - Returns a dictionary of image sizes: {image_name:(width,height)}"""
#     return {img_name:PILImage.open(img_fp).size for img_name,img_fp in image_filepaths.items()}
    ### Generate Points
def find_relative_extents(
        image_names:list,
        origin_relative_offsets:dict,
        image_shapes:dict):
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
        img_shape=image_shapes[img]
        x.append(-img_corner[0])#left side 
        x.append(-img_corner[0]+img_shape[1])#right side
        y.append(img_corner[1])#top side
        y.append(img_corner[1]-img_shape[0])#bottom side
        # Top to bottom is in the negative direction which is why the -img_size[1] is needed.
    origin_relative_extents=dict()
    origin_relative_extents["minx"]=min(x)
    origin_relative_extents["maxx"]=max(x)
    origin_relative_extents["miny"]=min(y)
    origin_relative_extents["maxy"]=max(y)
    return origin_relative_extents

def find_relative_extents_project(project:MISProject,origin_relative_offsets:dict):
    image_names=project.get_image_names()
    image_shapes={image_name:project.get_image(image_name).shape for image_name in image_names}
    return find_relative_extents(
        image_names=image_names,
        image_shapes=image_shapes,
        origin_relative_offsets=origin_relative_offsets)
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
## Render array-like class
@runtime_checkable
class array_like(Protocol):
    def __array__(self)->np.ndarray:
        ...
    @property
    def shape(self)->tuple[int, ...]:
        ...
## Rectangular Unblended Render
def render_unblended(
        # image_names:list,
        # image_filepaths:dict,
        # image_sizes:dict,
        image_arrays:dict[str, array_like],
        canvas_relative_offsets:dict,
        canvas_extents:dict):
    """ Renders a canvas without blending.
    - Takes:
        - A dictionary of image names/array likes {image_name:array_like}
        - A dictionary of canvas relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of canvas extents with keys `width` and `height`
    - Returns a PIL Image of the canvas."""
    canvas=np.zeros((canvas_extents["height"],canvas_extents["width"],3))
    for image_name,image_arraylike in image_arrays.items():
        image_shape: tuple[int, ...]=image_arraylike.shape
        image_place: tuple[int, ...]=canvas_relative_offsets[image_name]
        image_array: np.ndarray=np.asarray(image_arraylike)
        canv_slice={
            "left":image_place[0],
            "right":image_place[0]+image_shape[1],
            "top":image_place[1],
            "bottom":image_place[1]+image_shape[0],
        }
        canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]=image_array
    return PILImage.fromarray(canvas.astype(np.uint8))
def render_unblended_project(
        project:MISProject,
        canvas_relative_offsets:dict,
        canvas_extents:dict,
        image_names:list[str]|None=None,):
    if image_names is None:
        image_names=project.get_image_names()
    image_arrays: dict[str, array_like]={image_name:project.get_image(image_name) for image_name in image_names}
    return render_unblended(
        image_arrays=image_arrays,
        canvas_relative_offsets=canvas_relative_offsets,
        canvas_extents=canvas_extents
    )
## Rectangular Blended Render

    ### Distance-From-Edge Weight
#TODO add weight protocol
def weight_dfe(image_shape):
    """ Generates a distance-from-edge weight array for the given image shape.
    - Takes a tuple: (rows,columns)
    - Returns a numpy array of distance-from-edge values"""
    img_width=image_shape[1]
    img_height=image_shape[0]
    dfe_array=np.fromfunction(function=lambda y,x: np.min([x+1,y+1,img_width-x,img_height-y],axis=0),shape=(img_height,img_width))
    return dfe_array
    ### Flat Weight
def weight_flat(image_shape):
    """ Generates a flat weight array for the given image size.
    - Takes a tuple: (rows,columns)
    - Returns a numpy array of flat values"""
    img_width=image_shape[1]
    img_height=image_shape[0]
    flat_array=np.full(shape=(img_height,img_width),fill_value=1)
    return flat_array
    ### Normalization Array Building
def build_normalization(
        # image_names:list,
        # image_sizes:dict,
        # project:MISProject,
        image_arrays:dict[str, array_like],
        canvas_relative_offsets:dict,
        canvas_extents:dict,
        weight)->np.ndarray:
    """ Builds a normalization array.
    - Takes:
        - A dictionary of image names/array likes {image_name:array_like}
        - A dictionary of canvas relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of canvas extents with keys `width` and `height`
        - A weight array function `weight(img_size)`
    - Returns a numpy array of the normalization values."""
    normalization_array=np.zeros((canvas_extents["height"],canvas_extents["width"]))
    for image_name,image_arraylike in image_arrays.items():
        image_shape: tuple[int, ...]=image_arraylike.shape
        image_place: tuple[int, ...]=canvas_relative_offsets[image_name]
        weight_array=weight(image_shape)
        canv_slice={
            "left":image_place[0],
            "right":image_place[0]+image_shape[1],
            "top":image_place[1],
            "bottom":image_place[1]+image_shape[0],
        }
        normalization_array[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]+=weight_array
    return normalization_array
    ### Summation Blending
def render_blended(
#         image_names:list,
#         image_filepaths:dict,
#         image_sizes:dict,
        # project:MISProject,
        image_arrays:dict[str, array_like],
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
    for image_name,image_arraylike in image_arrays.items():
        image_shape: tuple[int, ...]=image_arraylike.shape
        image_place: tuple[int, ...]=canvas_relative_offsets[image_name]
        image_array: np.ndarray=np.asarray(image_arraylike)
        weight_array: np.ndarray=weight(image_shape)
        canv_slice: dict[str, int]={
            "left":image_place[0],
            "right":image_place[0]+image_shape[1],
            "top":image_place[1],
            "bottom":image_place[1]+image_shape[0],
        }
        normalizing_array: np.ndarray=normalizer[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]
        normed_array: np.ndarray=np.divide(weight_array,normalizing_array)
        weighted_image_array=np.repeat(normed_array[:,:,np.newaxis],3,axis=2)*image_array
        canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]+=weighted_image_array
    return PILImage.fromarray(canvas.astype(np.uint8))
def render_blended_project(
        project:MISProject,
        canvas_relative_offsets:dict,
        canvas_extents:dict,
        weight,
        image_names:list[str]|None=None,):
    if image_names is None:
        image_names=project.get_image_names()
    image_arrays: dict[str, array_like]={image_name:project.get_image(image_name) for image_name in image_names}
    normalizer=build_normalization(
        image_arrays=image_arrays,
        canvas_relative_offsets=canvas_relative_offsets,
        canvas_extents=canvas_extents,
        weight=weight)
    return render_blended(
        image_arrays=image_arrays,
        canvas_relative_offsets=canvas_relative_offsets,
        canvas_extents=canvas_extents,
        weight=weight,
        normalizer=normalizer
    )
#TODO rework methods/classes of canvas_rectangular to have "MISProject" and "just a dictionary" variants.
#TODO redo docstrings with project update
#TODO canvas_rectangular unit tests