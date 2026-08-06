Project B includes 39 images of two cut pieces of zinc-galvanized low-carbon steel bar(https://www.mcmaster.com/8962K13-8962K23/) mounted in resin, ground(silicon carbide 60, 80, 120, 320, 600, 800, and 1200 grit), and polished(polycrystalline diamond 1um). They were captured with the same 5x objective lens as `project_a`. These images were taken on 2024-03-08 by Jessica Garnett.

Below are example modifications to the notebooks to demo thisproject.

Setup code in `setup.ipynb`:
```
###
# Enter setup information
###
folder_path=Path("../example/project_b") # folder with images
misfile_name="demo-project_b-no_relations-calibrated.mis.json" # name for save file
#
calibration_filepath=Path("../example/project_a/scale_5x_1mm.miscal.json")
    # filepath to calibration file `.miscal.json`
#
file_ending=".tif" # file extension
file_contains="" # file names must contain - i.e. "sample1-5x", "sample2", "10x", etc.
file_notcontains="" # file names must not contain - i.e. "calibration"
```

Alignment code in `align.ipynb`:
```
mis_filepath="../example/project_b/project_b-no_relations-calibrated.mis.json"
...
mis_filepath="../example/project_b/demo-project_b-relations-calibrated.mis.json"
```

Render code in `render.ipynb`:
```
mis_filepath="../example/project_b/project_b-relations-calibrated.mis.json"
...
selected_image=selected_image
...
image_with_scale_bar(
    image=selected_image,
    scale_measurement="5mm",
    calibration=selected_calibration,
    loc="upper left")
```