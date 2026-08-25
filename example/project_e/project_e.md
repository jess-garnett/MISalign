Project E includes two 16 image subsets, from a 190 image dataset, of a Fe-Cr-Mo region of a dual-anneal diffusion multiple(DADM), primarily in the sigma(σ) and chi(χ) regions of the 1200°C 500h + 900°C 50h DADM pictured in Figure 3(b) of Zhao 2020. They were captured on a Hitachi SU70 scanning electron microscope(SEM) at 1000x magnification(49.60938nm/pixel) with a high-angle back scattered electron(BSE) detector. These images were taken on 2024-11-26 by Jessica Garnett.

Zhao, Ji-Cheng. 2020. “High-Throughput and Systematic Study of Phase Transformations and Metastability Using Dual-Anneal Diffusion Multiples.” Metallurgical and Materials Transactions A 51 (10): 5006–22. https://doi.org/10.1007/s11661-020-05915-w.

Below are example modifications to the notebooks to demo this project.

Setup code in `setup.ipynb`:
```
###
# Enter setup information
###
folder_path=Path("../example/project_e/") # folder with images
misfile_names=["demo-project_e-2-no_rel-cal.mis.json","demo-project_e-8-no_rel-cal.mis.json"] # name for save file
#
calibration_filepath=Path("../example/project_e/scale_1000x_1pixel.miscal.json")
    # filepath to calibration file `.miscal.json`
#
file_ending=".tif" # file extension
file_contains="" # file names must contain - i.e. "sample1-5x", "sample2", "10x", etc.
file_notcontains="" # file names must not contain - i.e. "calibration"
###
...
# user selected image sets using start and end index
image_sets={
    "demo-project_e-2-no_rel-cal.mis.json":(0,15),
    "demo-project_e-8-no_rel-cal.mis.json":(16,31),
}
for key,value in image_sets.items():
    print(key,[x.name for x in file_paths[value[0]:value[1]+1]])
```

Alignment code in `align.ipynb`:
```
mis_filepath="../example/project_e/project_e-2-no_rel-cal.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=1672,filter=Filter.simple))
...
imrc=IMRControls(mis_project,imshow_kwargs=dict(cmap="gray",vmin=0,vmax=255))
...
mis_filepath="../example/project_e/demo-project_e-2-rel-cal.mis.json"
```

```
mis_filepath="../example/project_e/project_e-8-no_rel-cal.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=1672,filter=Filter.simple))
...
imrc=IMRControls(mis_project,imshow_kwargs=dict(cmap="gray",vmin=0,vmax=255))
...
mis_filepath="../example/project_e/demo-project_e-8-rel-cal.mis.json"
```

Render code in `render.ipynb`:
```
mis_filepath=r"../example/project_e/project_e-2-rel-cal.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=1672,filter=Filter.simple))
...
selected_image=selected_image.transpose(Transpose.ROTATE_90)
...
image_with_scale_bar(
    image=selected_image,
    scale_measurement="100um",
    calibration=selected_calibration,
    loc="upper right")
```

```
mis_filepath=r"../example/project_e/project_e-8-rel-cal.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
from misalign.model.image import Filter, Modifier
mis_project.set_image_filter(Modifier.crop(bottom=1672,filter=Filter.simple))
...
selected_image=selected_image.transpose(Transpose.ROTATE_90)
...
image_with_scale_bar(
    image=selected_image,
    scale_measurement="100um",
    calibration=selected_calibration,
    loc="upper right")
```