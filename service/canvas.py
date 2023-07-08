from model.image import Image
from model.offset import Offset
from model.project import Project
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from typing import Union
import numpy as np

class Canvas():
    def __init__(self,project:Project) -> None:
        self.project=project
        self.canvas_offsets=None
        self.image_keys=None
        self.canvas_size=None
        self.array=None
        self.image=None
        self.scale=None
        self.overlap=None
    def canvas_array(self,image_keys:list[str] = None)->np.ndarray:
        if image_keys is None:
            self.canvas_offsets=self.project.get_canvas_offsets()
        else:
            self.canvas_offsets=self.project.get_canvas_offsets(image_keys)
            # self.image_keys=image_keys #if some things didn't load then this will be incorrect.
        self.image_keys=sorted(list(self.canvas_offsets.keys())) #gets the keys of all the properly loaded images
        #TODO alternate sorting/ordering methods.

        if self.canvas_offsets is None:
            #no origin/none of the specified images matched to origin.
            raise Exception
        
        self.canvas_size=self.project.get_canvas_size(self.image_keys)
        self.array=np.zeros(tuple(reversed(self.canvas_size))+(3,),dtype=int)
        for key in self.image_keys:
            rect_off=self.canvas_offsets[key][0] #(x,y) not np y,x
            image_size=self.project.images[key].size #(x,y) not np y,x
            self.array[
            rect_off[1]:rect_off[1]+image_size[1],
            rect_off[0]:rect_off[0]+image_size[0],
            :
            ]=self.project.images[key].image_array
        return self.array
    def canvas_image(self,image_keys:list[str] = None)->PILImage.Image:
        self.image=PILImage.fromarray(self.canvas_array(image_keys=image_keys).astype(np.uint8))
        return self.image
    def refresh(self,image_keys:list[str] = None):
        self.canvas_image(image_keys=image_keys) #will update both image and array.
    def scaled_canvas_image(self,max_size:tuple[int,int],input_image:PILImage.Image = None)->PILImage.Image:
        if input_image is None:
            if self.image is None:
                image_to_scale=self.canvas_image()
            else:
                image_to_scale=self.image
        else:
            image_to_scale=input_image
        x_scale=max_size[0]/image_to_scale.size[0]
        y_scale=max_size[1]/image_to_scale.size[1]
        self.scale=min(x_scale,y_scale)
        scaled_size=(int(self.scale*image_to_scale.size[0]),int(self.scale*image_to_scale.size[1]))
        scaled_image=image_to_scale.resize(scaled_size)
        return scaled_image
    def highlight(self,image_keys:list[str],highlight_width:int = 10,input_image:PILImage.Image = None)->PILImage.Image:
        if input_image is None:
            if self.image is None:
                image_to_highlight=self.canvas_image().copy()
            else:
                image_to_highlight=self.image.copy()
        else:
            image_to_highlight=input_image
        highlighter=ImageDraw.Draw(image_to_highlight)
        for key in image_keys:
            x0=self.canvas_offsets[key][0][0]
            y0=self.canvas_offsets[key][0][1]
            x1=x0+self.project.images[key].size[0]
            y1=y0+self.project.images[key].size[1]
            highlighter.rectangle([x0,y0,x1,y1],outline="red",width=highlight_width) #TODO figure out adjusting highlight_width with scale.
        return image_to_highlight
    def label(self,image_keys:list[str],input_image:PILImage.Image = None)->PILImage.Image:
        if input_image is None:
            if self.image is None:
                image_to_label=self.canvas_image().copy()
            else:
                image_to_label=self.image.copy()
        else:
            image_to_label=input_image
        if self.image is None:
            self.canvas_image()#if no canvas image exists, generate for all valid images.
        labeller=ImageDraw.Draw(image_to_label)
        for key in image_keys:
            label_font=ImageFont.truetype("arial.ttf", int(self.project.images[key].size[0]/16))
            x=self.canvas_offsets[key][0][0]+int(self.project.images[key].size[0]/2)
            y=self.canvas_offsets[key][0][1]+int(self.project.images[key].size[1]/2)
            labeller.text(text=key,xy=(x,y),anchor="mm",fill="red",font=label_font) #TODO figure out adjusting with scale.
        return image_to_label
    def mark(self,image_keys:list[str],highlight_width:int = 10)->PILImage.Image:
        if self.image is None:
            image_to_mark=self.canvas_image().copy()
        else:
            image_to_mark=self.image.copy()
        image_highlighted=self.highlight(image_keys=image_keys,highlight_width=highlight_width,input_image=image_to_mark)
        image_labelled=self.label(image_keys=image_keys,input_image=image_highlighted)
        return image_labelled
    def which_image(self,position:tuple[int,int],scaled:bool):
        if scaled is True:
            if self.scale is not None:
                unscaled_position=(int(position[0]/self.scale),int(position[1]/self.scale))#position coming in needs to be reversed by scale.
            else:
                unscaled_position=position #if the scaled position is wanted but the image hasn't been scaled, will just do scale of 1.
        else:
            unscaled_position=position
        
        for key in reversed(self.image_keys): #reversed so that the images that are on top in the canvas get checked first
            rect_off=self.canvas_offsets[key][0] #(x,y) not np y,x
            image_size=self.project.images[key].size #(x,y) not np y,x
            x1=rect_off[0]
            x2=rect_off[0]+image_size[0]
            y1=rect_off[1]
            y2=rect_off[1]+image_size[1]
            in_x= x2>unscaled_position[0] and unscaled_position[0]>x1
            in_y= y2>unscaled_position[1] and unscaled_position[1]>y1
            if in_x and in_y:
                return key
        return None
    def difference_area_array(self,image_keys):
        self.find_overlap(image_keys=image_keys)
        overlap_x=self.overlap[0]
        overlap_y=self.overlap[1]

        key=image_keys[0]
        img0_area=self.project.images[key].image_array[
            overlap_y[0]-self.canvas_offsets[key][0][1]:overlap_y[1]-self.canvas_offsets[key][0][1],
            overlap_x[0]-self.canvas_offsets[key][0][0]:overlap_x[1]-self.canvas_offsets[key][0][0],
            :
        ]
        key=image_keys[1]
        img1_area=self.project.images[key].image_array[
            overlap_y[0]-self.canvas_offsets[key][0][1]:overlap_y[1]-self.canvas_offsets[key][0][1],
            overlap_x[0]-self.canvas_offsets[key][0][0]:overlap_x[1]-self.canvas_offsets[key][0][0],
            :
        ]

        diff_area=np.abs(np.subtract(img0_area.astype(int),img1_area.astype(int)))
        return diff_area
    def difference_image(self,image_keys):
        diff_canvas_array=self.canvas_array(image_keys=image_keys).copy()
        diff_area=self.difference_area_array(image_keys=image_keys)
        diff_canvas_array[
            self.overlap[1][0]:self.overlap[1][1],
            self.overlap[0][0]:self.overlap[0][1],
            :
        ] = diff_area
        diff_canvas=PILImage.fromarray(diff_canvas_array.astype(np.uint8))
        return diff_canvas
    def find_overlap(self,image_keys):
        if self.canvas_offsets is None:
            self.canvas_array(image_keys=image_keys)
        
        key=image_keys[0]
        img0=(self.canvas_offsets[key][0],(self.canvas_offsets[key][0][0]+self.project.images[key].size[0],self.canvas_offsets[key][0][1]+self.project.images[key].size[1]))
        key=image_keys[1]
        img1=(self.canvas_offsets[key][0],(self.canvas_offsets[key][0][0]+self.project.images[key].size[0],self.canvas_offsets[key][0][1]+self.project.images[key].size[1]))
        
        overlap_x=(max(img0[0][0],img1[0][0]),min(img0[1][0],img1[1][0]))#this overlap might not work when one image is smaller than the other and entirely inside.
        overlap_y=(max(img0[0][1],img1[0][1]),min(img0[1][1],img1[1][1]))
        self.overlap=(overlap_x,overlap_y)
    def half_overlap_image(self,image_keys):
        self.find_overlap(image_keys=image_keys)
        overlap_x=self.overlap[0]
        overlap_y=self.overlap[1]

        key=image_keys[0]
        img0_area=self.project.images[key].image_array[
            overlap_y[0]-self.canvas_offsets[key][0][1]:overlap_y[1]-self.canvas_offsets[key][0][1],
            overlap_x[0]-self.canvas_offsets[key][0][0]:overlap_x[1]-self.canvas_offsets[key][0][0],
            :
        ]
        key=image_keys[1]
        img1_area=self.project.images[key].image_array[
            overlap_y[0]-self.canvas_offsets[key][0][1]:overlap_y[1]-self.canvas_offsets[key][0][1],
            overlap_x[0]-self.canvas_offsets[key][0][0]:overlap_x[1]-self.canvas_offsets[key][0][0],
            :
        ]

        overlap_area=np.average((img0_area.astype(int),img1_area.astype(int)),axis=0).astype(np.uint8)

        over_canvas_array=self.canvas_array(image_keys=image_keys).copy()
        over_canvas_array[
            self.overlap[1][0]:self.overlap[1][1],
            self.overlap[0][0]:self.overlap[0][1],
            :
        ] = overlap_area
        over_canvas=PILImage.fromarray(over_canvas_array.astype(np.uint8))
        return over_canvas
    def blended_image(self,image_keys:list[str] = None):
        self.blend_image=PILImage.fromarray(self.blended_array(image_keys=image_keys).astype(np.uint8))
        return self.blend_image
    def blended_array(self,image_keys:list[str] = None):
        if image_keys is None:
            self.canvas_offsets=self.project.get_canvas_offsets()
        else:
            self.canvas_offsets=self.project.get_canvas_offsets(image_keys)
            # self.image_keys=image_keys #if some things didn't load then this will be incorrect.
        self.image_keys=sorted(list(self.canvas_offsets.keys())) #gets the keys of all the properly loaded images
        #TODO alternate sorting/ordering methods.

        if self.canvas_offsets is None:
            #no origin/none of the specified images matched to origin.
            raise Exception
        
        self.canvas_size=self.project.get_canvas_size(self.image_keys)
        self.blend_array=np.zeros(tuple(reversed(self.canvas_size))+(3,),dtype=int)
        self.dfe_norm=np.zeros(tuple(reversed(self.canvas_size)),dtype=int) #sum of all DFE used for normalization
        for key in self.image_keys:
            rect_off=self.canvas_offsets[key][0] #(x,y) not np y,x
            image_size=self.project.images[key].size #(x,y) not np y,x
            self.dfe_norm[
            rect_off[1]:rect_off[1]+image_size[1],
            rect_off[0]:rect_off[0]+image_size[0]
            ]=np.add(
                self.dfe_norm[
                rect_off[1]:rect_off[1]+image_size[1],
                rect_off[0]:rect_off[0]+image_size[0]
                ],
                self.project.images[key].dfe_array)
        for key in self.image_keys:
            rect_off=self.canvas_offsets[key][0] #(x,y) not np y,x
            image_size=self.project.images[key].size #(x,y) not np y,x
            self.blend_array[
            rect_off[1]:rect_off[1]+image_size[1],
            rect_off[0]:rect_off[0]+image_size[0],
            :
            ]=np.add(
                self.blend_array[
                rect_off[1]:rect_off[1]+image_size[1],
                rect_off[0]:rect_off[0]+image_size[0],
                :
                ],
                np.multiply(
                    self.project.images[key].image_array,
                    np.repeat(
                        np.divide(
                            self.project.images[key].dfe_array,
                            self.dfe_norm[
                            rect_off[1]:rect_off[1]+image_size[1],
                            rect_off[0]:rect_off[0]+image_size[0]
                            ]
                        )[:,:,np.newaxis],
                        3,
                        axis=2
                    )
                )
            )
        return self.blend_array
