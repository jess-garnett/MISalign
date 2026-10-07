---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Simple notebook for running image alignment & blending
Recommended to run by block based on intended use.

```{code-cell} ipython3
from os.path import abspath
from os import listdir, getcwd

import MISalign.model.project as proj
import MISalign.model.project_service as proj_service
import MISalign.alignment.manual as align_manual
import MISalign.canvas.canvas_service as canv_service
```

```{code-cell} ipython3
start_dir=getcwd()
```

# Specify Data

```{code-cell} ipython3
global mis_fp
# mis_fp=abspath("_example_data/a_myproject_empty.mis")
data_fp=abspath(start_dir+"/example/data/set_a")
mis_fp=abspath(data_fp+"/a_myproject_empty.mis")
```

### First time setup of files:

```{code-cell} ipython3
all_file_names=listdir(data_fp)
data_file_names=sorted([file for file in all_file_names if file.find(".mis")==-1])
default_offset=[data_file_names[0],[0,0],0.0]
image_offset=dict()
for img in data_file_names:
    image_offset[img]=default_offset
```

# Setup, save, and load project

```{code-cell} ipython3
global main_project
main_project=proj.Project(
    mis_filepath=mis_fp,
    image_offset_pairs=image_offset,
    cal_value=None
)
```

```{code-cell} ipython3
proj_service.save_to_mis(
    mis_filepath=mis_fp,
    project=main_project
)
```

### Load mis project

```{code-cell} ipython3
global main_project
main_project:proj.Project=proj_service.load_from_mis(mis_filepath=mis_fp)
```

# Add more images

```{code-cell} ipython3
new_img_names={
        "a_myimages05.jpg": ["a_myimages04.jpg",[0,0],0.0],
        "a_myimages06.jpg": ["a_myimages05.jpg",[0,0],0.0]
    }
main_project.images.update(new_img_names)
main_project.reload_images_offsets()
```

# Alignment

```{code-cell} ipython3
import tkinter as tk
def saveAlign(save_project:proj.Project):
    #purpose: Callback function saving the  alignment results.
    main_project=save_project #updates global project
image_names=sorted(main_project.images.keys())
root=tk.Tk()
root.title("root")
manualalignment=align_manual.ManualAlignWindow(root,main_project,image_names[0],image_names[1],return_project=saveAlign)
root.mainloop()
```

```{code-cell} ipython3
main_project.get_image_offset_pairs()
```

# Canvas Functions

+++

### Rough Canvas

```{code-cell} ipython3
roughcanvas=canv_service.Canvas(project=main_project)
rough_img=roughcanvas.canvas_image()
```

```{code-cell} ipython3
rough_img.show()
```

```{code-cell} ipython3
canvas_save_fp=abspath(start_dir+"/example/expected_result/set_a/a_mycanvas_rough.jpg")
rough_img.save(fp=canvas_save_fp)
```

### Blended Canvas

```{code-cell} ipython3
blendcanvas=canv_service.Canvas(project=main_project)
blend_img=blendcanvas.blended_image()
```

```{code-cell} ipython3
blend_img.show()
```

```{code-cell} ipython3
canvas_save_fp=abspath(start_dir+"/example/expected_result/set_a/a_mycanvas_blend.jpg")
blend_img.save(fp=canvas_save_fp)
```

### Labelled Canvas

```{code-cell} ipython3
roughlabelcanvas=canv_service.Canvas(project=main_project)
roughlabel_img=roughlabelcanvas.mark(list(main_project.images.keys()))
```

```{code-cell} ipython3
roughlabel_img.show()
```

```{code-cell} ipython3
canvas_save_fp=abspath(start_dir+"/example/expected_result/set_a/a_mycanvas_mark.jpg")
roughlabel_img.save(fp=canvas_save_fp)
```
