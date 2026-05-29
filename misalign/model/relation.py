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
    """Protocol - Relation between image pairs."""
    def __init__(self,
        image_pair:tuple[str,str],
        **relation_data):
        """
        Initialize a MISRelation.

        Parameters
        ----------
        image_pair : tuple[str,str]
            Pair of image name strings.
        **relation_data : kwargs
            Required kwargs vary depending on class of MISRelation.
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """
    def __str__(self)->str:
        """
        String representation of the Relation.

        Returns
        -------
        str
            Description of the relation.
        """
        ...
    def get_reference(self)->tuple[str,str]:
        """
        Get the images names of the pair of images that are related.

        Returns
        -------
        image_pair : tuple[str,str]
            Pair of image name strings.
        """
        ...
    def get_relation(self,relation_type)->Any|None:
        """
        Get the relation between the images in the specified relation type.

        Parameters
        ----------
        relation_type : str|None
            Valid inputs: `'r'` for rectangular and `'p'` for points for certain relation classes.s

        Returns
        -------
        relation : Any|None
            `'r'` > tuple[int,int]
                `(x,y)`
            `'p'` > list[tuple[tuple[int,int],tuple[int,int]]]
                `[((xi,yi),(xj,yj)),...]`
            other > None

        Notes
        -----
        If a relation class does not implement a specific relation type it will return None.
        """
        ...
    def for_json(self)->dict[str,Any]:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        relation_data : dict
            JSON dump-able representation of relation information.
        """
        ...

class MISRelationReference():
    """
    Relation of an image pair.

    Reference relationship: `A(x?,y?)=B(x?,y?)`.

    `relation_type=None`"""
    _relation_type=None

    def __init__(self,
        image_pair:tuple[str,str],
        **relation_data):
        """
        Initialize a MISRelationReference.

        This relation should be interpretted as "These two images are related but not sure how exactly".

        Parameters
        ----------
        image_pair : tuple[str,str]
            Pair of image name strings.
        **relation_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """

        self._reference: tuple[str,str]=tuple(image_pair)
            # Note: When importing from JSON this will be a list of length 2.

        self._dict=relation_data

    def __str__(self)->str:
        """
        String representation of the Relation.

        Returns
        -------
        str
            Description of the relation.
        """
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}'."
    def get_reference(self)->tuple[str,str]:
        """
        Get the images names of the pair of images that are related.
        
        Returns
        -------
        image_pair : tuple[str,str]
            Pair of image name strings.
        """
        return tuple(self._reference)
    def get_relation(self,relation_type)->Any|None:
        """
        Get the relation between the images in the specified relation type.

        Parameters
        ----------
        relation_type : str|None
            Accepts any value. Does not change output for MISRelationReference.

        Returns
        -------
        relation = None
            MISRelationReference always returns None
        """
        return None
    def for_json(self)->dict[str,Any]:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        relation_data : dict
            JSON dump-able representation of relation information.
        """
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":list(self._reference),
            }

class MISRelationRectangular():
    """
    Relation of an image pair in terms of (x,y) offset.
    
    Rectilinear relationship: `A(x,y)=B(0,0)`.
    
    `relation_type='r'`
    """
    _relation_type='r'
    def __init__(self,
        image_pair:tuple[str,str],
        rectangular:tuple[int,int]|None=None,
        **relation_data):
        """
        Initialize a MISRelationRectangular
        
        This relation is the `(x,y)` value in `image a` that maps to the `(0,0)` of `image b`.
        These values may be negative if the top left corner `(0,0)` of `image b` is not inside `image a`.

        Parameters
        ----------
        image_pair : tuple[str,str]
            Pair of image name strings.
        rectangular : tuple[int,int]|None
            Rectangular offset x,y that maps from the `(x,y)` of `image a` to the `(0,0)` of `image b`.
        **relation_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """

        self._reference: tuple[str,str]=tuple(image_pair)
            # Note: When importing from JSON this will be a list of length 2.

        if rectangular is None:
            raise ValueError("`rectangular` cannot be None.")
        self._rect=tuple(rectangular)
            # Note: When importing from JSON this will be a list of length 2.

        self._dict=relation_data

    def __str__(self)->str:
        """
        String representation of the Relation.

        Returns
        -------
        str
            Description of the relation.
        """
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}' by {self._rect}."
    def get_reference(self)->tuple[str,str]:
        """
        Get the images names of the pair of images that are related.
        
        Returns
        -------
        image_pair : tuple[str,str]
            Pair of image name strings.
        """
        return tuple(self._reference)
    def get_relation(self,relation_type)->Any|None:
        """
        Get the relation between the images in the specified relation type.

        Parameters
        ----------
        relation_type : str|None
            Valid inputs: 'r' for rectangular, 'p' for points

        Returns
        -------
        relation : Any|None
            'r' > tuple[int,int]
                `(x,y)`
            'p' > list[tuple[tuple[int,int],tuple[int,int]]]
                `[((x,y),(0,0))]`
            other > None
        """
        if relation_type=='r':
            return self._rect
        elif relation_type=='p':
            return ((self._rect,(0,0))) # the offset point in image a should match up with 0,0 in image b.
        else:
            return None
    def for_json(self)->dict[str,Any]:
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        relation_data : dict
            JSON dump-able representation of relation information.
        """
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":list(self._reference),
            "rectangular":list(self._rect),
            }

class MISRelationPoints():
    """
    Contains information relating an image pair in terms of matching points.

    Matching point relationship: `A(xi,yi)=B(xj,yj)`.
    
    `relation_type='p'`"""
    _relation_type='p'
    def __init__(self,
        image_pair:tuple[str,str],
        points:list[tuple[tuple[int,int],tuple[int,int]]]|None=None,
        **relation_data):
        """
        Initialize a MISRelationPoints
        
        This relation is the list of point pairs `[(A(xi,yi),B(xj,yj)),...]` where `A(xi,yi)` matches `B(xj,yj)`.
        These values are generally expected to be positive but it is not strictly required.

        Parameters
        ----------
        image_pair : tuple[str,str]
            Pair of image name strings.
        points : list[tuple[tuple[int,int],tuple[int,int]]]|None
            List of pairs of `(x,y)` points. First point from `image a` and second from `image b`.
        **relation_data : kwargs
            Any other passed kwargs will be kept in `self._dict` and should be JSON dump-able objects.
        """

        self._reference: tuple[str,str]=tuple(image_pair)
            # Note: When importing from JSON this will be a list of length 2.

        if points is None:
            raise ValueError("`points` cannot be None.")
        self._points: list[tuple[tuple[int,int],tuple[int,int]]]=list(points)

        self._dict=relation_data
    def __str__(self)->str:
        """
        String representation of the Relation.

        Returns
        -------
        str
            Description of the relation.
        """
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}' by {self._points}."
    def get_reference(self)->tuple[str,str]:
        """
        Get the images names of the pair of images that are related.
        
        Returns
        -------
        image_pair : tuple[str,str]
            Pair of image name strings.
        """
        return tuple(self._reference)
    def get_relation(self,relation_type)->Any|None:
        """
        Get the relation between the images in the specified relation type.

        Parameters
        ----------
        relation_type : str|None
            Valid inputs: `'r'` for rectangular, `'p'` for points

        Returns
        -------
        relation : Any|None
            `'r'` > tuple[int,int]
                `(x,y)`
            `'p'` > list[tuple[tuple[int,int],tuple[int,int]]]
                `[((xi,yi),(xj,yj)),...]`
            other > None

        Notes
        -----
        Rectangular relation 'r' is calculated by taking the mean of the rectangular offsets from each point pair.
        """
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
        """
        Returns a dictionary compatible with JSON.dump().
        
        Returns
        -------
        relation_data : dict
            JSON dump-able representation of relation information.
        """
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
    """
    Construct `MISRelation` from relation data.

    Uses the `relation_type` field in `relation_data` to select the correct MISRelation implementation to initialize.

    Parameters
    ----------
    relation_data : dict
        JSON dump-able representation of image information. Must include `relation_type`.

    Returns
    -------
    relation : MISRelation
        Returns a MISRelation initialized from `relation_data`. 
        MISRelation implementation selection is based on `relation_type` lookup in the `relation_types` dictionary.
    """
    return relation_types[relation_data["relation_type"]](**relation_data)
