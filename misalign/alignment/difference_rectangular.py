"""
Difference- & Overlap-based Automated Rectangular Alignment Module
"""

import numpy as np
from collections.abc import Callable
from typing import runtime_checkable, Protocol
from misalign.model.image import MISImage
from misalign.model.relation import MISRelation

def axis_span(offset_vector:int,a_shape:int,b_shape:int)->tuple[tuple[int,int],tuple[int,int]]:
    """
    Calculates overlapping spans of two objects on a single axis given an offset vector and object shapes.

    Parameters
    ----------
    offset_vector : int
        The vector from the low value of a to the low value of b.
        i.e. the horizontal or vertical offset between objects a and b.
    a_shape : int
        The size of object a in the axis.
        i.e. the width or length of object a.
    b_shape : int
        The size of object b in the axis.
        i.e. the width or length of object b.

    Returns
    -------
    a_span, b_span : tuple[tuple[int,int],tuple[int,int]]
        Pair of start:stop spans for object a and object b.
    """
    if offset_vector==0: # If there is no offset, then span is based on smaller image.
        a_span=(0,min(a_shape,b_shape))
        b_span=(0,min(a_shape,b_shape))
    elif offset_vector > 0: # If there is a positive offset.
        a_span=(0,a_shape-offset_vector)
        b_span=(offset_vector,a_shape)
    elif offset_vector < 0: # If there is a negative offset.
        a_span=(-offset_vector,b_shape)
        b_span=(0,b_shape+offset_vector)
    else:
        raise ValueError()
    return a_span,b_span


def overlap_spans(offset_vector:tuple[int,int],a_shape:tuple[int,int],b_shape:tuple[int,int])->tuple[tuple[tuple[int,int],tuple[int,int]],tuple[tuple[int,int],tuple[int,int]]]:
    """
    Calculates overlapping spans of two images given an offset vector and shapes.

    Parameters
    ----------
    offset_vector : tuple[int,int]
        The vector from the top left corner of image a to the top left corner of image b.
        In (x,y) order.
        Example: image b's top left corner is at image a's bottom right corner: `offset=(-width_a,-height_a)`
    a_shape : tuple[int,int]
        The shape of image a.
        In (row,column) / (y,x) order.
    b_shape : tuple[int,int]
        The shape of image b.
        In (row,column) / (y,x) order.

    Returns
    -------
    (ax_span,ay_span),(bx_span,by_span) : tuple[tuple[tuple[int,int],tuple[int,int]],tuple[tuple[int,int],tuple[int,int]]]
        Tuple of image a and image b spans. Each a tuple of x and y spans. Each span is a start:stop pair.
    """
    if not all([offset_vector[0]>-b_shape[1], # valid in -x (b to the left of a)
                offset_vector[0]<a_shape[1], # valid in +x (a to the left of b)
                offset_vector[1]>-b_shape[0], # valid in -y (b above a)
                offset_vector[1]<a_shape[0]]): # valid in +y (a above b)
        raise ValueError("These images do not overlap")
    ax_span,bx_span=axis_span(offset_vector[0],a_shape[1],b_shape[1])
    ay_span,by_span=axis_span(offset_vector[1],a_shape[0],b_shape[0])
    return (ax_span,ay_span),(bx_span,by_span)


def overlap_evaluate(
        array_a:np.ndarray,
        array_b:np.ndarray,
        offset_ab:tuple[int,int]|np.ndarray,
        metric:Callable[[np.ndarray,np.ndarray],float]
        )->float:
    """
    Evaluates overlap between image a and image b based on a translation offset and a metric.
    
    Parameters
    ----------
    array_a : np.ndarray
        Numpy array of image a.
    array_b : np.ndarray
        Numpy array of image b.
    offset_ab : tuple[int,int] | np.ndarray
        The vector from the top left corner of image a to the top left corner of image b.
        In (x,y) order.
        Example: image b's top left corner is at image a's bottom right corner: `offset=(-width_a,-height_a)`
    metric : Callable[[np.ndarray,np.ndarray],float]
        Function that takes two numpy arrays and returns a value describing some aspect of them.
        Example: Function which takes the difference of the overlap regions and then squares it and gets the mean value.

    Returns
    -------
    overlap_metric : float
        Result of `metric(overlap_a,overlap_b)`.
    """
    ## Find overlap spans
    a_spans,b_spans=overlap_spans(tuple(offset_ab),array_a.shape,array_b.shape)
    ## Extract overlap regions
    overlap_a=array_a[a_spans[1][0]:a_spans[1][1],a_spans[0][0]:a_spans[0][1]]
    overlap_b=array_b[b_spans[1][0]:b_spans[1][1],b_spans[0][0]:b_spans[0][1]]
    ## Get overlap metric
    return metric(overlap_a,overlap_b)


def overlap_difference(
        array_a:np.ndarray,
        array_b:np.ndarray,
        offset_ab:tuple[int,int]|np.ndarray,
        )->np.ndarray:
    """
    Calculate the difference between overlapping regions of image a and image b given a translational offset.
    
    Parameters
    ----------
    array_a : np.ndarray
        Numpy array of image a.
        Note: Unsigned integer arrays are converted to float.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays are converted to float.
    offset_ab : tuple[int,int] | np.ndarray
        The vector from the top left corner of image a to the top left corner of image b.
        In (x,y) order.
        Example: image b's top left corner is at image a's bottom right corner: `offset=(-width_a,-height_a)`

    Returns
    -------
    difference : np.ndarray
        Difference (a-b) of the overlap between image a and image b.
    """
    ## Find overlap spans
    a_spans,b_spans=overlap_spans(tuple(offset_ab),array_a.shape,array_b.shape)
    ## Extract overlap regions
    overlap_a=array_a[a_spans[1][0]:a_spans[1][1],a_spans[0][0]:a_spans[0][1]]
    overlap_b=array_b[b_spans[1][0]:b_spans[1][1],b_spans[0][0]:b_spans[0][1]]

    if np.isdtype(overlap_a.dtype,kind='unsigned integer'):
        overlap_a=overlap_a.astype(np.float32)
    if np.isdtype(overlap_b.dtype,kind='unsigned integer'):
        overlap_b=overlap_b.astype(np.float32)

    return overlap_a-overlap_b


def metric_difference_squared_mean(overlap_a:np.ndarray,overlap_b:np.ndarray)->float:
    """
    Calculates the mean of the squared difference of two arrays.

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays are converted to float.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays are converted to float.

    Returns
    -------
    overlap_metric : float
        Result of taking the mean of the square of the difference of the arrays.
    """
    if np.isdtype(overlap_a.dtype,kind='unsigned integer'):
        overlap_a=overlap_a.astype(np.float32)
    if np.isdtype(overlap_b.dtype,kind='unsigned integer'):
        overlap_b=overlap_b.astype(np.float32)

    return np.mean((overlap_a-overlap_b)**2)
    
def metric_difference_absolute_mean(overlap_a:np.ndarray,overlap_b:np.ndarray)->float:
    """
    Calculates the mean of the absolute difference of two arrays.

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays are converted to float.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays are converted to float.

    Returns
    -------
    overlap_metric : float
        Result of taking the mean of the absolute value of the difference of the arrays.
    """
    if np.isdtype(overlap_a.dtype,kind='unsigned integer'):
        overlap_a=overlap_a.astype(np.float32)
    if np.isdtype(overlap_b.dtype,kind='unsigned integer'):
        overlap_b=overlap_b.astype(np.float32)

    diff=overlap_a-overlap_b
    return np.mean(np.abs(diff,out=diff))


def strategy_scaled_grid(
        array_a:np.ndarray,
        array_b:np.ndarray,
        initial_offset:tuple[int,int],
        strategy_grid_scale:int,
        strategy_max_size:int=5,
        metric:Callable[[np.ndarray,np.ndarray],float]=metric_difference_squared_mean,)->dict:
    """
    Sparse grid search strategy for difference gradient alignment.
    
    Parameters
    ----------
    array_a : np.ndarray
        Numpy array of image a.
        Note: Unsigned integer arrays are converted to float.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays are converted to float.
    initial_offset : tuple[int,int]
        An initial estimate for the vector from the top left corner of image a to the top left corner of image b.
        In (x,y) order.
        Example: image b's top left corner is at image a's bottom right corner: `offset=(-width_a,-height_a)`
    strategy_grid_scale : int
        Distance to space out search grid by.
    strategy_max_size : int
        Number of steps to check on each side of initial offset or `5` by default.
        Example: `...=5` means an 11x11 set of offsets will be searched.
    metric : Callable[[np.ndarray,np.ndarray],float]
        Function that takes two numpy arrays and returns a value describing some aspect of them or `metric_difference_squared_mean` by default.
        Example: Function which takes the difference of the overlap regions and then squares it and gets the mean value.

    Returns
    -------
    strategy_results : dict
        Dictionary with results of sparse grid search.
        `grid` : np.ndarray
            Offsets that were searched.
        `grid_results` : np.ndarray
            Metric value at matching offset in `grid`.
        `optimized_offset` : tuple[int,int]
            Optimized offset based on minimum in metric value.
        `initial_offset` : tuple[int,int]
            Initial offset provided to strategy.
    """
    grid_shape=(1+strategy_max_size*2,1+strategy_max_size*2)
    grid=np.fromfunction(lambda y,x: np.array([initial_offset[0]+(strategy_grid_scale*(x-strategy_max_size)),
                                                                                            initial_offset[1]+(strategy_grid_scale*(y-strategy_max_size))]),
                                                                                            shape=grid_shape,dtype=int)
    grid_results=np.full(grid_shape,np.nan)
    grid_indeces=np.fromfunction(lambda row,col: np.array([row,col]),shape=grid_shape,dtype=int).reshape(2,-1)

    for i,grid_index in enumerate(grid_indeces.T):
        check_offset=grid[:,grid_index[0],grid_index[1]]
        grid_results[grid_index[0],grid_index[1]]=overlap_evaluate(array_a,array_b,
            offset_ab=check_offset,
            metric=metric)
    optimized_location=grid_results.reshape(-1).argmin()
    optimized_offset=tuple([int(value) for value in grid[:,grid_indeces[0][optimized_location],grid_indeces[1][optimized_location]]])
    return {
        "grid":grid,
        "grid_results":grid_results,
        "optimized_offset":optimized_offset,
        "initial_offset":initial_offset
        }

def strategy_full_grid(
        array_a:np.ndarray,
        array_b:np.ndarray,
        initial_offset:tuple[int,int],
        strategy_max_size:int=5,
        metric:Callable[[np.ndarray,np.ndarray],float]=metric_difference_squared_mean,)->dict:
    """
    Full grid search strategy for difference gradient alignment.

    Convenience function that wraps `strategy_scaled_grid` with `strategy_grid_scale=1`.
    
    Parameters
    ----------
    array_a : np.ndarray
        Numpy array of image a.
        Note: Unsigned integer arrays are converted to float.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays are converted to float.
    initial_offset : tuple[int,int]
        An initial estimate for the vector from the top left corner of image a to the top left corner of image b.
        In (x,y) order.
        Example: image b's top left corner is at image a's bottom right corner: `offset=(-width_a,-height_a)`
    strategy_max_size : int
        Number of steps to check on each side of initial offset or `5` by default.
        Example: `...=5` means an 11x11 set of offsets will be searched.
    metric : Callable[[np.ndarray,np.ndarray],float]
        Function that takes two numpy arrays and returns a value describing some aspect of them or `metric_difference_squared_mean` by default.
        Example: Function which takes the difference of the overlap regions and then squares it and gets the mean value.

    Returns
    -------
    strategy_results : dict
        Dictionary with results of full grid search.
        `grid` : np.ndarray
            Offsets that were searched.
        `grid_results` : np.ndarray
            Metric value at matching offset in `grid`.
        `optimized_offset` : tuple[int,int]
            Optimized offset based on minimum in metric value.
        `initial_offset` : tuple[int,int]
            Initial offset provided to strategy.
    """
    return strategy_scaled_grid(array_a=array_a,
                                array_b=array_b,
                                initial_offset=initial_offset,
                                strategy_grid_scale=1,
                                strategy_max_size=strategy_max_size,
                                metric=metric)


## array-like class
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


def filter_simple(image:array_like)->np.ndarray:
    """
    Filter to get an array from an array-like and convert it to `np.int16`.
    
    Parameters
    ----------
    image : array_like
        Array-like image.

    Returns
    -------
    array : np.ndarray
        Converted array.
    """
    return np.asarray(image).astype(np.float32)
def filter_rgb_gray_mean(image:array_like)->np.ndarray:
    """
    Filter to get an array from an array-like, reduce it from RGB to grayscale by taking the mean, and convert it to `np.int16`.
    
    Parameters
    ----------
    image : array_like
        Array-like image with shape (Rows,Columns,Depth).

    Returns
    -------
    array : np.ndarray
        Converted array.
    """
    return np.mean(image,axis=-1).astype(np.float32)

def difference_gradient_analysis(
        image_a:MISImage|array_like,
        image_b:MISImage|array_like,
        relation:MISRelation|tuple[int,int]|None,
        strategy:Callable[...,dict]=strategy_full_grid,
        metric:Callable[[np.ndarray,np.ndarray],float]=metric_difference_squared_mean,
        filter:Callable[[array_like],np.ndarray]=filter_simple,
        **kwargs)->dict:
    """
    Uses a metric to evaluate overlaps of a pair of images at multiple offsets to identify the best offset.

    Note: This functions primary purpose is to prepare MISImage and MISRelation objects to be passed to a strategy function.

    Parameters
    ----------
    strategy : Callable[...,dict]
        Function that takes keyword arguments `array_a`, `array_b`, `initial_offset`, `metric`, and all other `kwargs`.
        Returns a dictionary of results that must include `optimized_offset`.
        `strategy_full_grid` by default.
    metric : Callable[[np.ndarray,np.ndarray],float]
        Function that takes two numpy arrays and returns a value describing some aspect of them.
        `metric_difference_squared_mean` by default.
        Example: Function which takes the difference of the overlap regions and then squares it and gets the mean value.
    filter : Callable[[array_like],np.ndarray]
        Filter to convert array_like to array, convert dtypes, or apply other effects such as gaussian or median filters.
        `filter_simple` by default.
    kwargs
        All keyword arguments are passed to the strategy function.

    dga_results : dict
        Dictionary with results of difference gradient alignment. Contents will depend on strategy used.
        `grid` : np.ndarray : optional
            Offsets that were searched.
        `grid_results` : np.ndarray : optional
            Metric value at matching offset in `grid`.
        `optimized_offset` : tuple[int,int]
            Optimized offset based on minimum in metric value.
        `initial_offset` : tuple[int,int] | None : optional
            Initial offset provided to strategy.
    """
    ## Get image arrays
    image_a_array:np.ndarray=filter(image_a)
    image_b_array:np.ndarray=filter(image_b)

    ## Get initial relation
    if isinstance(relation,MISRelation):
        try:
            initial_rectangular_relation=relation.get_relation('r')
        except ValueError:
            initial_rectangular_relation=None
    elif isinstance(relation,tuple):
        initial_rectangular_relation=relation
    else:
        initial_rectangular_relation=None

    return strategy(
        array_a=image_a_array,
        array_b=image_b_array,
        initial_offset=initial_rectangular_relation,
        metric=metric,
        **kwargs)

#TODO make `filter_...` and `metric_...` kwargs passable through to their respective use case.

#TODO potential strategy: `local_minima`
    # search starts with +1/-1 around `relation` and then moves to the observed minima and
    # another +1/-1 is searched until a local minima is found.

#TODO potential strategy: `gaussian_minimization`
    # gaussian process regression is used to fit the minimization trend and efficiently reach the minimum value.

#TODO consider downscaling for strategy/processing.