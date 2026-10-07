---
jupytext:
  formats: notebooks///ipynb,scripts///md:myst
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

# SEM Trim & Convert
For trimming footer of SEM images and converting into uint8/RGB which is presently needed for further processing

```{code-cell} ipython3
#TODO Remove need for RGB/uint8 conversion
#TODO Rework SEM Trim & Convert to use MISProject/MISImage
```

```{code-cell} ipython3
from sys import path as syspath
syspath.append("..")
```

```{code-cell} ipython3
# from misalign.model.mis_file import load_mis
from misalign.model.project import MISProjectJSON
from PIL import Image as PILImage
import numpy as np
# from shutil import copy2
# from os.path import split, join
# from os import mkdir
from pathlib import Path
```

```{code-cell} ipython3
mis_fp=".mis.json"
mis_project=MISProjectJSON.load(mis_fp)
mis_modified_folder=Path("")
# mis_image_paths=mis_project.get_image_paths()
# mis_image_paths
```

```{code-cell} ipython3
# split_mis_fp=split(mis_fp)
# original_image_folder=join(split_mis_fp[0],"original_images")
# mkdir(original_image_folder)
# for img_name, img_fp in mis_image_paths.items():
#     split_img_fp=split(img_fp)
#     copy_img_fp=join(original_image_folder,split_img_fp[1])
#     print(img_fp," > ",copy_img_fp)
#     copy2(img_fp,copy_img_fp)
```

```{code-cell} ipython3
# pixels_to_trim=248
# for img_name, img_fp in mis_image_paths.items():
#     img_arr=np.asarray(PILImage.open(img_fp))
#     if img_arr.dtype=="uint16":
#         img_arr=(img_arr//256).astype(np.uint8)
#     img_arr_trimmed=img_arr[:-248]
#     img_corrected=PILImage.fromarray(img_arr_trimmed).convert('RGB')
#     img_corrected.save(img_fp)

pixels_to_trim=248
for image_name in mis_project.get_image_names():
    img_arr=np.array(mis_project.get_image(image_name))
    if img_arr.dtype=="uint16":
        img_arr=(img_arr//256).astype(np.uint8)
    img_arr_trimmed=img_arr[:-248]
    img_corrected=PILImage.fromarray(img_arr_trimmed)
    img_corrected.save(mis_modified_folder.joinpath(image_name))
```

# `.mis` to `.json` Converter
Updated a lot of core program functionality. This converts the old save files to the new format.

```{code-cell} ipython3
from sys import path as syspath
syspath.append("..")
from misalign.model.project import convert_mis_project_json,MISProjectJSON
```

```{code-cell} ipython3
old_path="../example/data/set_a/set_a2_calibrated.mis"
mp=convert_mis_project_json(old_path)
new_path=old_path.replace(".mis",".mis.json")
mp.save(new_path)
```

# `.hdf5` Project Snippet
Code snippet to use for loading `.hdf5` project files.

```{code-cell} ipython3
from misalign.model.hdf5 import load_mis_project_hdf5
hdf5_path=r"../tests/test_files/mytestfile1.hdf5"
mis_project=load_mis_project_hdf5(hdf5_path)
```
