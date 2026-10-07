---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: .venv (3.10.8)
  language: python
  name: python3
---

# Notebook for generating example results.

```{code-cell} ipython3
import sys
import os
sys.path.insert(0, os.path.abspath(".."))  # Repository directory relative to this file.
```

## test_model_image.py

```{code-cell} ipython3
# from MISalign.model.image import Image
# import numpy as np
# test_img_a01=r"..\example\data\set_a\a_myimages01.jpg"
# test_image=Image(test_img_a01)
```

```{code-cell} ipython3
# test_dfe_arr_fp=r"..\example\expected_result\set_a\dfe_rectangular.npy"
# np.save(test_dfe_arr_fp,test_image.dfe_arr())
```

```{code-cell} ipython3
# test_img_arr_fp=r"..\example\expected_result\set_a\img_a01.npy"
# np.save(test_img_arr_fp,test_image.img_arr())
```

# test_model_mis_file.py

```{code-cell} ipython3
# from MISalign.model.mis_file import MisFile,save_mis,load_mis
# from MISalign.model.relation import Relation

# test_mis_none=MisFile()

# test_image_fps=["test_a.png","test_b.png","test_c.png"]
# test_mis_img=MisFile(image_fps=test_image_fps)

# test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
# test_mis_rel=MisFile(relations=test_relations)

# test_image_fps=["test_a.png","test_b.png","test_c.png"]
# test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
# test_mis_img_rel=MisFile(image_fps=test_image_fps,relations=test_relations)


# save_mis(r"..\example\expected_result\test\none.mis",test_mis_none)
# save_mis(r"..\example\expected_result\test\img.mis",test_mis_img)
# save_mis(r"..\example\expected_result\test\rel.mis",test_mis_rel)
# save_mis(r"..\example\expected_result\test\img_rel.mis",test_mis_img_rel)
```

```{code-cell} ipython3
# print(load_mis(r"..\example\expected_result\test\none.mis"))
# print(load_mis(r"..\example\expected_result\test\img.mis"))
# print(load_mis(r"..\example\expected_result\test\rel.mis"))
# print(load_mis(r"..\example\expected_result\test\img_rel.mis"))
```

# project_service.py deprecation

```{code-cell} ipython3
# from os import getcwd
# from MISalign.model.project_service import load_from_mis
# ref_old_proj="../example/data/set_a/a_myproject_full.mis"
# test_old_project=load_from_mis(ref_old_proj)
```

```{code-cell} ipython3
# display(test_old_project.offsets)
# display(getcwd())
```

```{code-cell} ipython3
# from MISalign.model.project_service import deprecate_project_offset_mis
# ref_old_proj="./a_myproject_full.mis"
# new_misfile=deprecate_project_offset_mis(ref_old_proj)
```

```{code-cell} ipython3
# print(new_misfile)
```

```{code-cell} ipython3
# print(new_misfile.get_rels(relation='r'))
```

# HDF5 Plugin

```{code-cell} ipython3
from sys import path as syspath
syspath.append("..")
import h5py
import MISalign.plugin.hdf5 as hdf5
from MISalign.model.project import MISProjectJSON
import json
import numpy as np
```

```{code-cell} ipython3
# %pip install h5py
```

```{code-cell} ipython3
f = h5py.File("test_files/mytestfile1.hdf5", "w") #a for read/write, w for create new
f.keys()
```

```{code-cell} ipython3
mp=MISProjectJSON().load(r"..\example\data\set_a\set_a2_calibrated.json")
```

```{code-cell} ipython3
# [mp.get_image(image_name).get_image_array() for image_name in mp.get_image_names()]
```

```{code-cell} ipython3
f.create_group("images")
for image_name in mp.get_image_names()[0:3]: #only loading 3 images/2 relations to keep file size below 50mb
    f["images"].create_dataset(image_name,data=mp.get_image(image_name).get_image_array()) # type: ignore
    f["images"][image_name].attrs["image_type"]= "hdf5" # type: ignore
    f["images"][image_name].attrs["image_name"]= image_name # type: ignore
    f["images"][image_name].attrs["hdf5_filepath"]= "test_files/mytestfile1.hdf5"  # type: ignore
    f["images"][image_name].attrs["PIL_mode"]= "RGB" # type: ignore
    f["images"][image_name].attrs.create('CLASS','IMAGE',dtype='<S5')
    f["images"][image_name].attrs.create('IMAGE_SUBCLASS','IMAGE_TRUECOLOR',dtype='<S15')
    f["images"][image_name].attrs.create('INTERLACE_MODE','INTERLACE_PIXEL',dtype='<S15')
    f["images"][image_name].attrs.create('IMAGE_VERSION','1.2',dtype='<S3')
f.create_dataset("relations",data=[json.dumps(x) for x in mp.save_dict()["relations"][0:2]])

f.create_group("calibration")
for key,value in mp.get_calibration().items():
    f["calibration"].attrs[key]=value
```

```{code-cell} ipython3
f.visit(lambda x:print(x,f[x],f[x].attrs.keys()))
# calibration - group
    # attrs key:value
# images - group
    # image_name1 - dataset
        # attrs: PIL_mode:"RGB"
        # attrs: key:value
    # image_name2 - dataset
        # ... 
# relations - dataset
    # array of json.dumps() strings
# project - group
    # attrs key:json.dumps() strings
    # Stores all other project data
```

```{code-cell} ipython3
f.close()
```

```{code-cell} ipython3
with h5py.File("test_files/plugin_hdf5/mytestfile1.hdf5", "r") as f:
    f.visit(lambda x:print(x,f[x],f[x].attrs.keys()))
```

```{code-cell} ipython3
with h5py.File("test_files/plugin_hdf5/mytestfile1.hdf5", "r") as f:
    # print(f["images/a_myimages01.jpg"].shape)
    print(dict(f["images/test"].attrs))
```

```{code-cell} ipython3
with h5py.File("test_files/plugin_hdf5/mytestfile1.hdf5", "a") as f:
    # print(f["images/a_myimages01.jpg"].shape)
    # test_attrs={'CLASS': b'IMAGE', 'IMAGE_MINMAXRANGE': np.array([  0, 255], dtype=np.uint8), 'IMAGE_SUBCLASS': b'IMAGE_TRUECOLOR', 'IMAGE_VERSION': b'1.2', 'INTERLACE_MODE': b'INTERLACE_PIXEL'}
    f["images/a_myimages02.jpg"].attrs.create('CLASS','IMAGE',dtype='<S5')
    f["images/a_myimages02.jpg"].attrs.create('IMAGE_SUBCLASS','IMAGE_TRUECOLOR',dtype='<S15')
    f["images/a_myimages02.jpg"].attrs.create('INTERLACE_MODE','INTERLACE_PIXEL',dtype='<S15')
    f["images/a_myimages02.jpg"].attrs.create('IMAGE_VERSION','1.2',dtype='<S3')
    print(dict(f["images/a_myimages01.jpg"].attrs))
```
