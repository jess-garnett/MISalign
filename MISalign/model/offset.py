
class Offset():
    def __init__(self,input:list):
        #expect: [ref:str,rect:tuple(int,int),rota:float]
        self._ref: str = input[0] #reference image for offset
        self._rect: tuple[int,int] = tuple(input[1]) #rectangular offset (x,y)
        self._rota: float = input[2] #rotational offset in clockwise radians
    
    def get_ref(self):
        return self._ref
    
    def get_rect(self):
        return self._rect
    def get_x(self):
        return self._rect[0]
    def get_y(self):
        return self._rect[1]

    def get_list(self):
        return [self._ref,self._rect,self._rota]
    
    def set_ref(self,new_ref:str):
        self._ref=new_ref

    def set_rect(self,new_rect:tuple[int,int]):
        self._rect=new_rect
    
    def set_rota(self,new_rota:float):
        self._rota=new_rota