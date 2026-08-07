"""
Canvas Rectangular Module

Solve how images relate to an origin.
Determine how images should be placed in a canvas and how big that canvas should be.
Render that canvas either unblended or blended.

`..._project` variants of functions implement the standard functions while simplifying certain data extraction/data formatting steps.
"""
from typing import runtime_checkable, Protocol, Any
from collections.abc import Callable
from PIL import Image as PILImage
import numpy as np
from misalign.model.project import MISProject

def simple_relation_map(relations:list[dict[str,tuple]],image_names:list[str],origin:str)->dict[str,list[tuple]]:
    """
    Identify a simple map from the origin to other images in a list of relations.
    
    Parameters
    ----------
    relations : list[dict[str, tuple[str, str] | Any]]
        List of relations(as dicts) in the form: `[{'ref':('image a','image b'),...},...]`.
    image_names : list[str]
        List of image names.
    origin : str
        Image name to start relation map at.

    Returns
    -------
    relation_map : dict[str,list[tuple]]
        Dictionary of the form `{'image a':[('image b',{rectangular relation dict a-b}),...],...}`
    
    Notes
    -----
    Search is done breadth-wise from the origin and is 'sorted' by the order in `image_names`.
    Especially for snake-style relations this naive approach can cause fairly significant misalignment stackup.
    Adding additional relations that shorten the image path to the origin can help reduce this issue.
    """
    found=[image_names.index(origin)] # images that have been found to have a relation to the origin
    matched=[] # images that have been matched up with an image related to the origin
    resolved=[] # images that have had all of their relations checked for additional un-matched images.
    relation_map:dict[str,list[tuple]]=dict({x:[] for x in image_names})

    while len(resolved)<len(relations):
        # As long as there are more relations than resolved images continue.
        for i in found:
            # for image index i from the images with known locations
            for ii,x in enumerate(image_names):
                # for image index ii from all the images names
                if (ii not in found) & (ii not in matched) & (ii not in resolved):
                    # if image ii has not been found, matched, and resolved.
                    i_match=[image_names[i] in r["ref"] for r in relations] # find relations with image i
                    ii_match=[image_names[ii] in r["ref"] for r in relations] # find relations with image ii
                    full_match=[im&iim for im,iim in zip(i_match,ii_match)] # find relations with both image i and ii
                    if any(full_match): # if there are any full matches then
                        relation_map[image_names[i]].append((image_names[ii],relations[full_match.index(True)]))
                            # add the first relation that full matches to the list for image i in the relation map.
                        matched.append(ii) # put ii into matched.
            resolved.append(i) # once all i x ii have been checked move i to resolved.
        found=matched # set found to matched.
        matched=[] # clear matched.
        #break if stuck
        if found==[]: # if found is empty then all possible relations to origin have been found.
            break
    return relation_map 

def rectangular_solve(
    relations:list[dict[str,tuple]],
    image_names:list[str],
    origin:str,
    relation_map_function:Callable|None=None,
    )->dict[str,tuple[int,int]]:
    """
    Finds the origin relative position of images given their relative relationships.

    Parameters
    ----------
    relations : list[dict[str, tuple[str, str] | tuple[int, int]]]
        List of rectangular relations(as dicts) in the form: `[{'ref':('image a','image b'),'rel':(x,y)},...]`.
        The offset `x,y` maps from the `(x,y)` of `image a` to the `(0,0)` of `image b`.
    image_names : list[str]
        List of image names.
    origin : str
        Image name to start relation map at.
    relation_map_function : Callable
        Default `simple_relation_map`.
        Any function that accepts `relations,image_names,origin` and returns `{'image a':[('image b',{rectangular relation dict a-b}),...],...}`

    Returns
    -------
    origin_relative_offsets : dict[str, tuple[int, int]]
        Output is a dictionary of the form "image_name":(origin-relative x, origin-relative y)
        Origin-relative x and y may be negative values.
    """
    if relation_map_function is None:
        relation_map_function=simple_relation_map
    relation_map: dict=relation_map_function(relations,image_names,origin)
    origin_relative_offsets={origin:(0,0)}
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
                origin_relative_offsets[image_name]=(origin_relative_offsets[s][0]+direction*rel["rel"][0],origin_relative_offsets[s][1]+direction*rel["rel"][1])
        solved+=solving
        solving=cansolve
        cansolve=[]
    return origin_relative_offsets

def rectangular_solve_project(
    project:MISProject,
    image_names:list[str]|None=None,
    origin:str|None=None,
    relation_map_function:Callable|None=None,
    )->dict[str,tuple[int,int]]:
    """
    Finds the origin relative position of images given a MISProject.

    Parameters
    ----------
    project : MISProject
        A MISProject with images and relations.
    image_names : list[str] | None
        List of image names or `None` by default.
        If `None` all images in project will be used.
    origin : str | None
        Image name to start relation map at or `None` by default.
        If `None` first image in project will be used.
    relation_map_function : Callable
        Default `simple_relation_map`.
        Any function that accepts `relations,image_names,origin` and returns `{'image a':[('image b',{rectangular relation dict a-b}),...],...}`

    Returns
    -------
    origin_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(origin-relative x, origin-relative y)`
        Origin-relative x and y may be negative values.
    """
    
    relations:list[dict[str,Any]]=[{"ref":r.get_reference(),"rel":r.get_relation(relation_type='r')}
                                        for r in project.get_relations()]
    if image_names is None:
        image_names=project.get_image_names()
    if origin is None:
        origin=image_names[0]
    return rectangular_solve(
        relations=relations,
        image_names=image_names,
        origin=origin,
        relation_map_function=relation_map_function
    )


# Rectangular Render
    # Uses solution from rectangular_solve

## Find Extents
    ### Generate Points
def find_relative_extents(
        image_names:list,
        origin_relative_offsets:dict[str,tuple[int,int]],
        image_shapes:dict)->dict[str,int]:
    """
    Finds minimum and maximum x and y extents relative to the origin.

    Parameters
    ----------
    image_names : list[str]
        List of image names.
    origin_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(origin-relative x, origin-relative y)`
    image_shapes : dict
        Dictionary of the form `"image_name":(rows, columns, ...)`

    Returns
    -------
    origin_relative_extents : dict[str, int]
        Dictionary of origin relative extents with keys `minx`,`maxx`,`miny`, and `maxy`
        Origin-relative exents may be negative values.
    """
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

def find_relative_extents_project(
    project:MISProject,
    origin_relative_offsets:dict[str,tuple[int,int]],
    image_names:list[str]|None=None,):
    """
    Finds minimum and maximum x and y extents relative to the origin.

    Parameters
    ----------
    project : MISProject
        A MISProject with images.
    origin_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(origin-relative x, origin-relative y)`
    image_names : list[str] | None
        List of image names or `None` by default.
        If `None` all images in project will be used.

    Returns
    -------
    origin_relative_extents : dict[str, int]
        Dictionary of origin relative extents with keys `minx`,`maxx`,`miny`, and `maxy`
        Origin-relative exents may be negative values.
    """
    if image_names is None:
        image_names=project.get_image_names()
    image_shapes={image_name:project.get_image(image_name).shape for image_name in image_names}
    return find_relative_extents(
        image_names=image_names,
        image_shapes=image_shapes,
        origin_relative_offsets=origin_relative_offsets)
    ### Resolve Extents
def resolve_extents(origin_relative_extents:dict[str,int])->tuple[dict,dict]:
    """
    Gets canvas extents and offsets from origin relative extents.

    The primary purpose of this function is to convert from potentially negative origin relative values into values greater than or equal to 0.

    Parameters
    ----------
    origin_relative_extents : dict[str, int]
        Dictionary of origin relative extents with keys `minx`,`maxx`,`miny`, and `maxy`

    Returns
    -------
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    canvas_offsets : dict[str, int]
        Dictionary of origin to canvas offsets with keys `x` and `y`.
    """
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
        canvas_offsets:dict)->dict[str,tuple[int,int]]:
    """
    Converts origin relative offsets to canvas relative offsets.
    
    Parameters
    ----------
    image_names : list[str]
        List of image names.
    origin_relative_extents : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(origin-relative x, origin-relative y)`
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    canvas_offsets : dict[str, int]
        Dictionary of offsets with keys `x` and `y`.

    Returns
    -------
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    """
    canvas_relative_offsets={name:
        (-origin_relative_offsets[name][0]+canvas_offsets["x"],
        canvas_extents["height"]-(origin_relative_offsets[name][1]+canvas_offsets["y"])) 
        for name in image_names}
    return canvas_relative_offsets
## Render array-like class
@runtime_checkable
class array_like(Protocol):
    """
    Type hinting utility class for representing objects compatible with `numpy.asarray` and with `.shape` property.

    MISImages are `array_like`.
    """
    def __array__(self)->np.ndarray:
        """
        Get array.
        
        Returns
        -------
        array : np.ndarray
            Numpy array.
        """
        ...
    @property
    def shape(self)->tuple[int, ...]:
        """
        Get the shape of the array.
        
        Returns
        -------
        shape : tuple[int]
            Tuple of ints describing the shape in numpy order - row, col, depth - (1200,1600,3).
        """
        ...
## Rectangular Unblended Render
def render_unblended(
        image_arrays:dict[str,array_like],
        canvas_relative_offsets:dict,
        canvas_extents:dict,
        return_image:bool=True,
        depth:int|None=None)->PILImage.Image | np.ndarray:
    """
    Renders a canvas without blending.

    Parameters
    ----------
    image_arrays : dict[str, array_like],
        Dictionary of the form `"image_name":array_like`
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    return_image : bool
        Wether to return an image or an array. `True` by default.
    depth : int|None
        Depth of images and canvas or `None` by default.
        If `None` depth determined from the shape of the first image in image_arrays.values().
    
    Returns
    PIL.Image.Image | numpy.ndarray
        PIL Image of the canvas or array if `return_image=False`.
    
    Notes
    -----
    The order of `image_arrays.items()` determines the stacking order with later items overriding early items.
    """
    image_2d=False
    if depth is None:
        first_image=next(iter(image_arrays.values()))
        if len(first_image.shape)==2: # image does not have depth - 1D
            depth=1
            image_2d=True
        else:
            depth=first_image.shape[2]
    canvas=np.zeros((canvas_extents["height"],canvas_extents["width"],depth))
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
        if image_2d:
            canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]=image_array[:,:,np.newaxis]
        else:
            canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]=image_array
    if return_image:
        if image_2d:
            return PILImage.fromarray(canvas[:,:,0].astype(np.uint8))
        else:
            return PILImage.fromarray(canvas.astype(np.uint8))
    else:
        return canvas
def render_unblended_project(
    project:MISProject,
    canvas_relative_offsets:dict[str,tuple[int,int]],
    canvas_extents:dict[str,int],
    image_names:list[str]|None=None,
    return_image:bool=True,
    depth:int|None=None)->PILImage.Image | np.ndarray:
    """
    Renders a canvas from a project without blending.

    Parameters
    ----------
    project : MISProject
        A MISProject with images.
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    image_names : list[str] | None
        List of image names or `None` by default.
        If `None` all images in project will be used.
    return_image : bool
        Wether to return an image or an array. `True` by default.
    depth : int|None
        Depth of images and canvas or `None` by default.
        If `None` depth determined from the shape of the first image in image_arrays.values().
    
    Returns
    -------
    PIL.Image.Image | numpy.ndarray
        PIL Image of the canvas or array if `return_image=False`.

    Notes
    -----
    The order of `image_names` determines the stacking order with later items overriding early items.
    """
    if image_names is None:
        image_names=project.get_image_names()
    image_arrays: dict[str, array_like]={image_name:project.get_image(image_name) for image_name in image_names}
    return render_unblended(
        image_arrays=image_arrays,
        canvas_relative_offsets=canvas_relative_offsets,
        canvas_extents=canvas_extents,
        return_image=return_image,
        depth=depth
    )
## Rectangular Blended Render

    ### Distance-From-Edge Weight
#TODO add weight protocol
def weight_dfe(image_shape:tuple)->np.ndarray:
    """
    Generates a distance-from-edge weight array for the given image shape.

    Parameters
    ----------
    image_shape : tuple[int,int]
        Image shape of form `(rows, columns, ...)`.

    Returns
    -------
    dfe_array : numpy.array
        Numpy array of distance-from-edge values.
    """
    img_width=image_shape[1]
    img_height=image_shape[0]
    dfe_array=np.fromfunction(function=lambda y,x: np.min([x+1,y+1,img_width-x,img_height-y],axis=0),shape=(img_height,img_width))
    return dfe_array
    ### Flat Weight
def weight_flat(image_shape:tuple)->np.ndarray:
    """
    Generates a flat weight array for the given image shape.

    Parameters
    ----------
    image_shape : tuple[int,int]
        Image shape of form `(rows, columns, ...)`.

    Returns
    -------
    flat_array : numpy.array
        Numpy array of flat values.
    """
    img_width=image_shape[1]
    img_height=image_shape[0]
    flat_array=np.full(shape=(img_height,img_width),fill_value=1)
    return flat_array
    ### Normalization Array Building
def build_normalization(
    image_arrays:dict[str, array_like],
    canvas_relative_offsets:dict,
    canvas_extents:dict,
    weight:Callable
    )->np.ndarray:
    """
    Builds a normalization array.

    Parameters
    ----------
    image_arrays : dict[str, array_like],
        Dictionary of the form `"image_name":array_like`
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    weight : Callable[tuple[int,int],numpy.ndarray]
        Function that takes image shape and returns a weight array.
    
    Returns
    -------
    normalizer : numpy.ndarray
        Array with image weights added to it at their relative position.
    """
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
    image_arrays:dict[str, array_like],
    canvas_relative_offsets:dict,
    canvas_extents:dict,
    weight,
    normalizer:np.ndarray,
    return_image:bool=True,
    depth:int|None=None)->PILImage.Image | np.ndarray:
    """
    Renders a canvas with blending.

    Parameters
    ----------
    image_arrays : dict[str, array_like],
        Dictionary of the form `"image_name":array_like`
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    weight : Callable[tuple[int,int],numpy.ndarray]
        Function that takes image shape and returns a weight array.
    normalizer : numpy.ndarray
        Array with image weights added to it at their relative position.
    return_image : bool
        Wether to return an image or an array. `True` by default.
    depth : int|None
        Depth of images and canvas or `None` by default.
        If `None` depth determined from the shape of the first image in image_arrays.values().
    
    Returns
    -------
    PIL.Image.Image | numpy.ndarray
        PIL Image of the canvas or array if `return_image=False`.
    
    Notes
    -----
    Due to rounding errors this function does not currently recreate the exact original image.
    However, in testing with two and four overlapping image regions the variation from the original image was less than 1 at any pixel.
    See `tests\test_canvas_rectangular.py` for those tests.
    """


    image_2d=False
    if depth is None:
        first_image=next(iter(image_arrays.values()))
        if len(first_image.shape)==2: # image does not have depth - 1D
            depth=1
            image_2d=True
        else:
            depth=first_image.shape[2]

    canvas=np.zeros((canvas_extents["height"],canvas_extents["width"],depth))
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
        if image_2d:
            weighted_image_array=np.repeat(normed_array[:,:,np.newaxis],depth,axis=2)*image_array[:,:,np.newaxis]
        else:
            weighted_image_array=np.repeat(normed_array[:,:,np.newaxis],depth,axis=2)*image_array
        canvas[canv_slice["top"]:canv_slice["bottom"],canv_slice["left"]:canv_slice["right"]]+=weighted_image_array
    if return_image:
        if image_2d:
            return PILImage.fromarray(canvas[:,:,0].astype(np.uint8))
        else:
            return PILImage.fromarray(canvas.astype(np.uint8))
    else:
        return canvas
def render_blended_project(
    project:MISProject,
    canvas_relative_offsets:dict,
    canvas_extents:dict,
    weight,
    image_names:list[str]|None=None,
    return_image:bool=True)->PILImage.Image | np.ndarray:
    """
    Renders a canvas from a project with blending.

    Handles creation of the normalization array.

    Parameters
    ----------
    project : MISProject
        A MISProject with images.
    canvas_relative_offsets : dict[str, tuple[int, int]]
        Dictionary of the form `"image_name":(canvas-relative x, canvas-relative y)`
    canvas_extents : dict[str, int]
        Dictionary of canvas extents with keys `width` and `height`
    weight : Callable[tuple[int,int],numpy.ndarray]
        Function that takes image shape and returns a weight array.
    image_names : list[str] | None
        List of image names or `None` by default.
        If `None` all images in project will be used.
    return_image : bool
        Wether to return an image or an array. `True` by default.
    
    Returns
    -------
    PIL.Image.Image | numpy.ndarray
        PIL Image of the canvas or array if `return_image=False`.
    
    Notes
    -----
    Due to rounding errors this function does not currently recreate the exact original image.
    However, in testing with two and four overlapping image regions the variation from the original image was less than 1 at any pixel.
    See `tests\test_canvas_rectangular.py` for those tests.
    """
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
        normalizer=normalizer,
        return_image=return_image
    )

#TODO canvas_rectangular unit tests
#TODO canvas rectangular unit tests for 2D/0 depth images.