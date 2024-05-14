#TODO deprecate this module.
from .image import Image
from .offset import Offset
from os.path import split
from os import chdir
from PIL import UnidentifiedImageError
from typing import Union
import numpy as np

class Project():
    def __init__(self,mis_filepath:str,cal_value:int,image_offset_pairs:dict) -> None:
        #mis_filepath should always be an absolute filepath.
        self.folder:str=split(mis_filepath)[0]
        chdir(self.folder)
        self.name:str=split(mis_filepath)[1]
        self.filepath=mis_filepath
        self.cal:int=cal_value
        self.images:dict[str,Image] = dict()
        self.image_err_descs:dict[str,list[str]] = dict()
        self.image_err_types:dict[str,list[str]] = dict()
        self.update_images(list(image_offset_pairs.keys()))
        self.offsets:dict[str,Offset] = dict()
        self.update_offsets(image_offset_pairs)

    def update_mis_filepath(self,new_mis_filepath:str):
        #new_mis_filepath should always be absolute path
        self.filepath=new_mis_filepath
        if split(new_mis_filepath)[0]==self.folder:
            self.name=split(new_mis_filepath)[1] #if file is in the same folder as before, then just update the project name
        else:
            self.folder:str=split(new_mis_filepath)[0]
            chdir(self.folder)
            self.name:str=split(new_mis_filepath)[1]
            self.reload_images_offsets()
    def reload_images_offsets(self):
        reload_pairs=self.get_image_offset_pairs()
        self.clear_arrays()
        self.update_images(list(reload_pairs.keys()))
        self.update_offsets(reload_pairs)
    def clear_arrays(self):
        self.images.clear()
        self.image_err_descs.clear()
        self.image_err_types.clear()
        self.offsets.clear()
    def get_image_offset_pairs(self) -> dict[str,list[str,tuple,float]]:
        #generate dictionary of image_fp:offset list for all unique image_fp.
        unique_image_fp=self.get_unique_image_fps()
        output_dict=dict()
        for image_fp in unique_image_fp:
            if image_fp in self.offsets:
                output_dict[image_fp]=self.offsets[image_fp].get_list()
            else:
                output_dict[image_fp]=None
        return output_dict
    def get_unique_image_fps(self):
        offset_refs=[]
        for offset_value in self.offsets.values():
            offset_refs.append(offset_value.get_ref())
        unique_image_fp=set()
        unique_image_fp.update(
            self.images,
            self.image_err_types,
            self.offsets,
            offset_refs
        )
        return unique_image_fp
    
    def update_images(self,image_fps:list[str]) -> None:
        #will add or update all valid image filepaths in dictionary keys.
        #TODO consider making this accept both dict and list
        for image_fp in image_fps:
            try:
                new_image=Image(image_fp)
                self.images[image_fp]=new_image
                self.reset_image_err(image_fp,"Image")
            except FileNotFoundError:
                self.record_image_err(image_fp,"Image","OS.FileNotFoundError")
            except UnidentifiedImageError:
                self.record_image_err(image_fp,"Image","PIL.UnidentifiedImageError")
    def update_offsets(self,im_of_pairs:dict[str,list[str,tuple,float]]) -> None:
        for key_image_fp,value_offset in im_of_pairs.items():
            if value_offset is not None:
                self.offsets[key_image_fp]=Offset(value_offset)
                self.reset_image_err(key_image_fp,"Offset")
            else:
                self.record_image_err(key_image_fp,"Offset","MIS.NoneOffset")
    def replace_image(self,new_image_fp:str,old_image_fp:str):
        if new_image_fp not in self.images:
            self.update_images([new_image_fp])
        self.offsets[new_image_fp]=self.offsets[old_image_fp]
        for image_fp in self.offsets:
            if self.offsets[image_fp].get_ref()==old_image_fp:
                self.offsets[image_fp].set_ref(new_image_fp)
        self.delete_image(old_image_fp)
    def delete_image(self,image_fp:str):
        #removes image from images, image_errs, offsets, and removes any offsets which direct to the image.
        self.images.pop(image_fp,None)
        self.image_err_types.pop(image_fp,None)
        self.image_err_descs.pop(image_fp,None)
        self.offsets.pop(image_fp,None)
        for img_fp in self.offsets.copy():
            if self.offsets[img_fp].get_ref()==image_fp:
                self.offsets.pop(img_fp,None)
                self.record_image_err(img_fp,"Offset","MIS.NoneOffset")
#TODO transfer a large amount of this into the canvas module.
    def get_origins(self) -> Union[list[str],None]:
        origins:list[str] = []
        for key_image_fp,value_offset in self.offsets.items():
            if key_image_fp == value_offset.get_ref():
                origins.append(key_image_fp)
        #TODO handle situations where there are multiple origins -> raise exception?
        if origins: #empty list will return false, list with values will return true
            return origins
        else:
            return None
    def get_origin_key(self) -> Union[str,None]:
        origins = self.get_origins()
        if origins==None:
            return None #if there is no origin, cannot find origin relative offset.
        if len(origins)==1:
            origin=origins[0] #ideal case
        elif len(origins)>1:
            #TODO handle multiple-origin considerations further
            origin=origins[0]
        return origin
    def get_origin_relative_offsets(self,specific_image_fps:list[str] = None) -> Union[dict[str,Offset],None]:
        
        #setup origin key
        origin = self.get_origin_key()
        if origin==None:
            return None #if there is no origin, cannot find origin relative offset.

        #setup lists for swapping offsets.
        to_swap:list[str] = [origin]
        origin_offsets:dict[str,Offset] = {origin:Offset([origin,(0,0),0.0])}
        offsets=self.offsets.copy()#copy so that the actual self.offsets don't get deleted.
        del offsets[origin]
        #carry out swap procedure starting at origin and mapping through all connected offsets.
        while to_swap: #as long as to_swap is not empty will keep running
            for swap in to_swap.copy():#make copy so that to_swap can have values added/removed while for loop is running.
                for offset in offsets.copy():#make copy so that to_swap can have values added/removed while for loop is running.
                    if offsets[offset].get_ref()==swap: #when image references currently image being swapped
                        origin_offsets[offset]=Offset([
                            origin,
                            (
                                offsets[offset].get_x()+origin_offsets[swap].get_x(),
                                offsets[offset].get_y()+origin_offsets[swap].get_y()
                            ),
                            0.0
                            ]
                        ) #do the swap and create the new origin relative offset.
                        to_swap.append(offset) #will swap this image on the next to_swap loop
                        del offsets[offset] #don't want to check it again
                to_swap.remove(swap) #have replaced it in all places it was referenced, don't want to check it again.
        #after swapping all the images which referenced to the origin, add an image err for all the other ones.
        for image_fp in offsets:
            self.record_image_err(image_fp,"Offset","MIS.NotOriginOffset")
        #return all origin relative offsets if specified image filepaths are None, return just those specific image offsets if they are specified.
        if specific_image_fps is None:
            return origin_offsets
        else:
            specific_origin_offsets:dict[str,Offset] = dict()
            for image_fp in specific_image_fps:
                if image_fp in origin_offsets:
                    specific_origin_offsets[image_fp]=origin_offsets[image_fp] #compiles any of the specific images which have origin offsets
            if specific_origin_offsets:#will be true when dict is not empty
                return specific_origin_offsets
            else:
                return None
    def get_canvas_offsets(self,specific_image_fps:list[str]=None) -> Union[dict[str,tuple[tuple[int,int],float]],None]:
        #TODO handle rotation
        #generate origin relative offsets
        origin_relative_offsets=self.get_origin_relative_offsets(specific_image_fps=specific_image_fps)
        if origin_relative_offsets == None:
            return None
        #find minimum values
        x_values=[]
        y_values=[]
        for oro in origin_relative_offsets:
            x_values.append(origin_relative_offsets[oro].get_x())
            y_values.append(origin_relative_offsets[oro].get_y())
        min_x=min(x_values)
        min_y=min(y_values)
        #create new dictionary that makes the minimum values equal to 0 and adjusts others accordingly
        canvas_offsets=dict()
        for oro in origin_relative_offsets:
            canvas_offsets[oro]=(
                (
                    origin_relative_offsets[oro].get_x()-min_x,
                    origin_relative_offsets[oro].get_y()-min_y
                ),
                0.0
            )
        return canvas_offsets
    def get_canvas_size(self,specific_image_fps:list[str]=None) -> Union[tuple[int,int],None]:
        #generate canvas offsets
        canvas_offsets=self.get_canvas_offsets(specific_image_fps=specific_image_fps)
        if canvas_offsets == None:
            return None
        #removes image_fp which have image errors.
        for image_fp in canvas_offsets.copy(): #Maybe do this 'error' detection somewhere else?
            if "Image" in self.image_err_types.get(image_fp,[]): #TODO method to check for list of error types for an image_fp
                del canvas_offsets[image_fp]
        #minimum value is known to be 0,0 so just store max values of offset+size
        x_values=[]
        y_values=[]
        for image_fp in canvas_offsets:
            x_values.append(canvas_offsets[image_fp][0][0]+self.images[image_fp].size[0])
            y_values.append(canvas_offsets[image_fp][0][1]+self.images[image_fp].size[1])
        max_x=max(x_values)
        max_y=max(y_values)
        canvas_size=(max_x,max_y)
        return canvas_size

    def dfe_canvas_layer(self,canvas_size:tuple[int,int],image_fp:str,canvas_offset:tuple[tuple[int,int],float]):
        return self.place_in_zeroes(
            canvas_size=canvas_size,
            layers=1,
            data_array=self.images[image_fp].dfe_array,
            canvas_offset=canvas_offset
        )
    def image_canvas_layer(self,canvas_size:tuple[int,int],image_fp:str,canvas_offset:tuple[tuple[int,int],float]):
        return self.place_in_zeroes(
            canvas_size=canvas_size,
            layers=3,
            data_array=self.images[image_fp].image_array,
            canvas_offset=canvas_offset
        )
    @staticmethod
    def place_in_zeroes(canvas_size:tuple[int,int],layers:int,data_array:np.ndarray,canvas_offset:tuple[tuple[int,int],float]):
        if len(data_array.shape)==2:
            data_array=data_array[:,:,np.newaxis]
        np_canvas_size=(
            canvas_size[1],#convert from (x,y) to (#rows,#columns)
            canvas_size[0],
            layers
        )
        np_rect_off=(
            canvas_offset[0][1],#convert from (x,y) to (#rows,#columns)
            canvas_offset[0][0]
        )
        data_size=(
            data_array.shape[0],
            data_array.shape[1]
        )
        layer=np.zeros(np_canvas_size,dtype=int)
        layer[
            np_rect_off[0]:np_rect_off[0]+data_size[0],
            np_rect_off[1]:np_rect_off[1]+data_size[1],
            :
        ]=data_array
        return layer
    
    def record_image_err(self,image_fp:str,err_type:str,err_desc:str) -> None:
        #record that there was an error with an image
        #err_type -> is the error caused by the image(Image) or the offset(Offset)
        if image_fp not in self.image_err_descs:
            self.image_err_descs[image_fp]=list()
            self.image_err_types[image_fp]=list()
        self.image_err_descs[image_fp].append(err_desc)
        self.image_err_types[image_fp].append(err_type)
    def reset_image_err(self,image_fp:str,err_type:str):
        if image_fp in self.image_err_types:
            to_remove=[]
            for i in range(len(self.image_err_types[image_fp])):
                if self.image_err_types[image_fp][i]==err_type:
                    to_remove.append(i)
            for i in reversed(to_remove):#reversed so removal won't impact indices that are yet to be removed
                self.image_err_types[image_fp].pop(i)
                self.image_err_descs[image_fp].pop(i)



