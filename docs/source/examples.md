# Examples

The primary workflow for using MISalign is:
- `setup.ipynb` - Create a project: select images files & scale calibration.
    - Optionally first: `calibration.ipynb` - Setup scale calibration by selecting points on an image.
- `align.ipynb` - Select matching points in image pairs to relate the images.
- `render.ipynb` - Render image montages with and without blending and add scale bar overlays.

This workflow has preconfigured paths and intermediate files in the [notebooks](https://github.com/jess-garnett/MISalign/tree/main/notebooks) and [examples](https://github.com/jess-garnett/MISalign/tree/main/example) (specifically `examples/project_a`) of the [Github Repository](https://github.com/jess-garnett/MISalign).

```{toctree}
:caption:  Primary Workflow Notebooks
:maxdepth: 2

_notebooks/setup
_notebooks/calibrate
_notebooks/align
_notebooks/render
```


```{toctree}
:caption: Example Notebooks
:maxdepth: 2
examples/hdf5_examples
```