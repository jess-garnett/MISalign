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

# Prototyping Difference Gradient Analysis for MISalign 2.0

```{code-cell} ipython3
# %matplotlib widget
%matplotlib inline
```

```{code-cell} ipython3
import numpy as np
from matplotlib import pyplot as plt

from misalign.model.project import MISProjectJSON
import misalign.canvas.canvas_rectangular as cr
from misalign.alignment import difference_rectangular
```

```{code-cell} ipython3
mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)
print(mis_project)
```

```{code-cell} ipython3
plt.close('all')
```

```{code-cell} ipython3
# 2 is fairly well overlapped
# 7 is neat for seeing how physical features effect plot.
# 8 is particularly bad initial alignment and good for visualizing
selected_relation=mis_project.get_relations()[0]
selected_registration_results=difference_rectangular.pairwise_registration(
        image_a=mis_project.get_image(selected_relation.get_reference()[0]),
        image_b=mis_project.get_image(selected_relation.get_reference()[1]),
        relation=selected_relation,
        strategy=difference_rectangular.StrategyLocal.scaled_grid,
        metric=difference_rectangular.LocateMetric.mean_squared_difference,
        # metric=lambda a,b : dr.metric_combined_simple_norm(a,b,modifier_squared=50),
        strategy_max_size=50,
        strategy_grid_scale=1,
        filter=difference_rectangular.Filter.rgb_gray_mean
        )
print("Initial:",selected_registration_results["initial_offset"],"Optimized:",selected_registration_results["optimized_offset"])
```

```{code-cell} ipython3
difference_rectangular.plot_registration_result_grid(
        image_a=mis_project.get_image(selected_relation.get_reference()[0]),
        image_b=mis_project.get_image(selected_relation.get_reference()[1]),
        registration_result_grid=selected_registration_results,
    )
plt.show()
```

```{code-cell} ipython3
relation_index_results=dict()
for i,relation in enumerate(mis_project.get_relations()):
    registration_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(relation.get_reference()[0]),
            image_b=mis_project.get_image(relation.get_reference()[1]),
            relation=relation,
            strategy=difference_rectangular.StrategyLocal.full_grid,
            # metric=difference_rectangular.LocateMetric.mean_absolute_difference,
            metric=metric_custom,
            strategy_max_size=10,
            )
    print(i,":",relation.get_reference(),relation.get_relation('r'),"->",registration_results["optimized_offset"])
    difference_rectangular.plot_registration_result_grid(
        image_a=mis_project.get_image(relation.get_reference()[0]),
        image_b=mis_project.get_image(relation.get_reference()[1]),
        registration_result_grid=registration_results,
    )
    plt.show()
    
```

```{code-cell} ipython3
# [mis_project.set_relation(i,relation) for i,relation in relation_index_results.items()]
# mis_filepath="../example/project_a/project_a-dga_relations-calibrated.mis.json"
# mis_project.save(mis_filepath)
```

# Comparing Performances

```{code-cell} ipython3
import timeit
import pandas as pd
import seaborn as sns
import math
```

```{code-cell} ipython3
# 2 is fairly well overlapped
# 8 is extremely well overlapped
performance_relation=mis_project.get_relations()[2]
performance_optimized_relation=(-124, -1060) # for [2]
performance_dga_results=difference_rectangular.pairwise_registration(
        image_a=mis_project.get_image(performance_relation.get_reference()[0]),
        image_b=mis_project.get_image(performance_relation.get_reference()[1]),
        relation=performance_relation,
        strategy=difference_rectangular.StrategyLocal.scaled_grid,
        metric=difference_rectangular.LocateMetric.mean_squared_difference,
        strategy_max_size=20,
        strategy_grid_scale=1,
        filter=difference_rectangular.Filter.rgb_gray_mean
        )
print("Initial:",performance_dga_results["initial_offset"],"Optimized:",performance_dga_results["optimized_offset"])
def performance_run(kwargs):
    performance_dga_results=difference_rectangular.pairwise_registration(
        image_a=mis_project.get_image(performance_relation.get_reference()[0]),
        image_b=mis_project.get_image(performance_relation.get_reference()[1]),
        relation=performance_relation,
        **kwargs
        )
    # assert performance_dga_results["optimized_offset"]==performance_optimized_relation # this makes sure that the same result is found
    assert math.dist(performance_dga_results["optimized_offset"],performance_optimized_relation)<2 # this makes sure that the result is identical or neighbor to reference.
def get_run_description(kwargs)->dict:
    return {key:(value.__name__ if hasattr(value,"__name__") else value) for key,value in kwargs.items()}
performance_repeats=5
performance_repeats_long=1
performance_results=list()
```

```{code-cell} ipython3
for size in [20,50]:
    kwargs=dict(
        strategy=difference_rectangular.StrategyLocal.full_grid,
        metric=difference_rectangular.LocateMetric.mean_squared_difference,
        strategy_max_size=size,
        filter=difference_rectangular.Filter.float
        )
    run_result=get_run_description(kwargs)
    run_result["average_time"]=timeit.timeit(stmt='performance_run(kwargs)',globals = globals(),number=performance_repeats)/performance_repeats
    print(run_result)
    performance_results.append(run_result)

for size in [20,50,100]:
    kwargs=dict(
        strategy=difference_rectangular.StrategyLocal.full_grid,
        metric=difference_rectangular.LocateMetric.mean_squared_difference,
        strategy_max_size=size,
        filter=difference_rectangular.Filter.rgb_gray_mean
        )
    run_result=get_run_description(kwargs)
    run_result["average_time"]=timeit.timeit(stmt='performance_run(kwargs)',globals = globals(),number=performance_repeats)/performance_repeats
    print(run_result)
    performance_results.append(run_result)
```

```{code-cell} ipython3
for size in [20,50]:
    kwargs=dict(
        strategy=difference_rectangular.StrategyLocal.full_grid,
        metric=difference_rectangular.LocateMetric.mean_absolute_difference,
        strategy_max_size=size,
        filter=difference_rectangular.Filter.float
        )
    run_result=get_run_description(kwargs)
    run_result["average_time"]=timeit.timeit(stmt='performance_run(kwargs)',globals = globals(),number=performance_repeats)/performance_repeats
    print(run_result)
    performance_results.append(run_result)


for size in [20,50,100]:
    kwargs=dict(
        strategy=difference_rectangular.StrategyLocal.full_grid,
        metric=difference_rectangular.LocateMetric.mean_absolute_difference,
        strategy_max_size=size,
        filter=difference_rectangular.Filter.rgb_gray_mean
        )
    run_result=get_run_description(kwargs)
    run_result["average_time"]=timeit.timeit(stmt='performance_run(kwargs)',globals = globals(),number=performance_repeats)/performance_repeats
    print(run_result)
    performance_results.append(run_result)
```

```{code-cell} ipython3
# for size in [20,50]:
#     kwargs=dict(
#         strategy=dr.Strategy.full_grid,
#         metric=dga.metric_combined_balanced,
#         strategy_max_size=size,
#         filter=dr.Filter.rgb_gray_mean
#         )
#     run_result=get_run_description(kwargs)
#     run_result["average_time"]=timeit.timeit(stmt='performance_run(kwargs)',globals = globals(),number=performance_repeats)/performance_repeats
#     print(run_result)
#     performance_results.append(run_result)
```

```{code-cell} ipython3
def metric_custom(overlap_a:np.ndarray,overlap_b:np.ndarray):
    return np.sum([
        difference_rectangular.LocateMetric.max_absolute_difference(overlap_a,overlap_b),
        difference_rectangular.LocateMetric.root_mean_squared_difference(overlap_a,overlap_b),
        difference_rectangular.WeightMetric.highlow_inverse(overlap_a,overlap_b),
    ])

for size in [20,50]:
    kwargs=dict(
        strategy=difference_rectangular.StrategyLocal.full_grid,
        metric=metric_custom,
        strategy_max_size=size,
        filter=difference_rectangular.Filter.rgb_gray_mean
        )
    run_result=get_run_description(kwargs)
    run_result["average_time"]=timeit.timeit(stmt='performance_run(kwargs)',globals = globals(),number=performance_repeats)/performance_repeats
    print(run_result)
    performance_results.append(run_result)
```

```{code-cell} ipython3
#TODO add total time(timeit call)/then average time
```

```{code-cell} ipython3
df_performance=pd.DataFrame(performance_results)
df_performance["average_time"]=np.round(df_performance["average_time"],2)
df_performance["total_checked"]=(2*df_performance["strategy_max_size"]+1)**2
print(df_performance.to_markdown())
```

```{code-cell} ipython3
sns.relplot(
    data=df_performance,
    x='strategy_max_size',
    y='average_time',
    hue='metric',
    style='filter',
    markers=["o","X"],
    kind="line",
    )
sns.relplot(
    data=df_performance,
    x='total_checked',
    y='average_time',
    hue='metric',
    style='filter',
    markers=["o","X"],
    kind="line",
    )
```

# Full Search

```{code-cell} ipython3
import numpy as np
from matplotlib import pyplot as plt

from misalign.model.project import MISProjectJSON
import misalign.canvas.canvas_rectangular as cr
from misalign.alignment import difference_rectangular
```

```{code-cell} ipython3
import pandas as pd
import skimage

import timeit
import logging
from sys import stdout
logging.basicConfig(stream=stdout, level=logging.INFO)
```

```{code-cell} ipython3
%matplotlib widget
# %matplotlib inline
plt.close('all')
```

```{code-cell} ipython3
# mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json"
mis_filepath="../example/project_b/project_b-relations-calibrated.mis.json"
# mis_filepath="../example/project_c/project_c-relations-calibrated.mis.json"
# mis_filepath="../example/project_d/project_d-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)
print(mis_project)
```

```{code-cell} ipython3
# def filter_rgb_gray_mean_gaussian(image):
#     return skimage.filters.gaussian(dr.Filter.rgb_gray_mean(image),sigma=1)
# def filter_rgb_gray_mean_dilate(image):
#     return skimage.morphology.dilation(dr.Filter.rgb_gray_mean(image),skimage.morphology.disk(5))
#     # dilation configured to remove debris on imaging system that shows up as small black dots.
```

```{code-cell} ipython3
full_search_filter=difference_rectangular.Filter.rgb_gray_mean
```

```{code-cell} ipython3
# def metric_cosine_histogram(overlap_a,overlap_b):
#     bins=np.linspace(0,255,51)
#     counts_a,bins_a=np.histogram(overlap_a.flatten(),bins=bins)
#     counts_b,bins_b=np.histogram(overlap_b.flatten(),bins=bins)
#     return np.dot(counts_a, counts_b)/(np.linalg.norm(counts_a)*np.linalg.norm(counts_b))
```

```{code-cell} ipython3
# for relation in mis_project.get_relations()[0:5]:
for relation in [mis_project.get_relations()[26]]:
    image_a=mis_project.get_image(relation.get_reference()[0])
    image_b=mis_project.get_image(relation.get_reference()[1])
    calibration_results_initial=difference_rectangular.calibrate_metrics_initial(
            image_a=image_a,
            image_b=image_b,
            relation_offset=relation,
            metrics={
                # "max-absolute":difference_rectangular.LocateMetric.max_absolute_difference,
                # "quantile-absolute":lambda a,b:(np.quantile(np.abs(a-b),0.95)),
                # "mean-absolute":difference_rectangular.LocateMetric.mean_absolute_difference,
                # "mean-squared":difference_rectangular.LocateMetric.mean_squared_difference,
                # "root-mean-squared":difference_rectangular.LocateMetric.root_mean_squared_difference,
                # "norm-root-mean-squared":difference_rectangular.LocateMetric.norm_root_mean_squared_difference,
                # "highlow-inverse":difference_rectangular.WeightMetric.highlow_inverse,
                # # "phase":metric_phase_correlation_distance,
                # "pearson":difference_rectangular.LocateMetricSkimage.modified_pearson,
                # "pearson-downsample":lambda a,b:difference_rectangular.LocateMetricSkimage.modified_pearson(a[::10,::10],b[::10,::10]),
                # # "mse":skimage.metrics.mean_squared_error,
                # # "norm rmse":skimage.metrics.normalized_root_mse,
                # # "nmi":dr.LocateMetricSkimage.modified_mutual_information,
                # # "structural":lambda a,b:skimage.metrics.structural_similarity(a,b,data_range=np.ptp(a)),
                # "quantile-absolute-99.99":lambda a,b:(np.quantile(np.abs(a-b),0.9999)),
                "quantile-absolute-99.9":lambda a,b:(np.quantile(np.abs(a-b),0.999)),
                # "quantile-absolute-99":lambda a,b:(np.quantile(np.abs(a-b),0.99)),
                # "quantile-absolute-95":lambda a,b:(np.quantile(np.abs(a-b),0.95)),
                # "quantile-absolute-90":lambda a,b:(np.quantile(np.abs(a-b),0.9)),
                # "quantile-absolute-75":lambda a,b:(np.quantile(np.abs(a-b),0.75)),
                # "quantile-absolute-50":lambda a,b:(np.quantile(np.abs(a-b),0.5)),
                # "highlow-max":lambda a,b:np.max([np.ptp(a),np.ptp(b)]),
                # "highlow-min":lambda a,b:np.min([np.ptp(a),np.ptp(b)]),
                # "quantile_absolute_fusion-cosine_hist":lambda a,b:np.mean((np.quantile(np.abs(a-b),[0.999,0.99,0.9])))/(np.max([metric_cosine_histogram(a,b)**2,0.1])),
                # "cosine-hist":lambda a,b:metric_cosine_histogram(a,b)**2
                # "diff_variation":lambda a,b:np.std(a-b),
                # "overlap_variation_a":lambda a,b:np.std(a),
                # "overlap_variation_b":lambda a,b:np.std(b),
                "diff_variation_over_overlap":lambda a,b:np.std(a-b)/(np.std(a)+np.std(b)),
                # "diff_of_std_normalized":lambda a,b:np.std((a/np.std(a))-(b/np.std(b))),
                "msd_normalized":lambda a,b:difference_rectangular.LocateMetric.mean_squared_difference(((a-np.mean(a))/np.std(a)),((b-np.mean(b))/np.std(b))),
                },
            strategies={
                "grid":difference_rectangular.StrategyLocal.full_grid,
                "sparse":difference_rectangular.StrategyFullSearch.interpolated_adaptive_grid,
            },
            strategy_kwargs={
                "grid":dict(strategy_max_size=20),
                "sparse":dict(strategy_full_search_progression=[dict(initial_grid_number=40)]),
            },
            filter=full_search_filter,
            )
```

```{code-cell} ipython3
build_summary=dict()
for metric_name,strategies in calibration_results_initial.items():
    fig, axs=plt.subplots(1,len(strategies)+1)
    axs:dict[str,plt.Axes]={strategy_name:ax for strategy_name,ax in zip(list(strategies.keys())+["histogram"],axs)}

    # fig.tight_layout()
    fig.set_figheight(2)
    fig.set_figwidth(4*(len(strategies)+1))
    fig.suptitle(metric_name)

    build_summary[metric_name]=dict()

    for strategy_name,strategy_result in strategies.items():
        if "interp_results" in strategy_result.keys():
            result_key="interp_results"
        else:
            result_key="grid_results"

        build_summary[metric_name][f"{strategy_name} ptp"]=np.ptp(strategy_result[result_key])
        build_summary[metric_name][f"{strategy_name} min"]=np.min(strategy_result[result_key])
        build_summary[metric_name][f"{strategy_name} max"]=np.max(strategy_result[result_key])

        im=axs[strategy_name].imshow(
            X=strategy_result[result_key],
            extent=(
                np.min(strategy_result["grid"][0])-0.5,
                np.max(strategy_result["grid"][0])+0.5,
                np.max(strategy_result["grid"][1])+0.5,
                np.min(strategy_result["grid"][1])-0.5,), #xmin,xmax,ymin,ymax
            # vmax=0.25*build_summary[metric_name][f"{strategy_name} max"]+0.75*build_summary[metric_name][f"{strategy_name} min"]
            # vmin=0.9*build_summary[metric_name][f"{strategy_name} max"]+0.1*build_summary[metric_name][f"{strategy_name} min"]
            )
        axs[strategy_name].scatter(*relation.get_relation('r'))  # ty:ignore[not-iterable]
        plt.colorbar(im)
        
        # Generate histogram for each strategy
        hist=axs["histogram"].hist(strategy_result[result_key].flatten(),bins=20,histtype="step",label=strategy_name)
        hist[2][0].xy[:,1]=hist[2][0].xy[:,1]/sum(hist[2][0].xy[:,1])  # ty:ignore[not-subscriptable, unresolved-attribute]
    
    # Add legend to histogram
    axs["histogram"].legend()
    axs["histogram"].set_ylim(bottom=0,top=0.4)
    axs["histogram"].set_yticks(ticks=axs["histogram"].get_yticks(),labels=[f'{x:0.0%}' for x in axs["histogram"].get_yticks()])
    plt.show()
print(pd.DataFrame.from_dict(build_summary,orient='index').to_markdown())
```

```{code-cell} ipython3
extracted=dict()
def extract(overlap_a,overlap_b):
    extracted["a"]=overlap_a
    extracted["b"]=overlap_b
    return 0
difference_rectangular.overlap_evaluate(
    array_a=full_search_filter(image_a),array_b=full_search_filter(image_b),
    # for relation in [mis_project.get_relations()[3]]: # c3-4
    # # offset_ab=(467, -1170),
    # # offset_ab=(10, 592),
    # # offset_ab=(100, 592),
    # c10-c11
    # offset_ab=(-268, 567),
    # offset_ab=(-268, 577),
    # offset_ab=(-1137, -510),
    # c26-c27
    offset_ab=(1144, 90),
    # offset_ab=(1485, 102),
    metric=extract)
plt.figure()
plt.imshow(extracted["a"],cmap="gray")
# plt.figure()
# # plt.imshow(np.fft.fftshift(np.fft.ifftn(np.fft.fftn(extracted["a"])*np.fft.fftn(extracted["a"]).conj())).real)
# plt.imshow(np.angle(np.fft.fftshift(np.fft.fftn(extracted["a"]))))
plt.figure()
plt.imshow(extracted["b"],cmap="gray")
# plt.figure()
# # plt.imshow(np.fft.fftshift(np.fft.ifftn(np.fft.fftn(extracted["b"])*np.fft.fftn(extracted["b"]).conj())).real)
# # plt.imshow(np.angle(np.fft.fftshift(np.fft.ifftn(np.fft.fftn(extracted["b"])*np.fft.fftn(extracted["b"]).conj()))))

# plt.imshow(np.angle(np.fft.fftshift(np.fft.fftn(extracted["b"]))))
# plt.figure()
# cross_correlation=np.abs(np.fft.fftshift(np.fft.ifftn((np.fft.fftn(extracted["a"])*np.fft.fftn(extracted["b"]).conj()))))
# # cross_correlation=np.angle(np.fft.fftshift(np.fft.ifftn((np.fft.fftn(extracted["a"])*np.fft.fftn(extracted["b"]).conj()))))
# # cross_correlation=np.fft.fftshift(np.fft.ifftn((np.fft.fftn(extracted["a"])*np.fft.fftn(extracted["b"]).conj()))).real
# # plt.imshow(cross_correlation,vmin=0.75*np.max(cross_correlation)+0.25*np.min(cross_correlation))
# # cross_correlation=np.abs(np.fft.fftshift(np.fft.fftn(extracted["a"])))-np.abs(np.fft.fftshift(np.fft.fftn(extracted["b"])))
# print(np.mean((np.log(cross_correlation))),np.max((np.log(cross_correlation))))
# plt.imshow(cross_correlation)

# plt.figure()
# plt.hist(extracted["a"].flatten(),histtype="step")
# plt.hist(extracted["b"].flatten(),histtype="step")

# bins=np.linspace(0,255,50)
# counts_a,bins_a=np.histogram(extracted["a"].flatten(),bins=bins)
# counts_b,bins_b=np.histogram(extracted["b"].flatten(),bins=bins)
# plt.figure()
# # plt.hist(extracted["a"].flatten(),histtype="step")
# # plt.hist(extracted["b"].flatten(),histtype="step")
# plt.bar((bins[1:]+bins[:-1])/2,counts_a,align="center",width=bins[1]-bins[0],alpha=0.5)
# plt.bar((bins[1:]+bins[:-1])/2,counts_b,align="center",width=bins[1]-bins[0],alpha=0.5)
# print("Cosine Distance between histograms:",np.dot(counts_a, counts_b)/(np.linalg.norm(counts_a)*np.linalg.norm(counts_b)))
# print("L2 Distance between histograms:",np.linalg.norm(counts_a-counts_b))

# def metric_cosine_histogram(overlap_a,overlap_b):
#     bins=np.linspace(0,255,51)
#     counts_a,bins_a=np.histogram(extracted["a"].flatten(),bins=bins)
#     counts_b,bins_b=np.histogram(extracted["b"].flatten(),bins=bins)
#     return np.dot(counts_a, counts_b)/(np.linalg.norm(counts_a)*np.linalg.norm(counts_b))
# print(metric_cosine_histogram(extracted["a"],extracted["b"]))

processed={
    "a":(extracted["a"]-np.mean(extracted["a"]))/np.std(extracted["a"]),
    "b":(extracted["b"]-np.mean(extracted["b"]))/np.std(extracted["b"]),
}
# plt.figure()
# plt.imshow(processed["a"],cmap="gray")
# plt.figure()
# plt.imshow(processed["b"],cmap="gray")
plt.figure()
plt.imshow((extracted["a"]-extracted["b"])**2,cmap="gray")
plt.figure()
plt.imshow((processed["a"]-processed["b"])**2,cmap="gray")
plt.figure()
plt.imshow((processed["a"]-processed["b"]),cmap="gray")
print(difference_rectangular.LocateMetric.mean_squared_difference(extracted["a"],extracted["b"]))
print(difference_rectangular.LocateMetric.mean_squared_difference(processed["a"],processed["b"]))
print(difference_rectangular.LocateMetric.mean_absolute_difference(extracted["a"],extracted["b"]))
print(difference_rectangular.LocateMetric.mean_absolute_difference(processed["a"],processed["b"]))
```

```{code-cell} ipython3
custom={
    # "max-absolute":{"modifier":1/100,"power":1},
    "quantile-absolute":{"modifier":1,"power":1},
    # "mean-absolute":{"modifier":1/100,"power":1},
    # "root-mean-squared":{"modifier":1,"power":1},
    # "norm-root-mean-squared":{"modifier":1,"power":1},
    # "norm-mean-squared":{"modifier":1,"power":1},
    "highlow-inverse":{"modifier":10000,"power":1}
    }

fig, axs=plt.subplots(1,len(strategies))
axs:dict[str,plt.Axes]={strategy_name:ax for strategy_name,ax in zip(strategies.keys(),axs)}
fig.tight_layout()
fig.set_figheight(2)
fig.set_figwidth(4*len(strategies))
fig.suptitle("custom")

custom_grid_results={strategy_name:np.zeros(strategy_results["grid_results"].shape,dtype=np.float64) for strategy_name,strategy_results in strategies.items()}

for metric_name in custom.keys():
    for strategy_name,strategy_results in calibration_results_initial[metric_name].items():

        if "interp_results" in strategy_results.keys():
            result_key="interp_results"
        else:
            result_key="grid_results"
        
        custom_grid_results[strategy_name]+=custom[metric_name]["modifier"]*(strategy_results[result_key]**custom[metric_name]["power"])

for strategy_name,strategy_results in calibration_results_initial[metric_name].items():
    
    im=axs[strategy_name].imshow(
        X=custom_grid_results[strategy_name],
        extent=(np.min(strategy_results["grid"][0])-0.5,
            np.max(strategy_results["grid"][0])+0.5,
            np.max(strategy_results["grid"][1])+0.5,
            np.min(strategy_results["grid"][1])-0.5,), #xmin,xmax,ymin,ymax
            )
    
    if "interp_results" in strategy_results.keys():
            im.set_clim(vmax=np.quantile(custom_grid_results[strategy_name],0.1))
    axs[strategy_name].scatter(*relation.get_relation('r'))  # ty:ignore[not-iterable]
    plt.colorbar(im)
plt.show()
print(custom)
```

```{code-cell} ipython3
def metric_custom(overlap_a:np.ndarray,overlap_b:np.ndarray):
    # return (
    #     # (np.quantile(np.abs(overlap_a-overlap_b),0.99))+
    #     np.mean(np.quantile(np.abs(overlap_a-overlap_b),[0.9999,0.999,0.99,0.95]))+
    #     # (1/100)*difference_rectangular.LocateMetric.max_absolute_difference(overlap_a,overlap_b)+
    #     # dr.LocateMetric.mean_absolute_difference(overlap_a,overlap_b)+
    #     # difference_rectangular.LocateMetric.norm_root_mean_squared_difference(overlap_a,overlap_b)+
    #     # difference_rectangular.LocateMetric.norm_root_mean_squared_difference(overlap_a,overlap_b)+
    #     10000*difference_rectangular.WeightMetric.highlow_inverse(overlap_a,overlap_b)
    #     )
    # return np.std(overlap_a-overlap_b)/(np.std(overlap_a)+np.std(overlap_b))
    # return np.std((overlap_a/np.std(overlap_a))-(overlap_b/np.std(overlap_b)))
    # return np.std((overlap_a/np.std(overlap_a))-(overlap_b/np.std(overlap_b)))*np.mean(np.quantile(np.abs(overlap_a-overlap_b),[0.9999,0.999,0.99,0.95]))
    # return difference_rectangular.LocateMetric.mean_squared_difference(
    #     overlap_a=((overlap_a-np.mean(overlap_a))/np.std(overlap_a)),
    #     overlap_b=((overlap_b-np.mean(overlap_b))/np.std(overlap_b)))
    return difference_rectangular.LocateMetric.mean_absolute_difference(
        overlap_a=((overlap_a-np.mean(overlap_a))/np.std(overlap_a)),
        overlap_b=((overlap_b-np.mean(overlap_b))/np.std(overlap_b)))
```

```{code-cell} ipython3
# for relation in mis_project.get_relations():
for relation in mis_project.get_relations()[0:5]:
# for relation in [mis_project.get_relations()[0]]:
    registration_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(relation.get_reference()[0]),
            image_b=mis_project.get_image(relation.get_reference()[1]),
            relation=relation,
            strategy=difference_rectangular.StrategyLocal.full_grid,
            metric=difference_rectangular.LocateMetric.max_absolute_difference,
            strategy_max_size=10,
            filter=difference_rectangular.Filter.rgb_gray_mean
            )
    dga_metric_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(relation.get_reference()[0]),
            image_b=mis_project.get_image(relation.get_reference()[1]),
            relation=relation,
            strategy=difference_rectangular.StrategyLocal.full_grid,
            metric=metric_custom,
            # metric=lambda a,b:(np.quantile(np.abs(a-b),0.95)),
            strategy_max_size=10,
            filter=full_search_filter,
            )
    # plt.figure()
    # plt.imshow(dga_results["grid_results"])
    optimized_metric=np.min(dga_metric_results["grid_results"])
    print(f"{relation.get_reference()} : {optimized_metric:.2f} : Ref. Offset: {registration_results["optimized_offset"]} Metric Offset: {dga_metric_results["optimized_offset"]}")
```

```{code-cell} ipython3
metric_custom_threshold=0.2
```

```{code-cell} ipython3
plt.close('all')
build_summary=list()
for full_relation in mis_project.get_relations():
# for full_relation in mis_project.get_relations()[0:10]:
# for full_relation in [mis_project.get_relations()[6]]:
# for full_relation in [mis_project.get_relations()[i] for i in [6,7,8,10,11,13,28,]]:
    print(full_relation.get_reference())
    optimized_relation=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            relation=full_relation,
            strategy=difference_rectangular.StrategyLocal.full_grid,
            metric=metric_custom,
            strategy_max_size=10,
            filter=difference_rectangular.Filter.rgb_gray_mean
            )["optimized_offset"]
    start_time=timeit.default_timer()
    full_dga_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            # relation=full_relation,
            relation=None,
            strategy=difference_rectangular.StrategyFullSearch.interpolated_adaptive_grid,
            metric=metric_custom,
            filter=full_search_filter,
            strategy_edge_avoid=100,
            strategy_initial_grid_number=30,
            strategy_metric_comparison=metric_custom_threshold
            )
    end_time=timeit.default_timer()
    print(f"Reference Optimized: {optimized_relation} Full Search DGA Optimized: {full_dga_results["optimized_offset"]} Time: {end_time-start_time:0.1f}s")
    fig, (ax1,ax2)=plt.subplots(1,2,sharex=True,sharey=True)

    ax1.imshow(full_dga_results["grid_results"],
            extent=(np.min(full_dga_results["grid"][0])-0.5,
                    np.max(full_dga_results["grid"][0])+0.5,
                    np.max(full_dga_results["grid"][1])+0.5,
                    np.min(full_dga_results["grid"][1])-0.5,), #xmin,xmax,ymin,ymax)
            vmax=np.quantile(full_dga_results["interp_results"],0.5)
            )

    ax1.scatter(*optimized_relation,marker="X",c='r')
    ax1.scatter(*full_dga_results["optimized_offset"],marker="o",c='pink',alpha=0.5)

    ax2.imshow(full_dga_results["interp_results"],
            extent=(np.min(full_dga_results["grid"][0])-0.5,
                    np.max(full_dga_results["grid"][0])+0.5,
                    np.max(full_dga_results["grid"][1])+0.5,
                    np.min(full_dga_results["grid"][1])-0.5,), #xmin,xmax,ymin,ymax)
            vmax=np.quantile(full_dga_results["interp_results"],0.5)
            )

    ax2.scatter(*optimized_relation,marker="X",c='r')
    ax2.scatter(*full_dga_results["optimized_offset"],marker="o",c='pink',alpha=0.5)

    fig.set_figwidth(12)
    plt.show()
    build_summary.append({
        "reference":full_relation.get_reference(),
        "total_checked":np.sum(~np.isnan(full_dga_results["grid_results"])),
        "total_time":round(end_time-start_time,1),
        "reference_offset":optimized_relation,
        "optimized_offset":full_dga_results["optimized_offset"],
        "optimized_metric":round(np.nanmin(full_dga_results["grid_results"]),2),
        })
print(pd.DataFrame(build_summary).to_markdown())
```

```{code-cell} ipython3
plt.figure()
pd.DataFrame(build_summary)["optimized_metric"].hist(bins=14)
plt.show()
```

```{code-cell} ipython3
plt.close('all')
```

```{code-cell} ipython3
from matplotlib.patches import Rectangle
```

```{code-cell} ipython3
print(f"Reference Optimized: {optimized_relation} Full Search DGA Optimized: {full_dga_results["optimized_offset"]} Time: {end_time-start_time:0.1f}s")
fig1,(ax1,ax2)=plt.subplots(nrows=1,ncols=2)
ax1:plt.Axes
ax2:plt.Axes

focus=101

im1=ax1.imshow(
    X=full_dga_results["interp_results"],
    extent=(np.min(full_dga_results["grid"][0])-0.5,
            np.max(full_dga_results["grid"][0])+0.5,
            np.max(full_dga_results["grid"][1])+0.5,
            np.min(full_dga_results["grid"][1])-0.5,) #xmin,xmax,ymin,ymax)
    )
cb1=plt.colorbar(mappable=im1)
# ax1.scatter(*optimized_relation,marker="X",c='r')
ax1.scatter(*full_dga_results["optimized_offset"],marker="o",c='pink')

ax1.add_artist(
    Rectangle(
        xy=(optimized_relation[0]-focus/2,optimized_relation[1]-focus/2),
        width=focus,
        height=focus,facecolor="none", edgecolor='r'),
    )

im2=ax2.imshow(
    X=full_dga_results["grid_results"],
    extent=(np.min(full_dga_results["grid"][0])-0.5,
            np.max(full_dga_results["grid"][0])+0.5,
            np.max(full_dga_results["grid"][1])+0.5,
            np.min(full_dga_results["grid"][1])-0.5,), #xmin,xmax,ymin,ymax)
    vmax=np.nanquantile(full_dga_results["interp_results"],0.1)
    )
cb2=plt.colorbar(mappable=im2)
# ax2.scatter(*optimized_relation,marker="X",c='r')
ax2.scatter(*full_dga_results["optimized_offset"],marker="o",c='pink')
ax2.set_xlim(left=optimized_relation[0]-focus/2,right=optimized_relation[0]+focus/2)
ax2.set_ylim(top=optimized_relation[1]-focus/2,bottom=optimized_relation[1]+focus/2)

fig1.set_figwidth(12)
plt.tight_layout()

inset=500

mosaic=[["tl","tc","tr"],["ml","mc","mr"],["bl","bc","br"]]
fig2,axs=plt.subplot_mosaic(mosaic=mosaic) # top/middle/bottom - left/right/center

for row in mosaic:
    for position in row:
        if position=="mc":
            offset=full_dga_results["optimized_offset"]
        else:
            match position[0]:
                case "t":
                    y_index=+inset
                case "m":
                    y_index=int(full_dga_results["grid_results"].shape[0]/2)
                case "b":
                    y_index=-inset
            match position[1]:
                case "l":
                    x_index=-inset
                case "c":
                    x_index=int(full_dga_results["grid_results"].shape[1]/2)
                case "r":
                    x_index=inset
            offset=tuple(full_dga_results["grid"][:,y_index,x_index].tolist())
            ax1.scatter(offset[0],offset[1],marker="s",c="k",zorder=10)
        # print(offset)
        plt.sca(axs[position])
        if position=="mc":
            plt.title("Optimized Flat Blend")
        difference_rectangular.plot_rectangular_pair(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            offset=offset,
            weight=cr.weight_flat,
            focus_overlap=False,
            )
fig2.set_figwidth(12)
fig2.set_figheight(12)
plt.tight_layout()
plt.show()
```

# Phase Correlation Test

```{code-cell} ipython3
import logging
import timeit

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import skimage

from misalign.model.project import MISProjectJSON
from misalign.alignment import difference_rectangular
```

```{code-cell} ipython3
mis_filepath="../example/project_b/project_b-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)

# phase_filter=dr.filter_rgb_gray_mean
# phase_filter=difference_rectangular.ModifierSkimage.scharr_edge(filter=difference_rectangular.Filter.rgb_gray_mean)
phase_filter=difference_rectangular.Filter.rgb_gray_mean

relation=mis_project.get_relations()[2]

image_a=mis_project.get_image(relation.get_reference()[0])
image_b=mis_project.get_image(relation.get_reference()[1])

reference_offset:tuple[int,int]=relation.get_relation('r')  # ty:ignore[invalid-assignment]
optimized_offset:tuple[int,int]=difference_rectangular.pairwise_registration(
        image_a=image_a,
        image_b=image_b,
        relation=relation,
        strategy=difference_rectangular.StrategyLocal.full_grid,
        metric=difference_rectangular.LocateMetric.max_absolute_difference,
        strategy_max_size=10,
        filter=difference_rectangular.Filter.rgb_gray_mean
        )["optimized_offset"]
print("Optimized:",optimized_offset,"Reference:",reference_offset)
```

```{code-cell} ipython3
print(difference_rectangular.PredictSkimage.phase_cross_correlation(
    array_a=phase_filter(image_a),
    array_b=phase_filter(image_b),
    offset_ab=optimized_offset,
))

print(difference_rectangular.PredictSkimage.phase_cross_correlation(
    array_a=phase_filter(image_a),
    array_b=phase_filter(image_b),
    offset_ab=reference_offset,
))
```

```{code-cell} ipython3
optimized_offset=(-6, -501)
modified_offset=(optimized_offset[0]+6,optimized_offset[1]+6)
difference_rectangular.plot_registration_result_grid(image_a,image_b,
    registration_result_grid=difference_rectangular.StrategyLocal.full_grid(
        array_a=phase_filter(image_a),
        array_b=phase_filter(image_b),
        initial_offset=modified_offset,
        metric=lambda a,b:
                # difference_rectangular.LocateMetric.norm_root_mean_squared_difference(a,b)+
                # (difference_rectangular.LocateMetric.max_absolute_difference(a,b)/100)+
                (np.quantile(np.abs(a-b),0.3))
                # (200*difference_rectangular.WeightMetric.highlow_inverse(a,b))
                , #TODO passing metric through?
        strategy_max_size=20
    ))
plt.show()
# result=difference_rectangular.Predict.scaled_local_minima(
#         array_a=phase_filter(image_a),
#         array_b=phase_filter(image_b),
#         offset_ab=modified_offset,
#     )
# difference_rectangular.plot_registration_result_grid(image_a,image_b,
#     registration_result_grid=result["search_results"])
# plt.show()
```

```{code-cell} ipython3
result
```

```{code-cell} ipython3
# def metric_phase_correlation_distance(
#         overlap_a:np.ndarray,
#         overlap_b:np.ndarray,
#     ):
#     shift_yx,error,phasediff=skimage.registration.phase_cross_correlation(
#         reference_image=overlap_a,
#         moving_image=overlap_b,
#         disambiguate=True)
#     return np.sqrt(np.sum(np.square(shift_yx)))

phase_correlation_results=difference_rectangular.StrategyFullSearch.prediction_grid(
    array_a=phase_filter(image_a),
    array_b=phase_filter(image_b),
    # metric=dr.metric_difference_squared_mean,
    metric=difference_rectangular.LocateMetricSkimage.modified_pearson,
    initial_offset=optimized_offset,
    strategy_predict=difference_rectangular.Predict.scaled_local_minima
    )
print("Manual Optimized:",optimized_offset,"Phase Correlation Optimized",phase_correlation_results["optimized_offset"])
# display(phase_correlation_results)
# pd.DataFrame({key:phase_correlation_results[key] for key in ['offsets_reduced','offsets_metric','offsets_metric_norm','offsets_phase_distance','offsets_phase_distance_norm','offsets_combined_norm']})
# print(pd.DataFrame({key:phase_correlation_results[key] for key in ['offsets_searched','offsets_found','reference_comparison','grid_results']}).to_markdown())
```

```{code-cell} ipython3
difference_rectangular.plot_registration_result_prediction(registration_results=phase_correlation_results)
```

# Full Search - Phase Cross Correlation Predictions on a Sparse Grid

```{code-cell} ipython3
# projects a-d
mis_filepath="../example/project_a/project_a-relations-calibrated.mis.json"
# mis_filepath="../example/project_b/project_b-relations-calibrated.mis.json"
# mis_filepath="../example/project_c/project_c-relations-calibrated.mis.json"
# mis_filepath="../example/project_d/project_d-relations-calibrated.mis.json"
mis_project=MISProjectJSON.load(mis_filepath)
mis_project.find_image_paths(mis_filepath,update=True)

# full_search_phase_filter=dr.filter_rgb_gray_mean
downsample=1
# full_search_phase_filter=lambda image:skimage.filters.scharr(dr.filter_rgb_gray_mean(image))
full_search_phase_filter=difference_rectangular.ModifierSkimage.scharr_edge(difference_rectangular.Filter.rgb_gray_mean)
reference_filter=difference_rectangular.Filter.rgb_gray_mean
```

```{code-cell} ipython3
# # project e 2 and 8
# # mis_filepath="../example/project_e/project_e-2-rel-cal.mis.json"
# mis_filepath="../example/project_e/project_e-8-rel-cal.mis.json"
# mis_project=MISProjectJSON.load(mis_filepath)
# mis_project.find_image_paths(mis_filepath,update=True)

# downsample=1
# full_search_phase_filter=\
#     dr.ModifierSkimage.median_disk(radius=2,filter=\
#     dr.Modifier.crop(bottom=1672,filter=\
#     dr.Filter.float
#     ),)
# reference_filter=dr.Modifier.crop(filter=dr.Filter.float,bottom=1672)
```

```{code-cell} ipython3
# # project f
# mis_filepath="../example/project_f/project_f-relations-calibrated.mis.json"
# mis_project=MISProjectJSON.load(mis_filepath)
# mis_project.find_image_paths(mis_filepath,update=True)

# downsample=10
# full_search_phase_filter=\
#         dr.ModifierSkimage.median_disk(radius=2,filter=\
#         dr.Modifier.crop(bottom=4096,right=4096,filter=\
#         dr.Filter.float,
#         ),)
# reference_filter=dr.Modifier.crop(filter=dr.Filter.float,bottom=4096,right=4096)
```

```{code-cell} ipython3
plt.close('all')
build_summary=list()
# for full_relation in mis_project.get_relations():
for full_relation in mis_project.get_relations()[0:5]:
# for full_relation in [mis_project.get_relations()[11]]:
    print(full_relation.get_reference())
    optimized_offset=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            relation=full_relation,
            strategy=difference_rectangular.StrategyLocal.full_grid,
            metric=difference_rectangular.LocateMetric.max_absolute_difference,
            strategy_max_size=10,
            filter=reference_filter
            )["optimized_offset"]
    start_time=timeit.default_timer()
    
    full_dga_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            relation=None,
            # relation=MISRelationRectangular(image_pair=full_relation.get_reference(),rectangular=optimized_relation), #optimized relation
            strategy=difference_rectangular.StrategyFullSearch.prediction_grid,
            # metric=dr.metric_difference_squared_mean,
            metric=lambda a,b:1-skimage.measure.pearson_corr_coeff(a,b)[0],
            filter=full_search_phase_filter,
            strategy_initial_grid_number=9,
            strategy_downsample=downsample
            )
    end_time=timeit.default_timer()
    print(f"Reference Optimized: {optimized_offset} Full Search DGA Optimized: {full_dga_results["optimized_offset"]} Time: {end_time-start_time:0.1f}s")


    search_offsets=np.array(full_dga_results["offsets_searched"])
    found_offsets=full_dga_results["offsets_predicted"]
    reduced_offsets=np.asarray(full_dga_results["offsets_reduced"])
    fig, (ax)=plt.subplots(1,1,)
    fig.set_figheight(3)
    fig.set_layout_engine('constrained')
    for i,offset in enumerate(found_offsets):
        ax.annotate("", xytext=search_offsets[i], xy=offset,
                arrowprops=dict(arrowstyle="->",alpha=0.5),)
    ax.yaxis.set_inverted(True)
    ax.scatter(search_offsets[:,0],search_offsets[:,1],marker='s',c='k',alpha=0.5,label="Search Offsets",zorder=0)
    combined_scatter=plt.scatter(reduced_offsets[:,0],reduced_offsets[:,1],c=full_dga_results["offsets_metric"],label="Search Results",zorder=1)
    plt.colorbar(combined_scatter)
    ax.scatter(*np.array(optimized_offset),marker='x', c='r',zorder=10,label="Reference Optimized")#(1/downsample)*()
    ax.scatter(*full_dga_results["optimized_offset"],marker='D', facecolors='none', edgecolors='r',zorder=11,label="Phase Optimized")
    fig.legend(loc="outside right")
    ax.set_aspect(1)
    plt.show()

    build_summary.append({
        "reference":full_relation.get_reference(),
        "total_checked":len(full_dga_results["offsets_searched"]),
        "total_time":round(end_time-start_time,1),
        "reference_offset":optimized_offset,
        "optimized_offset":full_dga_results["optimized_offset"],
        "optimized_metric":round(np.nanmin(full_dga_results["offsets_metric"]),3),
        })
print(pd.DataFrame(build_summary).to_markdown())
```

```{code-cell} ipython3
# print(pd.DataFrame(build_summary).to_markdown())
```

# Prototyping Local Minimization

```{code-cell} ipython3
selected_relation=mis_project.get_relations()[0]
selected_dga_results=difference_rectangular.pairwise_registration(
        image_a=mis_project.get_image(selected_relation.get_reference()[0]),
        image_b=mis_project.get_image(selected_relation.get_reference()[1]),
        relation=selected_relation,
        strategy=difference_rectangular.StrategyLocal.local_minima_grid,
        # metric=dr.metric_difference_squared_mean,
        metric=difference_rectangular.LocateMetric.max_absolute_difference,
        strategy_grid_scale=1,
        strategy_max_size=10,
        # strategy_footprint_shape=(7,7),
        strategy_footprint=skimage.morphology.disk(radius=2),
        filter=difference_rectangular.Filter.rgb_gray_mean
        )
print("Initial:",selected_dga_results["initial_offset"],"Optimized:",selected_dga_results["optimized_offset"])
# selected_dga_results
```

```{code-cell} ipython3
difference_rectangular.plot_registration_result_grid(
        image_a=mis_project.get_image(selected_relation.get_reference()[0]),
        image_b=mis_project.get_image(selected_relation.get_reference()[1]),
        registration_result_grid=selected_dga_results,
    )
plt.show()
```

```{code-cell} ipython3
relation_index_results=dict()
for i,relation in enumerate(mis_project.get_relations()):
    registration_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(relation.get_reference()[0]),
            image_b=mis_project.get_image(relation.get_reference()[1]),
            relation=relation,
            strategy=difference_rectangular.StrategyLocal.local_minima_grid,
            metric=difference_rectangular.LocateMetric.mean_absolute_difference,
            strategy_max_size=10,
            strategy_footprint=np.ones((7,7)),
            filter=difference_rectangular.Filter.rgb_gray_mean
            )
    print(i,":",relation.get_reference(),relation.get_relation('r'),"->",registration_results["optimized_offset"])
    difference_rectangular.plot_registration_result_grid(
        image_a=mis_project.get_image(relation.get_reference()[0]),
        image_b=mis_project.get_image(relation.get_reference()[1]),
        registration_result_grid=registration_results,
    )
    plt.show()
```

# Combining phase correlation with local minimization

```{code-cell} ipython3
plt.close('all')
build_summary=list()
for full_relation in mis_project.get_relations():
# for full_relation in mis_project.get_relations()[0:5]:
# for full_relation in [mis_project.get_relations()[10]]:
    print(full_relation.get_reference())
    optimized_offset=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            relation=full_relation,
            strategy=difference_rectangular.StrategyLocal.full_grid,
            metric=difference_rectangular.LocateMetric.mean_squared_difference,
            strategy_max_size=10,
            filter=reference_filter
            )["optimized_offset"]
    start_time=timeit.default_timer()
    
    prediction_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            relation=None,
            # relation=MISRelationRectangular(image_pair=full_relation.get_reference(),rectangular=optimized_relation), #optimized relation
            strategy=difference_rectangular.StrategyFullSearch.prediction_grid,
            # metric=dr.metric_difference_squared_mean,
            metric=lambda a,b:1-skimage.measure.pearson_corr_coeff(a,b)[0],
            filter=full_search_phase_filter,
            strategy_initial_grid_number=9,
            strategy_downsample=downsample,
            strategy_edge_avoid=50,
            )
    registration_results=difference_rectangular.pairwise_registration(
            image_a=mis_project.get_image(full_relation.get_reference()[0]),
            image_b=mis_project.get_image(full_relation.get_reference()[1]),
            relation=prediction_results["optimized_offset"],
            strategy=difference_rectangular.StrategyLocal.local_minima_grid,
            metric=difference_rectangular.LocateMetric.mean_squared_difference,
            strategy_max_size=50,
            strategy_footprint=skimage.morphology.disk(radius=7),
            filter=reference_filter
            )
    end_time=timeit.default_timer()
    print(f"Reference Opt.: {optimized_offset} Full Search Opt.: {prediction_results["optimized_offset"]} Local Opt.: {registration_results["optimized_offset"]} : {end_time-start_time:0.1f}s")


    difference_rectangular.plot_registration_result_prediction(
        # image_a=mis_project.get_image(full_relation.get_reference()[0]),
        # image_b=mis_project.get_image(full_relation.get_reference()[1]),
        registration_results=prediction_results,
        reference_optimized=optimized_offset
    )

    difference_rectangular.plot_registration_result_grid(
        image_a=mis_project.get_image(full_relation.get_reference()[0]),
        image_b=mis_project.get_image(full_relation.get_reference()[1]),
        registration_result_grid=registration_results,
    )
    plt.show()

    build_summary.append({
        "reference":full_relation.get_reference(),
        "total_checked":len(prediction_results["offsets_searched"]),
        "total_time":round(end_time-start_time,1),
        "reference_offset":optimized_offset,
        "full_search_optimized_offset":prediction_results["optimized_offset"],
        "local_optimized_offset":registration_results["optimized_offset"],
        "full_search_optimized_metric":round(np.nanmin(prediction_results["offsets_metric"]),3),
        "local_optimized_metric":round(np.nanmin(registration_results["grid_results"]),3),
        })
print(pd.DataFrame(build_summary).to_markdown())
```

```{code-cell} ipython3

# class Predict():
#     """
#     Group of functions which take two arrays and an offset and predicts an aligned offset.
#     """
    # @staticmethod
    # def scaled_local_minima(
    #         array_a:np.ndarray,
    #         array_b:np.ndarray,
    #         offset_ab:tuple[int,int]|np.ndarray,
    #         ):
    #     search_results=StrategyLocal.local_minima_grid(
    #         array_a=array_a,
    #         array_b=array_b,
    #         metric=lambda a,b:
    #             LocateMetric.norm_root_mean_squared_difference(a,b)+
    #             # (LocateMetric.max_absolute_difference(a,b)/100)+
    #             (np.quantile(np.abs(a-b),0.75))+
    #             (200*WeightMetric.highlow_inverse(a,b)), #TODO passing metric through?
    #         initial_offset=tuple(offset_ab),
    #         strategy_grid_scale=1,
    #         strategy_max_size=50,
    #         strategy_max_steps=50,
    #         strategy_footprint_shape=(11,11)
    #     )

    #     return {
    #         "offset":search_results["optimized_offset"],
    #         "shift":(offset_ab[1]-search_results["optimized_offset"][1],offset_ab[0]-search_results["optimized_offset"][0]),
    #         "search_results":search_results
    #         }
```
