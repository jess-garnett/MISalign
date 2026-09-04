"""
Tests for `misalign\alignment\auto_rectangular_skimage.py`
"""
from math import dist
import numpy as np
import pytest

# from misalign.model.project import MISProjectJSON
from misalign.model.image import MISImageFile
from misalign.model.relation import MISRelationRectangular

from misalign.alignment import auto_rectangular_skimage


class TestOverlap():
    def test_axis_span_matching_shape_positive_offset(self):
        """
        Tests `axis_span` with matching shapes and positive offset.

        Based on x-axis of `('image_a01.jpg', 'image_a02.jpg')` in `example/project_a/project_a-relations-calibrated.mis.json`.
        """
        a_span,b_span=auto_rectangular_skimage.axis_span(
            offset_vector=12,
            a_shape=1600,
            b_shape=1600)
        assert a_span==(0,1600-12) and b_span==(12,1600)
    def test_axis_span_matching_shape_negative_offset(self):
        """
        Tests `axis_span` with matching shapes and negative offset.

        Based on y-axis of `('image_a01.jpg', 'image_a02.jpg')` in `example/project_a/project_a-relations-calibrated.mis.json`.
        """
        a_span,b_span=auto_rectangular_skimage.axis_span(
            offset_vector=-1088,
            a_shape=1200,
            b_shape=1200)
        assert a_span==(1088,1200) and b_span==(0,1200-1088)
    def test_axis_span_matching_shape_zero_offset(self):
        """
        Tests `axis_span` with matching shapes and zero offset.
        """
        a_span,b_span=auto_rectangular_skimage.axis_span(
            offset_vector=0,
            a_shape=1200,
            b_shape=1200)
        assert a_span==(0,1200) and b_span==(0,1200)
    #TODO Test/handle non-matching shapes in axis_span
    def test_overlap_spans_simple(self):
        """
        Tests `overlap_spans` with one negative and one positive offset and matching shapes.

        Based on `('image_a01.jpg', 'image_a02.jpg')` in `example/project_a/project_a-relations-calibrated.mis.json`.
        """
        (ax_span,ay_span),(bx_span,by_span)=auto_rectangular_skimage.overlap_spans(
                offset_vector=(12,-1088),
                a_shape=(1200,1600),
                b_shape=(1200,1600)
            )
        assert ax_span==(0,1600-12) and bx_span==(12,1600) and ay_span==(1088,1200) and by_span==(0,1200-1088)
    def test_overlap_spans_no_overlap(self):
        """
        Tests `overlap_spans` with offset vectors that do not overlap.
        """
        with pytest.raises(expected_exception=ValueError):
            auto_rectangular_skimage.overlap_spans(
                    offset_vector=(1600,0),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            auto_rectangular_skimage.overlap_spans(
                    offset_vector=(-1600,0),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            auto_rectangular_skimage.overlap_spans(
                    offset_vector=(0,1200),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            auto_rectangular_skimage.overlap_spans(
                    offset_vector=(0,-1200),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
    #TODO diversify offsets/shapes tested.
    


    def test_overlap_evaluate_simple(self):
        """
        Tests `overlap_compare` with a simplified metric and arrays.
        """
        def metric_sum(overlap_a,overlap_b):
            return np.sum((overlap_a,overlap_b))
        overlap_metric=auto_rectangular_skimage.overlap_evaluate(
            array_a=np.full(shape=(100,100),fill_value=100,dtype=np.float32),
            array_b=np.full(shape=(100,100),fill_value=200,dtype=np.float32),
            offset_ab=(50,50),
            metric=metric_sum
        )
        assert overlap_metric==(100*50*50)+(200*50*50)



    def test_overlap_process_difference_simple(self):
        """
        Tests `overlap_process` to get the difference of simplified arrays.
        """
        def metric_sum(overlap_a,overlap_b):
            return np.sum((overlap_a,overlap_b))
        difference=auto_rectangular_skimage.overlap_process(
            array_a=np.full(shape=(100,100),fill_value=100,dtype=np.float32),
            array_b=np.full(shape=(100,100),fill_value=200,dtype=np.float32),
            offset_ab=(50,50),
        )
        assert np.all(difference==-100)


@pytest.fixture
def simple_parabolic_arrays_1():
        planned_offset=(-3,-5)
        # Quadratic curve centered at 50,50
        array_a=np.fromfunction(
            function=lambda row,col:(row-50)**2+(col-50)**2,
            shape=(100,100))
        array_a[array_a>255]==255
        array_a=array_a.astype(np.float32)

        # Quadratic curve centered at 50,50 and then offset.
        array_b=np.fromfunction(
            function=lambda row,col:(row-50-planned_offset[1])**2+(col-50-planned_offset[0])**2,
            shape=(100,100))
        array_b[array_b>255]==255
        array_b=array_b.astype(np.float32)
        
        return array_a,array_b,planned_offset

class TestMetric():
    @pytest.mark.parametrize(argnames="dtype",argvalues=[np.float32,np.float64,np.int16,pytest.param(np.uint8, marks=pytest.mark.xfail)])
    def test_metric_dtypes(self,benchmark,dtype):
        """
        Tests `LocateMetric.mean_squared_difference` with  simplified arrays.
        """
        
        overlap_a=np.full(shape=(50,50),fill_value=100,dtype=dtype)
        overlap_b=np.full(shape=(50,50),fill_value=200,dtype=dtype)
        overlap_metric=benchmark(auto_rectangular_skimage.LocateMetric.mean_squared_difference,
            overlap_a=overlap_a,
            overlap_b=overlap_b
            )
        assert overlap_metric==100**2

    @pytest.mark.parametrize(argnames="metric",argvalues=[
        pytest.param(auto_rectangular_skimage.LocateMetric.mean_squared_difference,id="mean_squared_difference"),
        pytest.param(auto_rectangular_skimage.LocateMetric.mean_absolute_difference,id="mean_absolute_difference"),
        pytest.param(auto_rectangular_skimage.LocateMetric.max_absolute_difference,id="max_absolute_difference"),
        pytest.param(auto_rectangular_skimage.LocateMetric.root_mean_squared_difference,id="root_mean_squared_difference"),
        pytest.param(auto_rectangular_skimage.LocateMetric.norm_mean_squared_difference,id="norm_mean_squared_difference"),
        pytest.param(auto_rectangular_skimage.LocateMetric.deviation_difference_over_source,id="deviation_difference_over_source"),
        pytest.param(auto_rectangular_skimage.LocateMetricSkimage.modified_pearson,id="modified_pearson"),
        pytest.param(auto_rectangular_skimage.LocateMetricSkimage.modified_mutual_information,id="modified_mutual_information"),
        ])
    def test_metric_locate_simple_1(self,benchmark,simple_parabolic_arrays_1,metric):
        """
        Tests metric that have a minima at the true match with simplified parabolic array.
        """
        array_a,array_b,planned_offset=simple_parabolic_arrays_1

        overlap_metric=benchmark(auto_rectangular_skimage.overlap_evaluate,
            array_a=array_a,
            array_b=array_b,
            offset_ab=planned_offset,
            metric=metric
            )
        assert overlap_metric<1e-3
    
    @pytest.mark.parametrize(argnames="metric,expected_value",argvalues=[
        pytest.param(auto_rectangular_skimage.WeightMetric.highlow_inverse,0.00020824657,id="highlow_inverse"),
        pytest.param(auto_rectangular_skimage.WeightMetric.linear_edge_penalty,0.1366666666666667,id="metric_linear_edge_penalty"),
        ])
    def test_metric_weight_simple_1(self,benchmark,simple_parabolic_arrays_1,metric,expected_value):
        """
        Tests metric which are not expected to consistently have a minima at the true solution.
        """
        array_a,array_b,planned_offset=simple_parabolic_arrays_1

        overlap_metric=benchmark(auto_rectangular_skimage.overlap_evaluate,
            array_a=array_a,
            array_b=array_b,
            offset_ab=planned_offset,
            metric=metric
            )
        assert overlap_metric==expected_value
    #TODO make two parametrized test sets. One for metrics which should find correct location. One for metrics that shouldn't(i.e. feature weighting).


class TestStrategy():
    @pytest.mark.parametrize(argnames="initial_offset,strategy_grid_scale,strategy_max_size",argvalues=[
        ((-5,-5),1,5), # 2 pixels away, non-scaled grid.
        ((-7,-1),1,5), # (4,4) pixels away, scaled grid aligned with true solution.
        ((1,4),1,10), # (4,9) pixels away, non-scaled large grid.
    ])
    def test_strategy_scaled_grid_simple_1(self,benchmark,simple_parabolic_arrays_1,initial_offset,strategy_grid_scale,strategy_max_size):
        """
        Tests `strategy_scaled_grid` with  simplified arrays and offsets.
        """
        array_a,array_b,planned_offset=simple_parabolic_arrays_1
        assert array_a[50,50]==0 and array_b[45,47]==0
        
        results=benchmark(auto_rectangular_skimage.StrategyLocal.scaled_grid,
            array_a=array_a,
            array_b=array_b,
            initial_offset=initial_offset,
            strategy_grid_scale=strategy_grid_scale,
            strategy_max_size=strategy_max_size
        )

        assert results["optimized_offset"]==planned_offset
        
        #TODO test more of the items in results.
        #TODO test with noise or other factors.
        

    def test_strategy_full_grid_simple(self):
        """
        Tests `strategy_full_grid` with  simplified arrays and offsets.
        """
        planned_offset=(5,45)
        # Quadratic curve centered at 50,50
        array_a=np.fromfunction(
            function=lambda row,col:(row-50)**2+(col-50)**2,
            shape=(100,100))
        array_a[array_a>255]==255
        array_a=array_a.astype(np.int32)

        # Quadratic curve centered at 50,50 and then offset.
        array_b=np.fromfunction(
            function=lambda row,col:(row-50-planned_offset[1])**2+(col-50-planned_offset[0])**2,
            shape=(100,100))
        array_b[array_b>255]==255
        array_b=array_b.astype(np.float32)

        
        assert array_a[50,50]==0 and array_b[95,55]==0
        
        results=auto_rectangular_skimage.StrategyLocal.full_grid(
            array_a=array_a,
            array_b=array_b,
            initial_offset=(2,48),
        )

        assert results["optimized_offset"]==planned_offset

        #TODO test more of the items in results.
        #TODO test with noise or other factors.
        
class TestRegistration():
    # (12,-1088) is (3,1) from true solution
    @pytest.mark.parametrize(argnames="kwargs",argvalues=[
        pytest.param(dict(
            strategy=auto_rectangular_skimage.StrategyLocal.full_grid,
            strategy_max_size=5,
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            metric=auto_rectangular_skimage.LocateMetric.mean_squared_difference),id="full_grid - small"),
        pytest.param(dict(
            strategy=auto_rectangular_skimage.StrategyLocal.full_grid,
            strategy_max_size=10,
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            metric=auto_rectangular_skimage.LocateMetric.mean_squared_difference),id="full_grid - small-medium"),
        pytest.param(dict(
            strategy=auto_rectangular_skimage.StrategyLocal.full_grid,
            strategy_max_size=20,
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            metric=auto_rectangular_skimage.LocateMetric.mean_squared_difference),id="full_grid - medium"),
        pytest.param(dict(
            strategy=auto_rectangular_skimage.StrategyLocal.scaled_grid,
            strategy_grid_scale=2,
            strategy_max_size=5,
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            metric=auto_rectangular_skimage.LocateMetric.mean_squared_difference),id="scaled_grid - x2 - small-medium"),
        pytest.param(dict(
            strategy=auto_rectangular_skimage.StrategyLocal.local_minima_grid,
            strategy_max_size=5,
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            metric=auto_rectangular_skimage.LocateMetric.mean_squared_difference),id="local_minima_grid - small"),
    ])
    def test_pairwise_full_grid_simple(self,benchmark,kwargs):
        reference_optimized_offset=(9, -1087)
        reference_initial_offset=(12,-1088)

        image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_a01.jpg")
        image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_a02.jpg")

        relation=MISRelationRectangular(
            image_pair=(image_a.name,image_b.name),
            rectangular=reference_initial_offset)
        
        results=benchmark(auto_rectangular_skimage.pairwise_registration,
            image_a=image_a,
            image_b=image_b,
            relation=relation,
            **kwargs)
        
        assert dist(results['optimized_offset'],reference_optimized_offset)<2
    @pytest.mark.parametrize(argnames="offset,kwargs",argvalues=[
        pytest.param((9, -1087),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_a01.jpg"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_a02.jpg"),
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            ),id="a01-a02"),
        pytest.param((934, -210),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_b25.tif"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_b26.tif"),
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            ),id="b25-b26"),
        pytest.param((1144, 91),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_c26.tif"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_c27.tif"),
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            ),id="c26-c27"),
        pytest.param((7, -786),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_d04.tif"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_d05.tif"),
            filter=auto_rectangular_skimage.Filter.rgb_gray_mean,
            ),id="d04-d05"),
        pytest.param((0, 1174),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_e004.tif"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_e005.tif"),
            filter=\
                auto_rectangular_skimage.ModifierSkimage.median_disk(radius=2,filter=\
                auto_rectangular_skimage.Modifier.crop(bottom=1672,filter=\
                auto_rectangular_skimage.Filter.float
                ),)
            ),id="e004-e005"),
        pytest.param((-55, 748),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_e100.tif"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_e101.tif"),
            filter=\
                auto_rectangular_skimage.ModifierSkimage.median_disk(radius=2,filter=\
                auto_rectangular_skimage.Modifier.crop(bottom=1672,filter=\
                auto_rectangular_skimage.Filter.float
                ),)
            ),id="e100-e101"),
        pytest.param((12, -3500),dict(
            image_a=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_f03.png"),
            image_b=MISImageFile(image_filepath="tests/test_files/auto_rectangular_skimage/test_image_f04.png"),
            strategy_downsample=10,
            filter=\
                auto_rectangular_skimage.ModifierSkimage.median_disk(radius=2,filter=\
                auto_rectangular_skimage.Modifier.crop(bottom=4096,right=4096,filter=\
                auto_rectangular_skimage.Filter.float
                ),)
            ),id="f03-f04"),
    ])
    def test_pairwise_predict(self,benchmark,offset,kwargs):

        results=benchmark(auto_rectangular_skimage.pairwise_registration,
            relation=None,
            metric=auto_rectangular_skimage.LocateMetricSkimage.modified_pearson,
            strategy=auto_rectangular_skimage.StrategyFullSearch.prediction_grid,
            **kwargs
            )
        
        assert dist(results['optimized_offset'],offset)<5

    #TODO Add more comprehensive tests to DGA
    #TODO figure out a good way to test `interpolated_adaptive_grid` because it is very slow.