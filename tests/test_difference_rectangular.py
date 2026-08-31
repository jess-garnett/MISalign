from math import dist
import numpy as np
import pytest
# from misalign.model.project import MISProjectJSON
from misalign.model.image import MISImageFile
from misalign.model.relation import MISRelationRectangular
import misalign.alignment.difference_rectangular as dr


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


class TestOverlap():
    def test_axis_span_matching_shape_positive_offset(self):
        """
        Tests `axis_span` with matching shapes and positive offset.

        Based on x-axis of `('image_a01.jpg', 'image_a02.jpg')` in `example/project_a/project_a-relations-calibrated.mis.json`.
        """
        a_span,b_span=dr.axis_span(
            offset_vector=12,
            a_shape=1600,
            b_shape=1600)
        assert a_span==(0,1600-12) and b_span==(12,1600)
    def test_axis_span_matching_shape_negative_offset(self):
        """
        Tests `axis_span` with matching shapes and negative offset.

        Based on y-axis of `('image_a01.jpg', 'image_a02.jpg')` in `example/project_a/project_a-relations-calibrated.mis.json`.
        """
        a_span,b_span=dr.axis_span(
            offset_vector=-1088,
            a_shape=1200,
            b_shape=1200)
        assert a_span==(1088,1200) and b_span==(0,1200-1088)
    def test_axis_span_matching_shape_zero_offset(self):
        """
        Tests `axis_span` with matching shapes and zero offset.
        """
        a_span,b_span=dr.axis_span(
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
        (ax_span,ay_span),(bx_span,by_span)=dr.overlap_spans(
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
            dr.overlap_spans(
                    offset_vector=(1600,0),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            dr.overlap_spans(
                    offset_vector=(-1600,0),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            dr.overlap_spans(
                    offset_vector=(0,1200),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            dr.overlap_spans(
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
        overlap_metric=dr.overlap_evaluate(
            array_a=np.full(shape=(100,100),fill_value=100,dtype=np.float32),
            array_b=np.full(shape=(100,100),fill_value=200,dtype=np.float32),
            offset_ab=(50,50),
            metric=metric_sum
        )
        assert overlap_metric==(100*50*50)+(200*50*50)



    def test_overlap_difference_simple(self):
        """
        Tests `overlap_difference` with simplified arrays.
        """
        def metric_sum(overlap_a,overlap_b):
            return np.sum((overlap_a,overlap_b))
        difference=dr.overlap_difference(
            array_a=np.full(shape=(100,100),fill_value=100,dtype=np.float32),
            array_b=np.full(shape=(100,100),fill_value=200,dtype=np.float32),
            offset_ab=(50,50),
        )
        assert np.all(difference==-100)

class TestMetric():
    @pytest.mark.parametrize(argnames="dtype",argvalues=[np.float32,np.float64,np.int16,pytest.param(np.uint8, marks=pytest.mark.xfail)])
    def test_metric_dtypes(self,benchmark,dtype):
        """
        Tests `LocateMetric.mean_squared_difference` with  simplified arrays.
        """
        
        overlap_a=np.full(shape=(50,50),fill_value=100,dtype=dtype)
        overlap_b=np.full(shape=(50,50),fill_value=200,dtype=dtype)
        overlap_metric=benchmark(dr.LocateMetric.mean_squared_difference,
            overlap_a=overlap_a,
            overlap_b=overlap_b
            )
        assert overlap_metric==100**2

    @pytest.mark.parametrize(argnames="metric",argvalues=[
        pytest.param(dr.LocateMetric.mean_squared_difference,id="mean_squared_difference"),
        pytest.param(dr.LocateMetric.mean_absolute_difference,id="mean_absolute_difference"),
        pytest.param(dr.LocateMetric.max_absolute_difference,id="max_absolute_difference"),
        pytest.param(dr.LocateMetric.root_mean_squared_difference,id="root_mean_squared_difference"),
        pytest.param(dr.LocateMetric.norm_root_mean_squared_difference,id="norm_root_mean_squared_difference"),
        pytest.param(dr.LocateMetricSkimage.modified_pearson,id="modified_pearson"),
        pytest.param(lambda a,b:dr.LocateMetricSkimage.modified_pearson(a[::10,::10],b[::10,::10]),id="modified_pearson_downsample"),
        pytest.param(dr.LocateMetricSkimage.modified_mutual_information,id="modified_mutual_information"),
        ])
    def test_metric_locate_simple_1(self,benchmark,simple_parabolic_arrays_1,metric):
        """
        Tests metric that have a minima at the true match with simplified parabolic array.
        """
        array_a,array_b,planned_offset=simple_parabolic_arrays_1

        overlap_metric=benchmark(dr.overlap_evaluate,
            array_a=array_a,
            array_b=array_b,
            offset_ab=planned_offset,
            metric=metric
            )
        assert overlap_metric<1e-3
    
    @pytest.mark.parametrize(argnames="metric,expected_value",argvalues=[
        pytest.param(dr.WeightMetric.highlow_inverse,0.00020824657,id="highlow_inverse"),
        pytest.param(dr.WeightMetric.linear_edge_penalty,0.1366666666666667,id="metric_linear_edge_penalty"),
        ])
    def test_metric_weight_simple_1(self,benchmark,simple_parabolic_arrays_1,metric,expected_value):
        """
        Tests metric which are not expected to consistently have a minima at the true solution.
        """
        array_a,array_b,planned_offset=simple_parabolic_arrays_1

        overlap_metric=benchmark(dr.overlap_evaluate,
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
        
        results=benchmark(dr.Strategy.scaled_grid,
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
        
        results=dr.Strategy.full_grid(
            array_a=array_a,
            array_b=array_b,
            initial_offset=(2,48),
        )

        assert results["optimized_offset"]==planned_offset

        #TODO test more of the items in results.
        #TODO test with noise or other factors.
        
class TestDifferenceGradientAnalysis():
    # (12,-1088) is (3,1) from true solution
    @pytest.mark.parametrize(argnames="size,kwargs",argvalues=[
        pytest.param(5,dict(metric=dr.LocateMetric.mean_squared_difference),id="small"),
        pytest.param(10,dict(metric=dr.LocateMetric.mean_squared_difference),id="small-medium"),
        pytest.param(20,dict(metric=dr.LocateMetric.mean_squared_difference),id="medium"),
    ])
    def test_difference_gradient_analysis_simple(self,benchmark,size,kwargs):
        reference_optimized_relation=(9, -1087)
        reference_initial_relation=(12,-1088)

        image_a=MISImageFile(image_filepath="tests/test_files/test_data/test_image_a01.jpg")
        image_b=MISImageFile(image_filepath="tests/test_files/test_data/test_image_a02.jpg")

        relation=MISRelationRectangular(
            image_pair=(image_a.name,image_b.name),
            rectangular=reference_initial_relation)
        
        dga_results=benchmark(dr.difference_gradient_analysis,
            image_a=image_a,
            image_b=image_b,
            relation=relation,
            strategy_max_size=size,
            **kwargs)
        
        assert dist(dga_results['optimized_offset'],reference_optimized_relation)<2
    #TODO Add more comprehensive tests to DGA