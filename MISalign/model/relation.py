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
            self._rect=None #TODO calculate rectangular and rotational from point set.
            self._rota=None
    def __str__(self):
        return "Image '"+self.ref[0]+"' relates to image '"+self.ref[1]+"' by:"+str([self._rect,self._rota,self._points])

    def get_rel(self,relation=None):
        if relation==None:
            return self.ref
        elif relation=='r':
            #rectilinear relationship A(0,0)->B(0,0)
            return self._rect
        elif relation=='rr':
            #rectilinear and rotational relationship A(0,0)->B(0,0) with B rotated Theta around B(0,0)
            return [self._rect,self._rota]
        elif relation=='p':
            #point-based relation Ai->Bi
            return self._points