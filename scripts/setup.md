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

# Project Setup

+++

**Imports**

```{code-cell} ipython3
# from os import listdir
# from os.path import join, abspath, relpath
from pathlib import Path
from misalign.model.project import MISProjectJSON
```

## Basic Setup

```{code-cell} ipython3
###
# Enter setup information
###
folder_path=Path("../example/project_a") # folder with images
misfile_name="demo-project_a-no_relations-calibrated.mis.json" # name for save file
#
calibration_filepath=Path("../example/project_a/scale_5x_1mm.miscal.json")
    # filepath to calibration file `.miscal.json`
#
file_ending=".jpg" # file extension
file_contains="" # file names must contain - i.e. "sample1-5x", "sample2", "10x", etc.
file_notcontains="" # file names must not contain - i.e. "calibration"
```

```{code-cell} ipython3
mis_filepath=folder_path.joinpath(misfile_name)
print(f"Save file filepath: {mis_filepath}")
file_paths=[x for x in folder_path.iterdir() if x.suffix==file_ending]
if file_contains != "":
    file_paths=[x for x in file_paths if file_contains in x.name]
if file_notcontains != "":
    file_paths=[x for x in file_paths if file_notcontains not in x.name]
print("\n  ".join(["Image files and filepaths:"]+[f"{fp.name}: {fp}" for fp in file_paths]))
filepath_dict={fp.name:fp for fp in file_paths}
if calibration_filepath is not None:
    print(f"Calibration file filepath: {calibration_filepath}")
```

```{code-cell} ipython3
mis_project=MISProjectJSON.build(image_filepaths=file_paths,calibration_filepath=calibration_filepath,mis_filepath=mis_filepath)
print(mis_project)
```

```{code-cell} ipython3
mis_project.save(mis_filepath)
```

## Advanced Setups

+++

### Image Sets

```{code-cell} ipython3
###
# Enter setup information
###
folder_path=Path("../example/project_a/") # folder with images
misfile_names=["demo-set_a1a.mis.json","demo-set_a1b.mis.json"] # name for save file
#
calibration_filepath=Path("../example/project_a/scale_5x_1mm.miscal.json")
    # filepath to calibration file `.miscal.json`
#
file_ending=".jpg" # file extension
file_contains="" # file names must contain - i.e. "sample1-5x", "sample2", "10x", etc.
file_notcontains="" # file names must not contain - i.e. "calibration"
###
```

```{code-cell} ipython3
mis_filepaths=[folder_path.joinpath(x) for x in misfile_names]
mis_dict={mn:mp for mn,mp in zip(misfile_names,mis_filepaths)}
print("\n  ".join(["Save files and filepaths: "]+[f"{mn}: {mp}" for mn,mp in zip(misfile_names,mis_filepaths)]))
file_paths=[x for x in folder_path.iterdir() if x.suffix==file_ending]
if file_contains != "":
    file_paths=[x for x in file_paths if file_contains in x]
if file_notcontains != "":
    file_paths=[x for x in file_paths if file_notcontains not in x]
print("\n  ".join(["Image index, file names, and filepaths:"]+[f"{i} - {fp.name}: {fp}" for i,fp in enumerate(file_paths)]))
if calibration_filepath is not None:
    print(f"Calibration file filepath: {calibration_filepath}")
```

```{code-cell} ipython3
# user selected image sets using start and end index
image_sets={
    "demo-set_a1a.mis.json":(0,4),
    "demo-set_a1b.mis.json":(5,9),
}
for key,value in image_sets.items():
    print(key,[x.name for x in file_paths[value[0]:value[1]+1]])
```

```{code-cell} ipython3
for key,value in image_sets.items():
    mis_fp=mis_dict[key]
    print(mis_fp,"\n  ",[x.name for x in file_paths[value[0]:value[1]+1]])
    mis_project=MISProjectJSON.build(image_filepaths=file_paths[value[0]:value[1]+1],calibration_filepath=calibration_filepath,mis_filepath=mis_fp)
    mis_project.save(mis_fp)
```
