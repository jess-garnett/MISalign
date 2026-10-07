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

# Calibrate from Image

+++

**Imports**

```{code-cell} ipython3
from misalign.calibration.calibrate import CalibrationManual
%matplotlib widget
```

## Basic Calibration
- Load image with reference dimension.
- Specify known length measurement.
- Select matching pairs of points.
- Resolve distance between points.
- Save calibration to `.miscal.json` file.

```{code-cell} ipython3
cm=CalibrationManual(calibration_image_path="../example/project_a/scale_5x_1mm.bmp")
cm.calibrate_measurement(length=1,units="mm")
cm.calibrate_setup()
```

```{code-cell} ipython3
cm.calibrate_resolve()
```

```{code-cell} ipython3
cm.print_pixels_per_length()
cm.print_length_per_pixel()
```

```{code-cell} ipython3
cm.save_calibration("../example/project_a/demo-scale_5x_1mm.miscal.json")
```

## Confirm Calibration
- Optional
- Load calibration from file to check saved values.

```{code-cell} ipython3
cm2=CalibrationManual()
cm2.load_calibration("../example/project_a/scale_5x_1mm.miscal.json")
cm2.print_pixels_per_length()
cm2.print_length_per_pixel()
print(cm2.distances)
```

```{code-cell} ipython3
cm3=CalibrationManual()
cm3.load_calibration("../example/project_a/project_a-no_relations-calibrated.mis.json")
cm3.print_pixels_per_length()
cm3.print_length_per_pixel()
print(cm3.distances)
```
