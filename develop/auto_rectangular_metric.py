from typing import Optional, Callable
import numpy as np
from matplotlib import pyplot as plt

from misalign.model.project import MISProjectJSON
from misalign.alignment import difference_rectangular

import pandas as pd
import skimage

import timeit
# import logging
# from sys import stdout
# logging.basicConfig(stream=stdout, level=logging.INFO)


def setup_project(mis_filepath:str)->MISProjectJSON:
    mis_project: MISProjectJSON=MISProjectJSON.load(mis_filepath)
    mis_project.find_image_paths(mis_filepath,update=True)
    return mis_project



class MetricsTest():
    def __init__(self,
            mis_project,
            filter:Callable=difference_rectangular.Filter.float,
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
                    "local":difference_rectangular.StrategyLocal.full_grid,
                },
                strategy_kwargs={
                    "local":dict(strategy_max_size=10),
                },
            )
        else:
            calibrate_kwargs=dict(
                strategies={
                    "local":difference_rectangular.StrategyLocal.full_grid,
                    "full":difference_rectangular.StrategyFullSearch.interpolated_adaptive_grid,
                },
                strategy_kwargs={
                    "local":dict(strategy_max_size=10),
                    "full":dict(strategy_full_search_progression=[dict(initial_grid_number=40)]),
                },
            )

        self.calibration_results.update(
            difference_rectangular.calibrate_metrics_initial(
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
            optimized_offset=difference_rectangular.pairwise_registration(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    relation=relation,
                    strategy=difference_rectangular.StrategyLocal.full_grid,
                    metric=difference_rectangular.LocateMetric.mean_squared_difference,
                    strategy_max_size=10,
                    filter=filter
                    )["optimized_offset"]

            local_start_time=timeit.default_timer()
            local_results=difference_rectangular.pairwise_registration(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    relation=relation,
                    strategy=difference_rectangular.StrategyLocal.full_grid,
                    metric=metric,
                    filter=filter,
                    **local_kwargs
                    )
            local_end_time=timeit.default_timer()

            print(f"Initial: {local_results["initial_offset"]} True Soln.: {optimized_offset} Local Soln.: {local_results["optimized_offset"]} Time: {local_end_time-local_start_time:0.1f}s")
            if plot:
                difference_rectangular.plot_registration_result_grid(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    registration_result_grid=local_results,
                )
                plt.show()

            full_start_time=timeit.default_timer()
            full_results=difference_rectangular.pairwise_registration(
                    image_a=self.project.get_image(relation.get_reference()[0]),
                    image_b=self.project.get_image(relation.get_reference()[1]),
                    relation=relation,
                    strategy=difference_rectangular.StrategyFullSearch.interpolated_adaptive_grid,
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
