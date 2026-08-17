"""
Difference- & Overlap-based Automated Rectangular Alignment Module
"""

import numpy as np
from collections.abc import Callable
from typing import runtime_checkable, Protocol
import logging

from misalign.model.image import MISImage
from misalign.model.relation import MISRelation

"""
Axis and Overlap Functions
"""

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
        Note: Unsigned integer arrays may underflow and should not be used.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays may underflow and should not be used.
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

    return overlap_a-overlap_b

"""
Basic Metric Functions
"""

def metric_difference_squared_mean(overlap_a:np.ndarray,overlap_b:np.ndarray)->float:
    """
    Calculates the mean of the squared difference of two arrays.

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.

    Returns
    -------
    overlap_metric : float
        Result of taking the mean of the square of the difference of the arrays.
    """

    return np.mean((overlap_a-overlap_b)**2)
    
def metric_difference_absolute_mean(overlap_a:np.ndarray,overlap_b:np.ndarray)->float:
    """
    Calculates the mean of the absolute difference of two arrays.

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.

    Returns
    -------
    overlap_metric : float
        Result of taking the mean of the absolute value of the difference of the arrays.
    """

    diff=overlap_a-overlap_b
    return np.mean(np.abs(diff,out=diff))

"""
Basic Strategy Functions
"""

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
        Note: Unsigned integer arrays may underflow and should not be used.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays may underflow and should not be used.
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
        Note: Unsigned integer arrays may underflow and should not be used.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays may underflow and should not be used.
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

#TODO potential strategy: `local_minima`
    # search starts with +1/-1 around `relation` and then moves to the observed minima and
    # another +1/-1 is searched until a local minima is found.

#TODO potential strategy: `gaussian_minimization`
    # gaussian process regression is used to fit the minimization trend and efficiently reach the minimum value.

#TODO consider downscaling for strategy/processing.


"""
Filter Functions
"""

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
    Filter to get an array from an array-like and convert it to `np.float32`.
    
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
    Filter to get an array from an array-like, reduce it from RGB to grayscale by taking the mean, and convert it to `np.float32`.
    
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

"""
Difference Gradient Analysis Function
"""

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

"""
Result Visualization Functions
"""

#TODO plotting functions from `difference_gradient.py`

"""
Difference Gradient Analysis Metric and Strategy Functions
"""

try:
    # import scipy
    from scipy.interpolate import NearestNDInterpolator
except ImportError:
    _if_scipy = False
else:
    _if_scpy = True

try:
    import skimage
    # from skimage.morphology import skeletonize, dilation, footprints
    # from skimage.filters import gaussian
except ImportError:
    _if_scipy = False
else:
    _if_scpy = True

### Difference Gradient Analysis Full Search Metrics

def metric_highlow_inverse_norm(overlap_a:np.ndarray,overlap_b:np.ndarray,modifier:int=16)->float:
    """
    Calculates the inverse of (max-min)/modifier for the overlap region.

    Weights against low-feature overlapping regions. Result will be on the interval (0,1]

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.
    modifier : int
        Modifier to divide the difference of max and min by.
        The higher the modifier the greater the difference needed to reduce the metric.
        Example: `modifier=16` difference of 16 is metric of 1, difference of 80 is metric of 0.2.
        Example: `modifier=8` difference of 16 is metric of 0.5, difference of 80 is metric of 0.1.

    Returns
    -------
    overlap_metric : float
        Result of taking the inverse of the difference of max and min of each overlap divided by the modifier.
    """

    def metric(overlap):
        return  np.min([1/((np.max(overlap)-np.min(overlap))/modifier),1])
        # variation of 16 > value of 1 > variation of 32 > value of 1/2 > etc. variation of 80 > 0.2
    return np.max([metric(overlap_a),metric(overlap_b)])


def metric_difference_squared_mean_norm(overlap_a:np.ndarray,overlap_b:np.ndarray,modifier=1)->float:
    """
    Calculates the mean of the squared difference of two arrays.

    Weights against misalignment in features. Result will be on the interval [0,1]

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.
    modifier : int
        Modifier to multiply the mean by.

    Returns
    -------
    overlap_metric : float
        Result of taking the mean of the square of the difference of the arrays.
    """

    return np.min([modifier*np.mean((overlap_a-overlap_b)**2)/(255**2),1])


def metric_difference_absolute_mean_norm(overlap_a:np.ndarray,overlap_b:np.ndarray,modifier=1)->float:
    """
    Calculates the mean of the absolute difference of two arrays.

    Weights against misalignment in features. Result will be on the interval [0,1]

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.
    modifier : int
        Modifier to multiply the mean by.

    Returns
    -------
    overlap_metric : float
        Result of taking the mean of the absolute value of the difference of the arrays.
    """
        
    diff=overlap_a-overlap_b
    return np.min([modifier*np.mean(np.abs(diff,out=diff))/255,1])


def metric_difference_max_norm(overlap_a:np.ndarray,overlap_b:np.ndarray,modifier=1)->float:
    """
    Calculates the max of the absolute difference of two arrays.

    Weights strongly against misalignment in features. Result will be on the interval [0,1]

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.
    modifier : int
        Modifier to multiply the mean by.

    Returns
    -------
    overlap_metric : float
        Result of taking the max of the difference of the arrays.
    """

    diff=(overlap_a-overlap_b)
    np.abs(diff,out=diff)
    return np.min([np.max(diff)/(255),1])

def metric_linear_edge_penalty(overlap_a:np.ndarray,overlap_b:np.ndarray,penalty:float=0.2,distance:float=300):
    """
    Calculates a linear penalty based on the shape of the overlap region. Thinner regions higher penalties.

    Weights against low-overlap distances. Result will be on the interval [0,1]

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
    overlap_b : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Not used. Only overlap_a's shape is considered.
    Penalty : float | int
        Maximum value for penalty.
    distance : float | int
        Distance at which penalty should reach 0.
        Note: Linear gradient is used between this distance and 1 pixel overlap.

    Returns
    -------
    overlap_metric : float
        Result of linear penalty.
    """
    distance_from_edge=np.min(overlap_a.shape[:2])
    if distance_from_edge>distance:
        return 0
    else:
        return (1-(distance_from_edge/distance))*penalty

def metric_combined_simple_norm(overlap_a:np.ndarray,overlap_b:np.ndarray,modifier_max:int=1,modifier_squared:int=50,modifier_highlow:int=1):
    """
    Simple combination of `metric_difference_max_norm`, `metric_difference_squared_mean_norm`, and `metric_highlow_inverse_norm`.

    Weights against misalignment in features and against low feature regions. Result will be on the interval (0,1]

    Parameters
    ----------
    overlap_a : np.ndarray
        Numpy array of the overlap region in image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    overlap_a : np.ndarray
        Numpy array of the overlap region in image b.
        Note: Unsigned integer arrays may underflow and should not be used.
    modifier_max : int
        Modifier to multiply the `metric_difference_max_norm` by.
    modifier_squared : int
        Modifier to multiply the `metric_difference_squared_mean_norm` by.
    modifier_highlow : int
        Modifier to multiply the `metric_highlow_inverse_norm` by.

    Returns
    -------
    overlap_metric : float
        Result of combining all three metrics.
    """
    
    return (metric_difference_max_norm(overlap_a,overlap_b,modifier=modifier_max)+
        metric_difference_squared_mean_norm(overlap_a,overlap_b,modifier=modifier_squared)+
        metric_highlow_inverse_norm(overlap_a,overlap_b,modifier=modifier_highlow)
        )/3
        
### Difference Gradient Analysis Full Search Strategy

def interpolate_nearest_neighbor(
    grid:np.ndarray,
    grid_results:np.ndarray,
    )->np.ndarray:
    interp=NearestNDInterpolator(
        np.array([
            grid[0].flatten()[~np.isnan(grid_results.flatten())],
            grid[1].flatten()[~np.isnan(grid_results.flatten())]]).T,
        grid_results.flatten()[~np.isnan(grid_results.flatten())])
    interp_results=interp(grid[0].flatten(),grid[1].flatten()).reshape(grid_results.shape)
    return interp_results

#TODO handle initial offset.
def strategy_full_search_grid(
        array_a:np.ndarray,
        array_b:np.ndarray,
        initial_offset:tuple[int,int]|None=None,
        metric:Callable[[np.ndarray,np.ndarray],float]=metric_combined_simple_norm,
        strategy_interpolate:Callable=interpolate_nearest_neighbor,
        strategy_edge_avoid=20,
        strategy_logger:logging.Logger=logging.getLogger(),
        strategy_initial_grid_number=20,
        strategy_metric_comparison:float=1,
        **kwargs)->dict:
    """
    Full search grid strategy.

    Strategy uses sparse grids and quantile-based refinement to search entire rectangular offset space.
    It is recommended to calibrate parameters on a few known offsets within a data set.
    
    Parameters
    ----------
    array_a : np.ndarray
        Numpy array of image a.
        Note: Unsigned integer arrays may underflow and should not be used.
    array_b : np.ndarray
        Numpy array of image b.
        Note: Unsigned integer arrays may underflow and should not be used.
    initial_offset : tuple[int,int] | None
        An initial estimate for the vector from the top left corner of image a to the top left corner of image b or Default `None`.
        In (x,y) order.
        Example: image b's top left corner is at image a's bottom right corner: `offset=(-width_a,-height_a)`
    metric : Callable[[np.ndarray,np.ndarray],float]
        Function that takes two numpy arrays and returns a value describing some aspect of them or `metric_difference_squared_mean` by default.
        Example: Function which takes the difference of the overlap regions and then squares it and gets the mean value.
    strategy_interpolate : Callable[[np.ndarray,np.ndarray],np.ndarray]
        Function that takes grid of offsets and grid of results and un-checked `np.nan` and interpolates for all `np.nan` values.
        `interpolate_nearest_neighbor` by default.
    strategy_edge_avoid : int
        Minimum amount of overlap to require between images. Default is 20.
    strategy_logger : logging.Logger
        Logger to use for logging full search steps. By Default root logger.
    strategy_initial_grid_number : int
        Number of points to use per direction in initial sparse grid. Default is 20.
        Used in simple search progression.
        Overridden by kwarg `strategy_full_search_progression`.
    strategy_metric_comparison : float
        Value of metric that is considered likely to be a true solution.
        Used in simple search progression.
        Overridden by kwarg `strategy_full_search_progression`.
    kwargs
        `strategy_full_search_progression` : list[dict]

    Returns
    -------
    strategy_results : dict
        Dictionary with results of sparse grid search.
        `grid` : np.ndarray
            Offsets that were searched.
        `grid_results` : np.ndarray
            Metric value at matching offset in `grid`.
        `interp_results` : np.ndarray
            Interpolation of results to grid.
        `optimized_offset` : tuple[int,int]
            Optimized offset based on minimum in metric value.
    """

    # Calculate full search size
    x_min: int=-array_b.shape[1]+1+strategy_edge_avoid
    x_max: int=array_a.shape[1]-strategy_edge_avoid
    y_min: int=-array_b.shape[0]+1+strategy_edge_avoid
    y_max: int=+array_a.shape[0]-strategy_edge_avoid

    # Generate grid of offsets
    grid: np.ndarray=np.stack(
        arrays=np.meshgrid(
            np.arange(x_min,x_max),
            np.arange(y_min,y_max)
            )
        )
    # Get column and row indices for grid of offsets
    grid_columns,grid_rows=np.meshgrid(
            np.arange(0,grid.shape[2]),
            np.arange(0,grid.shape[1]),
            )
    # Create `nan`-filled array for results of checking offsets
    grid_results=np.full(grid.shape[1:],np.nan)
    # Create `nan`-filled array as place-holder for interpolation
    interp_results=np.full(grid.shape[1:],np.nan)


    # Define function that applies metric at iy,ix and updates grid_results[iy,ix]
    def check_offset(iy,ix):
        grid_results[iy,ix]=overlap_evaluate(
                    array_a=array_a,
                    array_b=array_b,
                    offset_ab=grid[:,iy,ix],
                    metric=metric)
    

    def initial_grid_check(initial_grid_number:int):
        # Offsets that match grid columns.
        match_col:np.ndarray=np.isin(
            element=grid_columns,
            test_elements=np.linspace(start=0,stop=grid.shape[2]-1,num=initial_grid_number).astype(int))
        # Offsets that match grid rows.
        match_row:np.ndarray=np.isin(
            element=grid_rows,
            test_elements=np.linspace(start=0,stop=grid.shape[1]-1,num=initial_grid_number).astype(int))
        # Positions that match initial grid spacing.
        match_all:np.ndarray=np.all([match_col,match_row],axis=0)

        # Log initial check.
        strategy_logger.info(f"Initial Number: {initial_grid_number} Checking: {np.sum(match_all):,} / {grid_results.size:,}")
        # print(f"Initial Number: {strategy_initial_grid_number} Checking: {np.sum(match_all)} / {grid_results.size:,}")

        # Check initial set of offsets.
        for iy,ix in zip(grid_rows[match_all].flatten(),grid_columns[match_all].flatten()):
            check_offset(iy,ix)

        # Interpolate on initial set of offset results.
        return strategy_interpolate(grid=grid,grid_results=grid_results)

    # Define function that does quantile and grid filtering and checking.
    def quantile_filter_check(
        interp_results:np.ndarray,
        quantile:float,
        number:int|None=None,
        spacing:int|None=None,
        skeleton:bool=False,
        check_all=1000):
        #TODO could add a maximum number here so if this is selecting i.e. 10,000 points it reduce to 1000.

        # Quantile for threshold.
        quantile_cutoff=np.quantile(interp_results,quantile)

        # Interpolation results within quantile threshold.
        match_quantile:np.ndarray=interp_results<=quantile_cutoff

        # Offsets that have not been checked.
        match_unchecked:np.ndarray=np.isnan(grid_results)

        # Offsets that have not been checked and are within quantile threshold.
        match_remaining=np.all([match_quantile,match_unchecked],axis=0)

        # If the total remaining positions are less than the `check_all` threshold, just check all of them.
        if np.sum(match_remaining)<=check_all:
            match_all=match_remaining
            strategy_logger.info(f"Quantile: {quantile}/{quantile_cutoff:0.3f} - Checking all: {np.sum(match_all):,} / {np.sum(match_remaining):,}")
        
        # Otherwise, apply reducing filter and then check.
        else:
            # Reducing filter based on an evenly spaced grid with a certain number of points.
        
            #TODO consider splitting this into grid matching function > take a row array and a col array to match against > would also integrate initial grid
            if number is not None:
                # Offsets that match grid columns.
                match_col=np.isin(element=grid_columns,
                    test_elements=np.linspace(start=0,stop=grid.shape[2]-1,num=number).astype(int))

                # Offsets that match grid rows.
                match_row=np.isin(element=grid_rows,
                    test_elements=np.linspace(start=0,stop=grid.shape[1]-1,num=number).astype(int))

                # Offsets that match grid search positions.
                match_all=np.all([match_col,match_row,match_remaining],axis=0)
                
                strategy_logger.info(f"Quantile: {quantile}/{quantile_cutoff:0.3f} - Checking: {np.sum(match_all):,} / {np.sum(match_remaining):,}")
            elif spacing is not None:
                # Offsets that match grid columns.
                match_col=np.isin(element=grid_columns,
                    test_elements=np.arange(0,stop=grid.shape[2]-1,step=spacing).astype(int))

                # Offsets that match grid rows.
                match_row=np.isin(element=grid_rows,
                    test_elements=np.arange(0,stop=grid.shape[1]-1,step=spacing).astype(int))

                # Offsets that match grid search positions.
                match_all=np.all([match_col,match_row,match_remaining],axis=0)

                strategy_logger.info(f"Quantile: {quantile}/{quantile_cutoff:0.3f} Spacing: {spacing} Checking: {np.sum(match_all)} / {np.sum(match_remaining):,}")
            elif skeleton:
                # Get spine of quantile filtered region(s).
                skeleton_smooth=skimage.filters.gaussian(interp_results,sigma=10) # Smooth out interpolation to avoid excess branches.
                skeleton_binary=skeleton_smooth<quantile_cutoff # Smooth interpolation results within quantile threshold.
                skeleton_spine=skimage.morphology.skeletonize(skeleton_binary) # Spine of skeleton
                match_skeleton=skimage.morphology.dilation(skeleton_spine,skimage.morphology.footprints.disk(1)) #expanded

                # Overlay spacing 3 on 3 wide line to sparse out line slightly
                spacing=3
                # Offsets that match grid columns.
                match_col=np.isin(element=grid_columns,
                    test_elements=np.arange(0,stop=grid.shape[2]-1,step=spacing).astype(int))

                # Offsets that match grid rows.
                match_row=np.isin(element=grid_rows,
                    test_elements=np.arange(0,stop=grid.shape[1]-1,step=spacing).astype(int))

                # Offsets in spine without repeats
                match_all=np.all([match_col,match_row,match_skeleton,match_remaining],axis=0) #match_col,match_row,
                strategy_logger.info(f"Quantile: {quantile}/{quantile_cutoff:0.3f} - Skeleton - Checking: {np.sum(match_all)} / {np.sum(match_skeleton):,}")
            else:
                #TODO decide if this should be check all behavior implicitely or should be an error for not including number/spacing
                # If neighter number or spacing are given then brute force check all remaining offsets.
                match_all=match_remaining
                strategy_logger.info(f"Quantile: {quantile}/{quantile_cutoff:0.3f} - Checking all: {np.sum(match_all)} / {np.sum(match_remaining):,}")
        
        # Check set of offsets
        for iy,ix in zip(grid_rows[match_all].flatten(),grid_columns[match_all].flatten()):
            check_offset(iy,ix)

        # Return Interpolation
        return strategy_interpolate(
            grid=grid,
            grid_results=grid_results
            )
    
    # Strategy to use for full search.
    if "strategy_full_search_progression" in kwargs:
        strategy_full_search_progression=kwargs["strategy_full_search_progression"]
    else:
        strategy_full_search_progression: list[dict]=[
            dict(initial_grid_number=strategy_initial_grid_number),
            dict(quantile=0.1,spacing=32,), #number=100
            dict(quantile=0.01,spacing=16,), #number=200
            dict(quantile=0.001,spacing=8,), #number=400
            dict(quantile=0.0001,spacing=4,), #number=800
            dict(compare=strategy_metric_comparison),
            dict(quantile=0.05,skeleton=True,),
            dict(quantile=0.0001,spacing=4,), #number=800
            dict(compare=strategy_metric_comparison),
            dict(quantile=0.05,spacing=16,), #number=200
            dict(quantile=0.005,spacing=8,), #number=400
            dict(quantile=0.0005,spacing=4,), #number=800
            dict(compare=strategy_metric_comparison),
            dict(quantile=0.001,spacing=4,check_all=10000), #number=800
            ]

    # Looping through full search progression
    for step in strategy_full_search_progression:

        if "initial_grid_number" in step:
            interp_results=initial_grid_check(initial_grid_number=step["initial_grid_number"])
        elif "quantile" in step:
            interp_results=quantile_filter_check(
                interp_results=interp_results,
                **step
                )
        elif "compare" in step:
            # If minimum metric is less than compare threshold, a near-true-solution has probably been found.
                # Do any final search and then break the progression.
                # If not then continue.
            if np.nanmin(grid_results)<=step["compare"]:
                #TODO potentially a final search to make sure area near minimum point has been checked.
                    # possible use full grid 5x5 on optimized location and inject into the grid results.
                strategy_logger.info(f"Metric: {np.nanmin(grid_results):0.3f} is below threshold {step["compare"]} - Stopping.")
                break
            else:
                strategy_logger.info(f"Metric: {np.nanmin(grid_results):0.3f} is above threshold {step["compare"]} - Continuing.")
                pass
        elif "search_function" in step:
            interp_results=step["search_function"](step,locals())
        elif "compare_function" in step:
            compare_result=step["compare_function"](step,locals())
            if compare_result:
                break
            else:
                pass
        else:
            strategy_logger.warning(msg=f"Encountered unknown strategy step: {step}")
            pass
            

    # Get indeces of optimized offset
    optimized_location:tuple=np.unravel_index(np.nanargmin(grid_results), grid_results.shape)
    # Get optimized offset
    optimized_offset:tuple[int,int]=tuple(grid[:,optimized_location[0],optimized_location[1]].tolist())

    strategy_logger.info(f"Optimized metric: {np.nanmin(grid_results):0.3f}")

    #TODO add option for including initial regular relation in initial grid OR in interpolation at the very end.

    return {
        "grid":grid,
        "grid_results":grid_results,
        "interp_results":interp_results,
        "optimized_offset":optimized_offset,
        }