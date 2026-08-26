Project E includes a 6 image subset, from a 31 image dataset, of a Fe-Cr-Mo region of a dual-anneal diffusion multiple(DADM), primarily in the chi(χ) region of the 1200°C 500h + 900°C 50h DADM pictured in Figure 3(b) of Zhao 2020. They were captured on a TESCAN XEIA3 scanning electron microscope(SEM) at 5400x magnification(50.061nm/pixel) with separate back scattered electron(BSE) and secondary electron(SE) signals. These images were taken on 2025-08-07 by Jessica Garnett.

Zhao, Ji-Cheng. 2020. “High-Throughput and Systematic Study of Phase Transformations and Metastability Using Dual-Anneal Diffusion Multiples.” Metallurgical and Materials Transactions A 51 (10): 5006–22. https://doi.org/10.1007/s11661-020-05915-w.

Below are example modifications to the notebooks to demo this project.

Setup code in `setup.ipynb`:
```
###
# Enter setup information
###
folder_path=Path("../example/project_f") # folder with images
misfile_name="demo-project_f-no_relations-calibrated.mis.json" # name for save file
#
calibration_filepath=Path("../example/project_f/scale_5400x_1pixel.miscal.json")
    # filepath to calibration file `.miscal.json`
#
file_ending=".png" # file extension
file_contains="" # file names must contain - i.e. "sample1-5x", "sample2", "10x", etc.
file_notcontains="project" # file names must not contain - i.e. "calibration"
```

Alignment code in `align.ipynb`:
```
mis_filepath="../example/project_f/project_f-no_relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=4096,right=4096,filter=Filter.simple_uint16))
...
imrc=IMRControls(mis_project,imshow_kwargs=dict(cmap="gray",vmin=0,vmax=255))
...
mis_filepath="../example/project_f/demo-project_f-relations-calibrated.mis.json"
```

Render code in `render.ipynb`:

BSE render:
```
mis_filepath="../example/project_f/project_f-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=4096,right=4096,filter=Filter.simple_uint16))
...
selected_image=selected_image
...
image_with_scale_bar(
    image=selected_image,
    scale_measurement="100um",
    calibration=selected_calibration,
    loc="upper left")
```

SE render:
```
mis_filepath="../example/project_f/project_f-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=4096,left=4096,filter=Filter.simple_uint16))
...
selected_image=selected_image
...
image_with_scale_bar(
    image=selected_image,
    scale_measurement="100um",
    calibration=selected_calibration,
    loc="upper left")
```