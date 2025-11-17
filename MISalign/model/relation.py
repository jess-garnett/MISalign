"""Relations Model
- Relate two images
- Can store None relation i.e. these two images are related but it is not known what the relationship is.
- Can store simple rectangular relation A(0,0) maps to B(0,0)
- Can store simple rectangular + rotational relation which is A(0,0) to B(0,0) and A→B(Theta) with Theta around B(0,0)
    - Rotation first, then translate? Need to figure out exact implementation and how it works with rotated chains of images.
- Can store point match pairs Point A(X,Y) maps to points B(X,Y)
    - Can generate rectangular + rotational
- Can generate a relation tree graphic/table/something showing relation chains
"""
from statistics import mean
from typing import Protocol, runtime_checkable, Any

class Relation():
    """Stores the relationship between two images."""
    def __init__(self,image_a,image_b,relation=None,*data):
        self.ref=(image_a,image_b)
        self._relation=relation
        if relation is None:
            self._rect=None
            self._rota=None
            self._points=None
        if relation=='r':
            #rectilinear relationship A(0,0)->B(0,0)
            self._rect=data[0]
            self._rota=None
            self._points=None
        elif relation=='rr':
            #rectilinear and rotational relationship A(0,0)->B(0,0) with B rotated Theta around B(0,0)
            self._rect=data[0]
            self._rota=data[1]
            self._points=None
        elif relation=='p':
            #point-based relation Ai->Bi
            self._points=data[0]
            self._rect=None
            self._rota=None
    def __str__(self):
        return "Image '"+self.ref[1]+"' relates to image '"+self.ref[0]+"' by:"+str([self._rect,self._rota,self._points])

    def get_rel(self,relation=None):
        if relation==None:
            return self.ref
        elif relation=='r':
            #rectilinear relationship A(0,0)->B(0,0)
            if self._relation=='r':
                return self._rect
            elif self._relation=='p':
                points_a=[x[0] for x in self._points] # type: ignore
                points_b=[x[1] for x in self._points] # type: ignore
                shift=[[b[0]-a[0],b[1]-a[1]] for a,b in zip(points_a,points_b)]
                x_shift=int(mean([x[0] for x in shift]))
                y_shift=int(mean([x[1] for x in shift]))
                return (x_shift,y_shift)
        elif relation=='rr':
            #rectilinear and rotational relationship A(0,0)->B(0,0) with B rotated Theta around B(0,0)
            if self._relation=='rr':
                return [self._rect,self._rota]
            elif self._relation=='p':#TODO implement an actual rotation algorithm here.
                return None
        elif relation=='p':
            #point-based relation Ai->Bi
            return self._points
    def save_rel(self):
        if self._relation is None:
            data=None
        if self._relation=='r':
            data=self._rect
        elif self._relation=='rr':
            data=(self._rect,self._rota)
        elif self._relation=='p':
            data=self._points
        return [self.ref,self._relation,data]  # type: ignore
    


@runtime_checkable
class MISRelation(Protocol):
    """Contains information relating an image pair."""
    def __init__(self,**relation_data)->None:
        """Initialize Relation"""
    def __str__(self)->str:
        """String Representation of the Relation."""
        ...
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        ...
    def get_relation(self,relation_type)->Any:
        """Get the relation between the images in the specified relation type."""
        ...
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump().
        - `relation_data["image_pair"]:tuple[str,str]`"""
        ...

class MISRelationReference():
    """Image pair that is related but no specific relation is known.
    - `relation_type=None`"""
    _relation_type=None
    def __init__(self,**relation_data):
        self._dict=relation_data
        self._reference=relation_data["image_pair"]
    def __str__(self)->str:
        """String Representation of the Relation."""
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}'."
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        return self._reference
    def get_relation(self,relation_type):
        """Get the relation between the images in the specified relation type."""
        return None
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()."""
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":self._reference,
            }

class MISRelationRectangular():
    """Contains information relating an image pair in terms of (x,y) offset.
    - `relation_type='r'`
    - rectilinear relationship A(0,0)->B(0,0)"""
    _relation_type='r'
    def __init__(self,**relation_data):
        self._dict=relation_data
        self._reference=relation_data["image_pair"]
        self._rect=relation_data["rectangular"]

    def __str__(self)->str:
        """String Representation of the Relation."""
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}' by {self._rect}."
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        return self._reference
    def get_relation(self,relation_type):
        """Get the relation between the images in the specified relation type."""
        if relation_type=='r':
            return self._rect
        elif relation_type=='p':
            return ((self._rect,(0,0))) # the offset point in image a should match up with 0,0 in image b.
        else:
            return None
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()."""
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":self._reference,
            "rectangular":self._rect,
            }

class MISRelationPoints():
    """Contains information relating an image pair in terms of matching points.
    - `relation_type='p'`
    - point-based relation Ai->Bi"""
    _relation_type='p'
    def __init__(self,**relation_data):
        self._dict=relation_data
        self._reference=relation_data["image_pair"]
        self._points=relation_data["points"]
    def __str__(self)->str:
        """String Representation of the Relation."""
        return f"Image '{self._reference[1]}' is related to image '{self._reference[0]}' by {self._points}."
    def get_reference(self)->tuple[str,str]:
        """Get the images names of the pair of images that are related."""
        return self._reference
    def get_relation(self,relation_type):
        """Get the relation between the images in the specified relation type."""
        if relation_type=='r':
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
    def save_dict(self)->dict:
        """Returns a dictionary compatible with JSON.dump()."""
        return {
            **self._dict,
            "relation_type":self._relation_type,
            "image_pair":self._reference,
            "points":self._points
            }


relation_types={
    MISRelationReference._relation_type:MISRelationReference,
    MISRelationRectangular._relation_type:MISRelationRectangular,
    MISRelationPoints._relation_type:MISRelationPoints,
}
def setup_relation(**relation_data)->MISRelation:
    return relation_types[relation_data["relation_type"]](**relation_data)
