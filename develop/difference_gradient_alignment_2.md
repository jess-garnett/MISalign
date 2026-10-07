---
jupytext:
  formats: ipynb,md:myst
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

# Plotting Functions for Pairwise Registration

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import axes_grid1
# import scipy as sp
# import skimage as ski


from misalign.model.project import MISProjectJSON, MISProject
from misalign.model.relation import MISRelation
from misalign.model.image import HasArray
import misalign.canvas.canvas_rectangular as cr
from misalign.alignment import auto_rectangular_skimage as arski

from typing import Any
from collections.abc import Callable
```

```{code-cell} ipython3
# %matplotlib widget
%matplotlib inline
```

```{code-cell} ipython3
project_configs:list[dict]=[
    dict(mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json",
        primary_filter=arski.Filter.simple,
        local_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
        full_interpolation_filter=arski.Filter.rgb_gray_mean,
        full_phase_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
        full_strategy_edge_avoid=50,full_strategy_downsample=1,
        ),
    # dict(mis_filepath="../example/project_b/project_b-relations-calibrated.mis.json",
    #     primary_filter=arski.Filter.simple,
    #     local_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
    #     full_interpolation_filter=arski.Filter.rgb_gray_mean,
    #     full_phase_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
    #     full_strategy_edge_avoid=200,full_strategy_downsample=1,
    #     ),
    # dict(mis_filepath="../example/project_c/project_c-relations-calibrated.mis.json",
    #     primary_filter=arski.Filter.simple,
    #     local_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
    #     full_interpolation_filter=arski.Filter.rgb_gray_mean,
    #     full_phase_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
    #     full_strategy_edge_avoid=100,full_strategy_downsample=1,
    #     ),
    # dict(mis_filepath="../example/project_d/project_d-relations-calibrated.mis.json",
    #     primary_filter=arski.Filter.simple,
    #     local_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
    #     full_interpolation_filter=arski.Filter.rgb_gray_mean,
    #     full_phase_filter=arski.ModifierSkimage.scharr_edge(filter=arski.Filter.rgb_gray_mean),
    #     full_strategy_edge_avoid=100,full_strategy_downsample=1,
    #     ),
    # dict(mis_filepath="../example/project_e/project_e-2-rel-cal.mis.json",
    #     primary_filter=arski.Modifier.crop(bottom=1672,filter=arski.Filter.simple),
    #     local_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     full_interpolation_filter=arski.Filter.float,
    #     full_phase_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     full_strategy_edge_avoid=100,full_strategy_downsample=5,
    #     ),
    # dict(mis_filepath="../example/project_e/project_e-8-rel-cal.mis.json",
    #     primary_filter=arski.Modifier.crop(bottom=1672,filter=arski.Filter.simple),
    #     local_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     full_interpolation_filter=arski.Filter.float,
    #     full_phase_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     full_strategy_edge_avoid=100,full_strategy_downsample=5,
    #     ),
    # dict(mis_filepath="../example/project_f/project_f-relations-calibrated.mis.json",
    #     primary_filter=arski.Modifier.crop(bottom=4096,right=4096,filter=arski.Filter.simple_uint16),
    #     local_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     full_interpolation_filter=arski.Filter.float,
    #     full_phase_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     registration_filter=arski.ModifierSkimage.median_disk(filter=arski.Filter.float),
    #     full_strategy_edge_avoid=100,full_strategy_downsample=10,
    #     ),
]
```

```{code-cell} ipython3
plt.close('all')
for project in project_configs:
    mis_project=MISProjectJSON.load(mis_filepath=project["mis_filepath"])
    mis_project.find_image_paths(mis_filepath=project["mis_filepath"])
    mis_project.set_image_filter(filter=project["primary_filter"])
    i=0
    for relation in mis_project.get_relations():
        if i<2: # Only run the first n relations in each project.
            i+=1
        else:
            break
        # if "c27" not in str(relation.get_reference()): # only run matching relation
        #     continue
        registration_result:Any=arski.pairwise_registration_project(
            project=mis_project,
            relation=relation,
            strategy=arski.StrategyLocal.local_minima_grid,
            metric=arski.LocateMetric.mean_squared_difference,
            filter=project["local_filter"],
            strategy_max_size=10,
            strategy_footprint_shape=(5,5)
            )
        reference_optimized=registration_result.optimized_offset
        composite=arski.plot_result(project=mis_project,relation=relation,axs=None,result=registration_result,
            plot_kwargs={
                arski.plot_process_overlap:dict(filter=project["local_filter"]),
                },)
        plt.show()

        registration_result:Any=arski.pairwise_registration_project(
            project=mis_project,
            relation=relation,
            strategy=arski.StrategyFullSearch.interpolated_adaptive_grid,
            metric=arski.LocateMetricSkimage.modified_pearson,
            filter=project["full_interpolation_filter"],
            strategy_edge_avoid=project["full_strategy_edge_avoid"],
            )
        composite=arski.plot_result(project=mis_project,relation=relation,axs=None,result=registration_result,
            plot_kwargs={
                arski.plot_interpolation_grid:dict(reference_offset=reference_optimized),
                arski.plot_process_overlap:dict(filter=project["full_interpolation_filter"]),
                },)
        plt.show()

        registration_result:Any=arski.pairwise_registration_project(
            project=mis_project,
            relation=relation,
            strategy=arski.StrategyFullSearch.prediction_grid,
            metric=arski.LocateMetricSkimage.modified_pearson,
            filter=project["full_phase_filter"],
            strategy_edge_avoid=project["full_strategy_edge_avoid"],
            strategy_downsample=project["full_strategy_downsample"],
            )
        composite=arski.plot_result(project=mis_project,relation=relation,axs=None,result=registration_result,
            plot_kwargs={
                arski.plot_predict_sparse:dict(reference_offset=reference_optimized),
                },)
        plt.show()

        registration_result:Any=arski.pairwise_registration_project(
            project=mis_project,
            relation=relation,
            strategy=arski.StrategyFullSearch.composite_predict_local,
            metric=arski.LocateMetricSkimage.modified_pearson,
            filter=project["full_phase_filter"],
            strategy_prediction_kwargs=dict(
                strategy_edge_avoid=project["full_strategy_edge_avoid"],
                strategy_downsample=project["full_strategy_downsample"],
                ),
            strategy_local_kwargs=dict(
                strategy_max_size=10,
                strategy_footprint_shape=(5,5),
                metric=arski.LocateMetric.mean_squared_difference,
                ),
            )
        composite=arski.plot_result(project=mis_project,relation=relation,axs=None,result=registration_result,
            plot_kwargs={
                arski.plot_process_overlap:dict(filter=project["full_phase_filter"]),
                arski.plot_predict_sparse:dict(
                    reference_offset=reference_optimized,
                    ),
                },)
        plt.show()
```

```{code-cell} ipython3
#TODO add more pass through kwargs
```
