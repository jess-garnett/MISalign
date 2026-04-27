"""Build test files for MISalign"""
from PIL import Image as PILImage
import numpy as np
from pathlib import Path
from json import dump

#TODO update to use ".mis.json" notation.

class BuildCanvasRectangular():
    def __init__(self,folder:Path,image:Path,overlap=100) -> None:
        self.build_folder=folder
        self.source_image=image
        self.overlap=overlap
        self.build_npy()
        self.build_vertical()
        self.build_horizontal()
        self.build_quadrants()
    def build_npy(self):
        image=PILImage.open(self.source_image)
        self.array=np.asarray(image)
        np.save(self.build_folder.joinpath(self.source_image.stem+".npy"),self.array)
    def build_vertical(self):
        rows,cols,channels=self.array.shape
        array_top=self.array[:int((rows+self.overlap)/2)]
        array_bottom=self.array[int((rows-self.overlap)/2):]
        # print(array_top.shape)
        # print(array_bottom.shape)
        name_top=self.source_image.stem+"_v_t.png"
        name_bottom=self.source_image.stem+'_v_b.png'
        PILImage.fromarray(array_top).save(self.build_folder.joinpath(name_top))
        PILImage.fromarray(array_bottom).save(self.build_folder.joinpath(name_bottom))

        build_project=dict(
            images=[{"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_top}"},
                    {"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_bottom}"}],
            relations=[{"image_pair":[name_top,name_bottom],
                        "relation_type": "p",
                        "points":[[[0,int((rows-self.overlap)/2)],[0,0]]]}]
        )
        with open(self.build_folder.joinpath(self.source_image.stem.replace("image","project")+"_v.json"),"w") as f:
            dump(build_project,fp=f,indent=4)
    def build_horizontal(self):
        rows,cols,channels=self.array.shape
        array_left=self.array[:,:int((cols+self.overlap)/2)]
        array_right=self.array[:,int((cols-self.overlap)/2):]
        # print(array_left.shape)
        # print(array_right.shape)
        name_left=self.source_image.stem+"_h_l.png"
        name_right=self.source_image.stem+"_h_r.png"
        PILImage.fromarray(array_left).save(self.build_folder.joinpath(name_left))
        PILImage.fromarray(array_right).save(self.build_folder.joinpath(name_right))

        build_project=dict(
            images=[{"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_left}"},
                    {"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_right}"}],
            relations=[{"image_pair":[name_left,name_right],
                        "relation_type": "p",
                        "points":[[[int((cols-self.overlap)/2),0],[0,0]]]}]
        )
        with open(self.build_folder.joinpath(self.source_image.stem.replace("image","project")+"_h.json"),"w") as f:
            dump(build_project,fp=f,indent=4)
    def build_quadrants(self):
        rows,cols,channels=self.array.shape
        array_topleft=self.array[:int((rows+self.overlap)/2),:int((cols+self.overlap)/2)]
        array_topright=self.array[:int((rows+self.overlap)/2),int((cols-self.overlap)/2):]
        array_bottomleft=self.array[int((rows-self.overlap)/2):,:int((cols+self.overlap)/2)]
        array_bottomright=self.array[int((rows-self.overlap)/2):,int((cols-self.overlap)/2):]
        # print(array_topleft.shape)
        # print(array_topright.shape)
        # print(array_bottomleft.shape)
        # print(array_bottomright.shape)
        name_topleft=self.source_image.stem+"_q_tl.png"
        name_topright=self.source_image.stem+"_q_tr.png"
        name_bottomleft=self.source_image.stem+"_q_bl.png"
        name_bottomright=self.source_image.stem+"_q_br.png"
        PILImage.fromarray(array_topleft).save(self.build_folder.joinpath(name_topleft))
        PILImage.fromarray(array_topright).save(self.build_folder.joinpath(name_topright))
        PILImage.fromarray(array_bottomleft).save(self.build_folder.joinpath(name_bottomleft))
        PILImage.fromarray(array_bottomright).save(self.build_folder.joinpath(name_bottomright))

        build_project=dict(
            images=[{"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_topleft}"},
                    {"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_topright}"},
                    {"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_bottomleft}"},
                    {"image_type":"file","image_filepath":f"tests/test_files/canvas_rectangular/{name_bottomright}"}],
            relations=[{"image_pair":[name_topleft,name_topright],
                        "relation_type": "p",
                        "points":[[[int((cols-self.overlap)/2),0],[0,0]]]},
                        {"image_pair":[name_topright,name_bottomright],
                        "relation_type": "p",
                        "points":[[[0,int((rows-self.overlap)/2)],[0,0]]]},
                        {"image_pair":[name_topleft,name_bottomleft],
                        "relation_type": "p",
                        "points":[[[0,int((rows-self.overlap)/2)],[0,0]]]}]
        )
        with open(self.build_folder.joinpath(self.source_image.stem.replace("image","project")+"_q.json"),"w") as f:
            dump(build_project,fp=f,indent=4)

class BuildModelImage():
    def __init__(self,folder:Path,image:Path) -> None:
        self.build_folder=folder
        self.source_image=image
        self.build_npy_png()
    def build_npy_png(self):
        image=PILImage.open(self.source_image)
        self.array=np.asarray(image)
        np.save(self.build_folder.joinpath(self.source_image.stem+".npy"),self.array)
        image.save(self.build_folder.joinpath(self.source_image.stem+".png"))

if __name__=="__main__":
    BuildCanvasRectangular(
        folder=Path("canvas_rectangular"),
        image=Path("test_data/test_image_a01.jpg")
        )
    BuildModelImage(
        folder=Path("model_image"),
        image=Path("test_data/test_image_a01.jpg")
        )