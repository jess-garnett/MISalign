"""
Difference- & Overlap-based Rectangular Alignment Module
"""

import numpy as np
from collections.abc import Callable, Container
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
#TODO add better handling for different image sizes.
#TODO add tests for axis_span


def overlap_spans(offset_vector:tuple[int,int],a_shape:tuple[int,int],b_shape:tuple[int,int])->tuple[tuple[tuple[int,int],tuple[int,int]],tuple[tuple[int,int],tuple[int,int]]]:
    """
    Calculates overlapping spans of two images given an offset vector and shapes.

    Parameters
    ----------
    offset_vector : tuple[int,int]
        The vector from the top left corner of image a to the top left corner of image b.
        In (x,y) order.
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
#TODO add tests for overlap_spans

