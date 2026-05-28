"""
Models for relation data.

Includes `Protocol` model: `MISRelation`

MISRelations describe the relation between two images.
This can range from "Related but no known specific relation" to "Related by these sets of points".

TODO Generate a relation tree graphic/table/something showing relation chains
"""
from statistics import mean
from typing import Protocol, runtime_checkable, Any

@runtime_checkable
class MISRelation(Protocol):
    """Protocol - Contains information relating an image pair."""
    def __init__(self,
        image_pair:list[str]|None=None,
        **relation_data):
        """Initialize a MISRelation"""
    def __str__(self)->str:
        """String Representation of the Relation."""
        ...
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        ...
    def get_relation(self,relation_type)->Any:
        """Get the relation between the images in the specified relation type."""
        ...
    def for_json(self)->dict[str,Any]:
        """Returns a dictionary compatible with `json.JSONEncoder`.
        - `relation_data["image_pair"]:list[str,str]`"""
        ...

class MISRelationReference():
    """Image pair that is related but no specific relation is known.
    - `relation_type=None`"""
    _relation_type=None
    def __init__(self,
        image_pair:tuple[str,str]|None=None,
        **relation_data):
        """Initialize a MISRelationReference"""

        if image_pair is None:
            raise ValueError("`image_pair` cannot be None.")
        self._reference: tuple[str,str]=tuple(image_pair)
            # Note: When importing from JSON this will be a list of length 2.

        self._dict=relation_data

    def __str__(self)->str:
        """String Representation of the Relation."""
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}'."
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        return tuple(self._reference)
    def get_relation(self,relation_type):
        """Get the relation between the images in the specified relation type."""
        return None
    def for_json(self)->dict[str,Any]:
        """Returns a dictionary compatible with `json.JSONEncoder`."""
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":list(self._reference),
            }

class MISRelationRectangular():
    """Contains information relating an image pair in terms of (x,y) offset.
    - `relation_type='r'`
    - rectilinear relationship A(0,0)->B(0,0)"""
    _relation_type='r'
    def __init__(self,
        image_pair:tuple[str,str]|None=None,
        rectangular:tuple[int|float,int|float]|None=None,
        **relation_data):
        """Initialize a MISRelationRectangular"""

        if image_pair is None:
            raise ValueError("`image_pair` cannot be None.")
        self._reference: tuple[str,str]=tuple(image_pair)
            # Note: When importing from JSON this will be a list of length 2.

        if rectangular is None:
            raise ValueError("`rectangular` cannot be None.")
        self._rect=tuple(rectangular)
            # Note: When importing from JSON this will be a list of length 2.

        self._dict=relation_data

    def __str__(self)->str:
        """String Representation of the Relation."""
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}' by {self._rect}."
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        return tuple(self._reference)
    def get_relation(self,relation_type):
        """Get the relation between the images in the specified relation type."""
        if relation_type=='r':
            return self._rect
        elif relation_type=='p':
            return ((self._rect,(0,0))) # the offset point in image a should match up with 0,0 in image b.
        else:
            return None
    def for_json(self)->dict[str,Any]:
        """Returns a dictionary compatible with `json.JSONEncoder`."""
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":list(self._reference),
            "rectangular":list(self._rect),
            }

class MISRelationPoints():
    """Contains information relating an image pair in terms of matching points.
    - `relation_type='p'`
    - point-based relation Ai->Bi"""
    _relation_type='p'
    def __init__(self,
        image_pair:tuple[str,str]|None=None,
        points:list[tuple[tuple[int,int],tuple[int,int]]]|None=None,
        **relation_data):
        """Initialize a MISRelationPoints"""

        if image_pair is None:
            raise ValueError("`image_pair` cannot be None.")
        self._reference: tuple[str,str]=tuple(image_pair)
            # Note: When importing from JSON this will be a list of length 2.

        if points is None:
            raise ValueError("`points` cannot be None.")
        self._points: list[tuple[tuple[int,int],tuple[int,int]]]=list(points)

        self._dict=relation_data
    def __str__(self)->str:
        """String Representation of the Relation."""
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}' by {self._points}."
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        return tuple(self._reference)
    def get_relation(self,relation_type):
        """Get the relation between the images in the specified relation type."""
        if relation_type=='r':
            #TODO rework this as numpy array operation.
            points_a=[x[0] for x in self._points]
            points_b=[x[1] for x in self._points]
            shift=[[b[0]-a[0],b[1]-a[1]] for a,b in zip(points_a,points_b)]
            x_shift=int(mean([x[0] for x in shift]))
            y_shift=int(mean([x[1] for x in shift]))
            return (x_shift,y_shift)
        elif relation_type=='p':
            return self._points
        else:
            return None
    def for_json(self)->dict[str,Any]:
        """Returns a dictionary compatible with `json.JSONEncoder`."""
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":list(self._reference),
            "points":self._points
            }


relation_types={
    MISRelationReference._relation_type:MISRelationReference,
    MISRelationRectangular._relation_type:MISRelationRectangular,
    MISRelationPoints._relation_type:MISRelationPoints,
}
def setup_relation(**relation_data)->MISRelation:
    return relation_types[relation_data["relation_type"]](**relation_data)
