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

# Align Images

+++

**Imports**

```{code-cell} ipython3
from misalign.model.project import MISProjectJSON
from misalign.alignment.interactive_manual import IMRControls
```

## Basic Alignment

```{code-cell} ipython3
mis_filepath="../example/project_a/project_a-no_relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)
print(mis_project)
```

```{code-cell} ipython3
%matplotlib widget
imrc=IMRControls(mis_project)
```

```{code-cell} ipython3
# retrieve project with updated image relations from imrc
mis_project=imrc.get_mis()
print(mis_project)
```

```{code-cell} ipython3
# save updated mis project with image relations
mis_filepath="../example/project_a/demo-project_a-relations-calibrated.mis.json"
mis_project.save(mis_filepath)  # ty:ignore[unresolved-attribute]
```
