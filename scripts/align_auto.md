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

# Automated Image Alignment

+++

Note: Fully automated alignment requires scikit-image and/or scipy. You can configure your virtual environment to include those libraries with `uv sync --extra sci`.

+++

**Imports**

```{code-cell} ipython3
from misalign.model.project import MISProjectJSON
from misalign.model.relation import MISRelationRectangular, MISRelationReference
from misalign.alignment import auto_rectangular_skimage as arski
```

## Alignment With Initial Offset

+++

This approach is intended to be used when you have pre-existing relations such as from doing manual alignment.

```{code-cell} ipython3
mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)
print(mis_project)
```

```{code-cell} ipython3
local_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean)
```

```{code-cell} ipython3
%matplotlib inline
optimized_relations=dict()
for i,relation in enumerate(mis_project.get_relations()):
    registration_result=arski.pairwise_registration_project(
        project=mis_project,
        relation=relation,
        strategy=arski.StrategyLocal.local_minima_grid,
        metric=arski.LocateMetric.mean_squared_difference,
        filter=local_filter,
        strategy_max_size=10,
        strategy_footprint_shape=(5,5)
        )
    optimized_relations[i]=MISRelationRectangular(
        image_pair=relation.get_reference(),
        rectangular=registration_result.optimized_offset,
        note="Aligned with `StrategyLocal.local_minima_grid`")
    composite=arski.plot_result(project=mis_project,relation=relation,axs=None,result=registration_result,
        plot_kwargs={
            arski.plot_process_overlap:dict(filter=local_filter),
            },)
```

```{code-cell} ipython3
exclude_relations:list[int]=[] # list of relation indices for any relations that should not be updated.
for i,relation in optimized_relations.items():
    if i in exclude_relations:
        continue
    mis_project.set_relation(relation_index=i,relation=relation)
print(mis_project)
```

```{code-cell} ipython3
# save updated mis project with image relations
mis_filepath="../example/project_a/demo-project_a-relations-auto_local-calibrated.mis.json"
mis_project.save(mis_filepath)
```

## Alignment Without Initial Offset

+++

This approach is intended to be used when you do not have pre-existing relations.

```{code-cell} ipython3
mis_filepath="../example/project_a/project_a-no_relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)
print(mis_project)
```

If every image is related to the next image you can use the following code to setup simple offsets, if not you may need to manually add reference relations for each image pair.

```{code-cell} ipython3
for image_a,image_b in zip(mis_project.get_image_names()[0:-1],mis_project.get_image_names()[1:]):
    mis_project.add_relation(MISRelationReference(image_pair=(image_a,image_b)))
print(mis_project)
```

```{code-cell} ipython3
full_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean)
full_strategy_edge_avoid=50
full_strategy_downsample=1
```

```{code-cell} ipython3
%matplotlib inline
optimized_relations=dict()
for i,relation in enumerate(mis_project.get_relations()):
    registration_result=arski.pairwise_registration_project(
        project=mis_project,
        relation=relation,
        strategy=arski.StrategyFullSearch.composite_predict_local,
        metric=arski.LocateMetricSkimage.modified_pearson,
        filter=full_filter,

        strategy_prediction_kwargs=dict(
            strategy_edge_avoid=full_strategy_edge_avoid,
            strategy_downsample=full_strategy_downsample,
            ),
        strategy_local_kwargs=dict(
            strategy_max_size=10,
            strategy_footprint_shape=(5,5),
            metric=arski.LocateMetric.mean_squared_difference,
            ),
        )
    optimized_relations[i]=MISRelationRectangular(
        image_pair=relation.get_reference(),
        rectangular=registration_result.optimized_offset,
        note="Aligned with `StrategyFullSearch.composite_predict_local`")
    composite=arski.plot_result(project=mis_project,relation=relation,axs=None,result=registration_result,
        plot_kwargs={
            arski.plot_process_overlap:dict(filter=full_filter),
            },)
```

```{code-cell} ipython3
exclude_relations:list[int]=[] # list of relation indices for any relations that should not be updated.
for i,relation in optimized_relations.items():
    if i in exclude_relations:
        continue
    mis_project.set_relation(relation_index=i,relation=relation)
print(mis_project)
```

```{code-cell} ipython3
# save updated mis project with image relations
mis_filepath="../example/project_a/demo-project_a-relations-auto_full-calibrated.mis.json"
mis_project.save(mis_filepath)
```
