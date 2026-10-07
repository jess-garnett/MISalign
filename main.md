---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: .venv
  language: python
  name: python3
---

# Notebook For Running MISalign

+++

Included changes:
- Updated model module
    - offset > relations
    - project > mis_file
    - ipy/ipympl alignment GUI
- TODO:
    - canvas rendering

+++

# First Time Setup

+++

## Select Image Files

```{code-cell} ipython3
from os import listdir
from os.path import join, abspath
# source of images

###
folder_path=r"example\data\set_a"
###

# restricts to just files that match the ending you provide.
###
file_ending="jpg"#.tif files
###
file_names=[x for x in listdir(folder_path) if x.split(".")[1]==file_ending]
print(file_names)
# combines images with folder to get absolute path for each.
file_paths=[abspath(join(folder_path,x)) for x in file_names]
print(file_paths)
```

## Create mis_file from Image Paths

```{code-cell} ipython3
from MISalign.model.mis_file import MisFile,save_mis
```

```{code-cell} ipython3
###
mis_fp=join(folder_path,"mymis.mis")
###
```

```{code-cell} ipython3
mis_project=MisFile(image_fps=file_paths)
print(mis_project)
save_mis(mis_fp,mis_project)
```

# Alignment

```{code-cell} ipython3
from MISalign.alignment.interactive_manual import IMRControls
%matplotlib widget
imrc=IMRControls(mis_project)
```

```{code-cell} ipython3
mis_project=imrc.get_mis()
print(mis_project)
```

```{code-cell} ipython3
del imrc._images #free up memory.
```

# Save/Load

```{code-cell} ipython3
from MISalign.model.mis_file import load_mis
```

```{code-cell} ipython3
mis_project=load_mis(mis_fp)
```

```{code-cell} ipython3
save_mis(mis_fp,mis_project)
```

```{code-cell} ipython3
#TODO load mis from file
#TODO tbd
```

# Canvas

```{code-cell} ipython3
from MISalign.canvas.canvas_solve import rectangular_solve
relations=mis_project.get_rels('r')
image_names=mis_project.get_image_names()
origin="a_myimages01.jpg"
origin_relative_offsets=rectangular_solve(
    relations=relations,
    image_names=image_names,
    origin=origin
)
display(origin_relative_offsets)
```

```{code-cell} ipython3
import MISalign.canvas.canvas_render as cr
image_filepaths={k:v for k,v in zip(mis_project.get_image_names(),mis_project.get_image_names())}
image_sizes=cr.find_image_sizes(image_filepaths)
origin_relative_extents=cr.find_relative_extents(
    image_names=image_names,
    origin_relative_offsets=origin_relative_offsets,
    image_sizes=image_sizes)
canvas_extents, canvas_offsets=cr.resolve_extents(origin_relative_extents)
canvas_relative_offsets=cr.place_in_canvas(
    image_names,
    origin_relative_offsets,
    canvas_extents,
    canvas_offsets)
```

```{code-cell} ipython3
unblended_canvas=cr.render_unblended(
    image_names,
    image_filepaths,
    image_sizes,
    canvas_relative_offsets,
    canvas_extents)
display(unblended_canvas)
```

```{code-cell} ipython3
dfe_normalizer=cr.build_normalization(
    image_names,
    image_sizes,
    canvas_relative_offsets,
    canvas_extents,
    cr.weight_dfe)
blended_canvas_dfe=cr.render_blended(
    image_names,
    image_filepaths,
    image_sizes,
    canvas_relative_offsets,
    canvas_extents,
    cr.weight_dfe,
    dfe_normalizer)
display(blended_canvas_dfe)
```

```{code-cell} ipython3
flat_normalizer=cr.build_normalization(
    image_names,
    image_sizes,
    canvas_relative_offsets,
    canvas_extents,
    cr.weight_flat)
blended_canvas_flat=cr.render_blended(
    image_names,
    image_filepaths,
    image_sizes,
    canvas_relative_offsets,
    canvas_extents,
    cr.weight_flat,
    flat_normalizer)
display(blended_canvas_flat)
```
