---
jupytext:
  formats: notebooks///ipynb,scripts///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: misalign
  language: python
  name: python3
---

# Render Image Montages

+++

**Imports**

```{code-cell} ipython3
from misalign.model.project import MISProjectJSON
import misalign.canvas.canvas_rectangular as cr
```

## Render Setup

```{code-cell} ipython3
###
mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
auto_save_renders=False
###
mis_project.find_image_paths(mis_filepath,update=True)
print(mis_project)
```

```{code-cell} ipython3
origin_relative_offsets=cr.rectangular_solve_project(
    project=mis_project,
)
print("Origin-relative offsets")
display(origin_relative_offsets)
origin_relative_extents=cr.find_relative_extents_project(
    project=mis_project,
    origin_relative_offsets=origin_relative_offsets,)
canvas_extents, canvas_offsets=cr.resolve_extents(origin_relative_extents)
canvas_relative_offsets=cr.place_in_canvas(
    image_names=mis_project.get_image_names(),
    origin_relative_offsets=origin_relative_offsets,
    canvas_extents=canvas_extents,
    canvas_offsets=canvas_offsets)
print("Canvas-relative offsets")
display(canvas_relative_offsets)
```

## Render Unblended

```{code-cell} ipython3
unblended_canvas=cr.render_unblended_project(
    project=mis_project,
    canvas_relative_offsets=canvas_relative_offsets,
    canvas_extents=canvas_extents)
display(unblended_canvas)
if auto_save_renders:
    unblended_save_fp=mis_filepath.replace(".mis.json","-unblend.png")
    unblended_canvas.save(unblended_save_fp)
```

## Render Blended

```{code-cell} ipython3
blended_canvas_dfe=cr.render_blended_project(
    project=mis_project,
    canvas_relative_offsets=canvas_relative_offsets,
    canvas_extents=canvas_extents,
    weight=cr.weight_dfe)
display(blended_canvas_dfe)
if auto_save_renders:
    blended_save_fp=mis_filepath.replace(".mis.json","-blend.png")
    blended_canvas_dfe.save(blended_save_fp)
```

## Image Scale Bar and Overlays

```{code-cell} ipython3
from misalign.calibration.scale_bar import image_with_scale_bar,scale_bar_calibrate,save_calibrated_image,add_image_overlays_project
from misalign.calibration.calibrate import CalibrationManual
from PIL.Image import Transpose
%matplotlib widget
```

```{code-cell} ipython3
## Select image, it can be either a filepath to an image or a PIL Image object.
###
# selected_image=r"../example/expected_result/set_a/a_mycanvas_blend.jpg"
selected_image=blended_canvas_dfe
# selected_image=unblended_canvas
###

## Tranpose selected PIL Image object if needed.
# selected_image=selected_image
# selected_image=selected_image.transpose(Transpose.FLIP_LEFT_RIGHT)
# selected_image=selected_image.transpose(Transpose.FLIP_TOP_BOTTOM)
selected_image=selected_image.transpose(Transpose.ROTATE_90)
# selected_image=selected_image.transpose(Transpose.ROTATE_180)
# selected_image=selected_image.transpose(Transpose.ROTATE_270)

###
selected_calibration=mis_project.get_calibration()
#
# calibration_path=r"..\example\data\set_a\a_5x.miscal"
# cm=CalibrationManual()
# cm.load_calibration(calibration_path)
# selected_calibration=cm.distances
###
```

```{code-cell} ipython3
image_with_scale_bar(
    image=selected_image,
    scale_measurement="1mm",
    calibration=selected_calibration,
    loc="upper left")
```

```{code-cell} ipython3
scaled_dpi=1000
# Increasing this DPI makes the above image smaller
# As a result, increasing the DPI makes the scale bar text/box larger relative to the image.
# Changing this DPI does not effect the resolution of the final image
#
scale_bar_calibrate(scale_dpi=scaled_dpi)
```

```{code-cell} ipython3
# Optional add image boundaries and labels - Does not currently work with the image transpose functions
# add_image_overlays_project(project=mis_project,canvas_relative_offsets=canvas_relative_offsets,boundary=True,label=True)
```

```{code-cell} ipython3
# Save at full resolution
if type(selected_image) is str:
    split_fp=selected_image.split(".")
    scalebar_save_fp=split_fp[0]+"-scale."+split_fp[1]
else:
    scalebar_save_fp=mis_filepath.replace(".mis.json","-scale.png")
save_calibrated_image(scalebar_save_fp,scale_dpi=scaled_dpi)
```

```{code-cell} ipython3
# Save at 10 to 1 resolution (i.e. 50000x20000 becomes 5000x2000)
if type(selected_image) is str:
    split_fp=selected_image.split(".")
    scalebar_save_fp=split_fp[0]+"-scale_10_1."+split_fp[1]
else:
    scalebar_save_fp=mis_filepath.replace(".mis.json","-scale_10_1.png")
save_calibrated_image(scalebar_save_fp,scale_dpi=int(scaled_dpi/10))
```
