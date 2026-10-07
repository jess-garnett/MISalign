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

# Testing of different metric functions

```{code-cell} ipython3
from misalign.alignment import difference_rectangular
import auto_rectangular_metric  # ty:ignore[unresolved-import]

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
```

```{code-cell} ipython3
selected_metrics={
                "mean-squared":difference_rectangular.LocateMetric.mean_squared_difference,
                "msd_normalized":lambda a,b:difference_rectangular.LocateMetric.mean_squared_difference(
                    ((a-np.mean(a))/np.std(a)),((b-np.mean(b))/np.std(b))),
            }
selected_metric="msd_normalized"
calibrate=False
registration=True
project_configs=[
    # dict(mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json",filter=difference_rectangular.Filter.rgb_gray_mean,full_strategy_edge_avoid=50),
    # dict(mis_filepath="../example/project_b/project_b-relations-calibrated.mis.json",filter=difference_rectangular.Filter.rgb_gray_mean,full_strategy_edge_avoid=200),
    # dict(mis_filepath="../example/project_c/project_c-relations-calibrated.mis.json",filter=difference_rectangular.Filter.rgb_gray_mean,full_strategy_edge_avoid=100),
    # dict(mis_filepath="../example/project_d/project_d-relations-calibrated.mis.json",filter=difference_rectangular.Filter.rgb_gray_mean,full_strategy_edge_avoid=100),
    dict(mis_filepath="../example/project_e/project_e-2-rel-cal.mis.json",filter=difference_rectangular.Modifier.crop(bottom=1672,filter=difference_rectangular.Filter.float),full_strategy_edge_avoid=100),
    dict(mis_filepath="../example/project_e/project_e-8-rel-cal.mis.json",filter=difference_rectangular.Modifier.crop(bottom=1672,filter=difference_rectangular.Filter.float),full_strategy_edge_avoid=100),
    dict(mis_filepath="../example/project_f/project_f-relations-calibrated.mis.json",filter=difference_rectangular.Modifier.crop(bottom=4096,right=4096,filter=difference_rectangular.Filter.float),full_strategy_edge_avoid=100),
]
```

```{code-cell} ipython3
for config in project_configs:
    mt=auto_rectangular_metric.MetricsTest(
        auto_rectangular_metric.setup_project(config["mis_filepath"]),
        filter=config["filter"],
        metrics=selected_metrics,
        )
    if calibrate:
        mt.calibrate_metrics(0)
        mt.update_metrics({
            "quantile-absolute-99.9":lambda a,b:(np.quantile(np.abs(a-b),0.999)),
            "msd_normalized":lambda a,b:difference_rectangular.LocateMetric.mean_squared_difference(
                ((a-np.mean(a))/np.std(a)),((b-np.mean(b))/np.std(b))),
            })
        mt.calibrate_metrics()

        mt.plot_metrics()
        summary=mt.summary_metrics()

    if registration:
        project_summary=mt.pairwise(
            metric_name=selected_metric,
            # selected_indeces=[0],
            local_kwargs=dict(
                strategy_max_size=10
                ),
            full_kwargs=dict(
                strategy_full_search_progression=
                        [dict(initial_grid_number=40),
                        dict(quantile=0.1,spacing=32,),
                        dict(quantile=0.01,spacing=16,),
                        dict(quantile=0.001,spacing=8,),
                        dict(quantile=0.0001,spacing=4,)],
                strategy_edge_avoid=config["full_strategy_edge_avoid"],
                strategy_initial_grid_number=30,
                ),
            plot=True
        )
        print(pd.DataFrame(project_summary).to_markdown())
```
