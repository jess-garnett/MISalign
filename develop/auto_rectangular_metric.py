from typing import Optional, Callable
import numpy as np
from matplotlib import pyplot as plt

from misalign.model.project import MISProjectJSON
from misalign.model.image import MISImage, array_like
from misalign.model.relation import MISRelation
from misalign.alignment import auto_rectangular_skimage
from misalign.canvas import canvas_rectangular as cr

import pandas as pd
import skimage

import timeit
# import logging
# from sys import stdout
# logging.basicConfig(stream=stdout, level=logging.INFO)

#TODO Move pair solve/render into canvas module.

def _plot_grid_result(
        registration_result_grid:dict,
        overlays=True):
    plt.imshow(registration_result_grid["grid_results"],
        extent=(np.min(registration_result_grid["grid"][0])-0.5,
                np.max(registration_result_grid["grid"][0])+0.5,
                np.max(registration_result_grid["grid"][1])+0.5,
                np.min(registration_result_grid["grid"][1])-0.5,), #xmin,xmax,ymin,ymax
        )
    plt.xlabel("Rectangular X-offset")
    plt.ylabel("Rectangular Y-offset")
    plt.colorbar(label="Metric Results")

    if overlays:
        legend=False
        if "initial_offset" in registration_result_grid:
            plt.scatter(
                x=registration_result_grid["initial_offset"][0],
                y=registration_result_grid["initial_offset"][1],
                marker=".",
                color="r",
                label=f'Initial: {registration_result_grid["initial_offset"]}')
            legend=True
        if "optimized_offset" in registration_result_grid:
            plt.scatter(
                x=registration_result_grid["optimized_offset"][0],
                y=registration_result_grid["optimized_offset"][1],
                marker="o",
                color="r",
                label=f'Optimized: {registration_result_grid["optimized_offset"]}')
            legend=True
        if "initial_offset" in registration_result_grid and "optimized_offset" in registration_result_grid:
            plt.annotate("", 
                xytext=registration_result_grid["initial_offset"],
                xy=registration_result_grid["optimized_offset"],
                arrowprops=dict(arrowstyle="->",color="w"),)
        if legend:
            plt.legend()

def _render_rectangular_pair(
        image_a:MISImage,
        image_b:MISImage,
        offset:tuple[int,int],
        weight=cr.weight_flat,
        return_canvas_relative_offsets=False
        ):
    origin_relative_offsets=cr.rectangular_solve(
        relations=[{"ref":(image_a.name,image_b.name),"rel":offset}],
        image_names=[image_a.name,image_b.name],
        origin=image_a.name
        )

    origin_relative_extents=cr.find_relative_extents(
        image_names=[image_a.name,image_b.name],
        origin_relative_offsets=origin_relative_offsets,
        image_shapes={image_a.name:image_a.shape,image_b.name:image_b.shape}
        )

    canvas_extents, canvas_offsets=cr.resolve_extents(origin_relative_extents)

    canvas_relative_offsets=cr.place_in_canvas(
        image_names=[image_a.name,image_b.name],
        origin_relative_offsets=origin_relative_offsets,
        canvas_extents=canvas_extents,
        canvas_offsets=canvas_offsets)

    normalizer=cr.build_normalization(
        image_arrays={image_a.name:image_a,image_b.name:image_b},
        canvas_relative_offsets=canvas_relative_offsets,
        canvas_extents=canvas_extents,
        weight=weight,
        )
    render=cr.render_blended(
        image_arrays={image_a.name:image_a,image_b.name:image_b},
        canvas_relative_offsets=canvas_relative_offsets,
        canvas_extents=canvas_extents,
        weight=weight,
        normalizer=normalizer,
        )

    if return_canvas_relative_offsets:
        return render, canvas_relative_offsets
    else:
        return render

def plot_rectangular_pair(
        image_a:MISImage,
        image_b:MISImage,
        offset:tuple[int,int],
        weight=cr.weight_flat,
        focus_overlap=False,
        focus_expand=50
        ):
    render, canvas_relative_offsets=_render_rectangular_pair(
        image_a=image_a,
        image_b=image_b,
        offset=offset,
        weight=weight,
        return_canvas_relative_offsets=True)
    plt.imshow(render)
    if focus_overlap:
        a_spans,b_spans=auto_rectangular_skimage.overlap_spans(
            offset_vector=offset,
            a_shape=image_a.shape,
            b_shape=image_b.shape)
        plt.xlim(
            left=canvas_relative_offsets[image_a.name][0]+a_spans[0][0]-focus_expand,
            right=canvas_relative_offsets[image_a.name][0]+a_spans[0][1]+focus_expand)
        plt.ylim(
            top=canvas_relative_offsets[image_a.name][1]+a_spans[1][0]-focus_expand,
            bottom=canvas_relative_offsets[image_a.name][1]+a_spans[1][1]+focus_expand)

def plot_registration_result_grid(
        image_a:MISImage,
        image_b:MISImage,
        registration_result_grid:dict,
        figwidth=12,
        figheight=4,
        overlays=True
        ):
    if "initial_offset" in registration_result_grid:
        fig,axs=plt.subplot_mosaic(
            mosaic=[
                ["metric_map","initial"],
                ["metric_map","optimized"]])
    else:
        fig,axs=plt.subplot_mosaic(
            mosaic=[
                ["metric_map","optimized"]])
    fig.set_figwidth(figwidth)
    fig.set_figheight(figheight)
    plt.tight_layout(pad=1.5,h_pad=2,w_pad=2)

    plt.sca(axs["metric_map"])
    plt.title("Registration Grid Result")
    _plot_grid_result(
        registration_result_grid=registration_result_grid,
        overlays=overlays)

    if "initial_offset" in registration_result_grid:
        plt.sca(axs["initial"])
        plt.title("Initial Flat Blend")
        plot_rectangular_pair(
            image_a=image_a,
            image_b=image_b,
            offset=registration_result_grid["initial_offset"],
            weight=cr.weight_dfe,
            focus_overlap=True)

    plt.sca(axs["optimized"])
    plt.title("Optimized Flat Blend")
    plot_rectangular_pair(
        image_a=image_a,
        image_b=image_b,
        offset=registration_result_grid["optimized_offset"],
        weight=cr.weight_dfe,
        focus_overlap=True)

def plot_registration_result_prediction(
        # image_a:MISImage,
        # image_b:MISImage,
        registration_results:dict,
        figwidth=12,
        figheight=4,
        reference_optimized:Optional[tuple[int,int]]=None
    ):
    search_offsets=np.array(registration_results["offsets_searched"])
    found_offsets=registration_results["offsets_predicted"]
    reduced_offsets=np.asarray(registration_results["offsets_reduced"])
    fig, (ax)=plt.subplots(1,1,)
    fig.set_figwidth(figwidth)
    fig.set_figheight(figheight)
    fig.set_layout_engine('constrained')
    for i,offset in enumerate(found_offsets):
        ax.annotate("", xytext=search_offsets[i], xy=offset,
                arrowprops=dict(arrowstyle="->",alpha=0.5),)
    ax.yaxis.set_inverted(True)
    ax.scatter(search_offsets[:,0],search_offsets[:,1],marker='s',c='k',alpha=0.5,label="Search Offsets",zorder=0)
    combined_scatter=plt.scatter(reduced_offsets[:,0],reduced_offsets[:,1],c=registration_results["offsets_metric"],label="Search Results",zorder=1)
    plt.colorbar(combined_scatter)
    if reference_optimized is not None:
        ax.scatter(*np.array(reference_optimized),marker='x', c='r',zorder=10,label="Reference Optimized")#(1/downsample)*()
    ax.scatter(*registration_results["optimized_offset"],marker='D', facecolors='none', edgecolors='r',zorder=11,label="Prediction Optimized")
    fig.legend(loc="outside right")
    ax.set_aspect(1)
    plt.show()

def calibrate_metrics_initial(
        image_a:MISImage|array_like,
        image_b:MISImage|array_like,
        relation_offset:MISRelation|tuple[int,int]|None,
        metrics:dict[str,Callable[[np.ndarray,np.ndarray],float]],
        filter:Callable[[array_like],np.ndarray],
        strategies:dict[str,Callable]={
                "grid":auto_rectangular_skimage.StrategyLocal.full_grid,
                "sparse":auto_rectangular_skimage.StrategyFullSearch.interpolated_adaptive_grid,
            },
        strategy_kwargs:dict[str,dict]={
                "grid":dict(strategy_max_size=20),
                "sparse":dict(strategy_full_search_progression=[dict(initial_grid_number=40)]),
            },
        **kwargs
    ):

    ## Get image arrays
    array_a:np.ndarray=filter(image_a)
    array_b:np.ndarray=filter(image_b)

    ## Get initial relation
    if isinstance(relation_offset,MISRelation):
        try:
            initial_rectangular_offset=relation_offset.get_relation('r')
        except ValueError:
            initial_rectangular_offset=None
    elif isinstance(relation_offset,tuple):
        initial_rectangular_offset=relation_offset
    else:
        initial_rectangular_offset=None
    
    calibration_results_initial=dict()

    for metric_name,metric in metrics.items():
        calibration_results_initial[metric_name]=dict()
        for strategy_name,strategy in strategies.items():
            calibration_results_initial[metric_name][strategy_name]=strategy(
                array_a,array_b,
                initial_offset=initial_rectangular_offset,
                metric=metric,
                **strategy_kwargs[strategy_name],
                )

    return calibration_results_initial


def setup_project(mis_filepath:str)->MISProjectJSON:
    mis_project: MISProjectJSON=MISProjectJSON.load(mis_filepath)
    mis_project.find_image_paths(mis_filepath,update=True)
    return mis_project



class MetricsTest():
    def __init__(self,
            mis_project,
            filter:Callable=auto_rectangular_skimage.Filter.float,
            metrics:Optional[dict]=None):
        self.project=mis_project
        self.filter=filter
        if metrics is not None:
            self.metrics=metrics
        else:
            self.metrics={}
        self.calibration_results={}
    def calibrate_metrics(self,relation_index=None,local_only=False):
        if relation_index is not None:
            self.calibration_results={}
            self.relation_index=relation_index

        not_calibrated={metric_name:metric_function
            for metric_name,metric_function in self.metrics.items()
            if metric_name not in self.calibration_results.keys()}
        self.relation=self.project.get_relations()[self.relation_index]
        self.image_a=self.project.get_image(self.relation.get_reference()[0])
        self.image_b=self.project.get_image(self.relation.get_reference()[1])

        if local_only:
            calibrate_kwargs=dict(
                strategies={
                    "local":auto_rectangular_skimage.StrategyLocal.full_grid,
                },
                strategy_kwargs={
                    "local":dict(strategy_max_size=10),
                },
            )
        else:
            calibrate_kwargs=dict(
                strategies={
                    "local":auto_rectangular_skimage.StrategyLocal.full_grid,
                    "full":auto_rectangular_skimage.StrategyFullSearch.interpolated_adaptive_grid,
                },
                strategy_kwargs={
                    "local":dict(strategy_max_size=10),
                    "full":dict(strategy_full_search_progression=[dict(initial_grid_number=40)]),
                },
            )

        self.calibration_results.update(
            calibrate_metrics_initial(
                image_a=self.image_a,
                image_b=self.image_b,
                relation_offset=self.relation,
                metrics=not_calibrated,
                filter=self.filter,
                **calibrate_kwargs)  # ty:ignore[invalid-argument-type]
            )
    def update_metrics(self,metrics):
        for metric_name,metric_function in metrics.items():
            self.calibration_results.pop(metric_name,None)
            self.metrics[metric_name]=metric_function
    def plot_metrics(self):
        for metric_name,strategies in self.calibration_results.items():
            fig, axs=plt.subplots(1,len(strategies)+1)
            axs:dict[str,plt.Axes]={strategy_name:ax for strategy_name,ax in zip(list(strategies.keys())+["histogram"],axs)}

            # fig.tight_layout()
            fig.set_figheight(2)
            fig.set_figwidth(4*(len(strategies)+1))
            fig.suptitle(metric_name)
            for strategy_name,strategy_result in strategies.items():
                if "interp_results" in strategy_result.keys():
                    result_key="interp_results"
                else:
                    result_key="grid_results"
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
                axs[strategy_name].scatter(*self.relation.get_relation('r'))
                plt.colorbar(im)
                # Generate histogram for each strategy
                hist=axs["histogram"].hist(strategy_result[result_key].flatten(),bins=20,histtype="step",label=strategy_name)
                hist[2][0].xy[:,1]=hist[2][0].xy[:,1]/sum(hist[2][0].xy[:,1])  # ty:ignore[not-subscriptable, unresolved-attribute]
            # Add legend to histogram
            axs["histogram"].legend()
            axs["histogram"].set_ylim(bottom=0,top=0.4)
            axs["histogram"].set_yticks(ticks=axs["histogram"].get_yticks(),labels=[f'{x:0.0%}' for x in axs["histogram"].get_yticks()])
            plt.show()

    def summary_metrics(self):
        build_summary=dict()
        for metric_name,strategies in self.calibration_results.items():
            build_summary[metric_name]=dict()
            for strategy_name,strategy_result in strategies.items():
                if "interp_results" in strategy_result.keys():
                    result_key="interp_results"
                else:
                    result_key="grid_results"

                build_summary[metric_name][f"{strategy_name} ptp"]=np.ptp(strategy_result[result_key])
                build_summary[metric_name][f"{strategy_name} min"]=np.min(strategy_result[result_key])
                build_summary[metric_name][f"{strategy_name} max"]=np.max(strategy_result[result_key])
        print(pd.DataFrame.from_dict(build_summary,orient='index').to_markdown())
        return build_summary

    def pairwise(self,
        metric_name=None,
        metric=None,
        plot=True,
        selected_indeces=None,
        filter=None,
        local_kwargs=dict(),
        full_kwargs=dict(),
        ):
        if metric is None:
            metric=self.metrics[metric_name]
        if selected_indeces is None:
            relations=self.project.get_relations()
        else:
            relations=[self.project.get_relations()[i] for i in selected_indeces]
        if filter is None:
            filter=self.filter
        
        build_summary=list()
        for relation in relations:
            print(relation.get_reference())
            optimized_offset=auto_rectangular_skimage.pairwise_registration(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    relation=relation,
                    strategy=auto_rectangular_skimage.StrategyLocal.full_grid,
                    metric=auto_rectangular_skimage.LocateMetric.mean_squared_difference,
                    strategy_max_size=10,
                    filter=filter
                    )["optimized_offset"]

            local_start_time=timeit.default_timer()
            local_results=auto_rectangular_skimage.pairwise_registration(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    relation=relation,
                    strategy=auto_rectangular_skimage.StrategyLocal.full_grid,
                    metric=metric,
                    filter=filter,
                    **local_kwargs
                    )
            local_end_time=timeit.default_timer()

            print(f"Initial: {local_results["initial_offset"]} True Soln.: {optimized_offset} Local Soln.: {local_results["optimized_offset"]} Time: {local_end_time-local_start_time:0.1f}s")
            if plot:
                plot_registration_result_grid(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    registration_result_grid=local_results,
                )
                plt.show()

            full_start_time=timeit.default_timer()
            full_results=auto_rectangular_skimage.pairwise_registration(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    relation=relation,
                    strategy=auto_rectangular_skimage.StrategyFullSearch.interpolated_adaptive_grid,
                    metric=metric,
                    filter=filter,
                    **full_kwargs
                    )
            full_end_time=timeit.default_timer()

            print(f"True Soln.: {optimized_offset} Full Soln.: {full_results["optimized_offset"]} Time: {full_end_time-full_start_time:0.1f}s")
            if plot:
                fig, (ax1,ax2)=plt.subplots(1,2,sharex=True,sharey=True)
                fig.set_figwidth(12)
                ax1.imshow(full_results["grid_results"],
                        extent=(np.min(full_results["grid"][0])-0.5,
                                np.max(full_results["grid"][0])+0.5,
                                np.max(full_results["grid"][1])+0.5,
                                np.min(full_results["grid"][1])-0.5,), #xmin,xmax,ymin,ymax)
                        vmax=np.quantile(full_results["interp_results"],0.5)
                        )

                ax1.scatter(*optimized_offset,marker="x",c='r',label="Reference Optimized")
                ax1.scatter(*full_results["optimized_offset"],marker="D",facecolors='none',edgecolors='r',label="Interpolation Optimized")

                ax2.imshow(full_results["interp_results"],
                        extent=(np.min(full_results["grid"][0])-0.5,
                                np.max(full_results["grid"][0])+0.5,
                                np.max(full_results["grid"][1])+0.5,
                                np.min(full_results["grid"][1])-0.5,), #xmin,xmax,ymin,ymax)
                        vmax=np.quantile(full_results["interp_results"],0.5)
                        )

                ax2.scatter(*optimized_offset,marker="x",c='r',label="Reference Optimized")
                ax2.scatter(*full_results["optimized_offset"],marker="D",facecolors='none',edgecolors='r',label="Interpolation Optimized")
                plt.show()


            build_summary.append({
                "reference":relation.get_reference(),
                "reference_offset":optimized_offset,
                "local_total_checked":np.sum(~np.isnan(local_results["grid_results"])),
                "local_total_time":round(local_end_time-local_start_time,1),
                "local_optimized_offset":local_results["optimized_offset"],
                "local_optimized_metric":round(np.nanmin(local_results["grid_results"]),2),
                "full_total_checked":np.sum(~np.isnan(full_results["grid_results"])),
                "full_total_time":round(full_end_time-full_start_time,1),
                "full_reference_offset":optimized_offset,
                "full_optimized_offset":full_results["optimized_offset"],
                "full_optimized_metric":round(np.nanmin(full_results["grid_results"]),2),
                })
        return build_summary
