import numpy as np
import pytest
# from misalign.model.project import MISProjectJSON
from misalign.model.image import MISImageFile
from misalign.model.relation import MISRelationRectangular
import misalign.alignment.difference_rectangular as dr

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
    def test_metric_difference_squared_mean_simple(self):
        """
        Tests `metric_difference_squared_mean` with  simplified arrays.
        """
        
        overlap_metric=dr.metric_difference_squared_mean(
            overlap_a=np.full(shape=(50,50),fill_value=100,dtype=np.float32),
            overlap_b=np.full(shape=(50,50),fill_value=200,dtype=np.float32)
            )
        assert overlap_metric==100**2
    def test_metric_difference_absolute_mean_simple(self):
        """
        Tests `metric_difference_absolute_mean` with  simplified arrays.
        """
        
        overlap_metric=dr.metric_difference_absolute_mean(
            overlap_a=np.full(shape=(50,50),fill_value=100,dtype=np.float32),
            overlap_b=np.full(shape=(50,50),fill_value=200,dtype=np.float32)
            )
        assert overlap_metric==100


class TestStrategy():
    def test_strategy_scaled_grid_simple(self):
        """
        Tests `strategy_scaled_grid` with  simplified arrays and offsets.
        """
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

        assert array_a[50,50]==0 and array_b[45,47]==0
        
        results=dr.strategy_scaled_grid(
            array_a=array_a,
            array_b=array_b,
            initial_offset=(-5,-5),
            strategy_grid_scale=1,
        )

        assert results["optimized_offset"]==planned_offset

        results=dr.strategy_scaled_grid(
            array_a=array_a,
            array_b=array_b,
            initial_offset=(-7,1),
            strategy_grid_scale=2,
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
        
        results=dr.strategy_full_grid(
            array_a=array_a,
            array_b=array_b,
            initial_offset=(2,48),
        )

        assert results["optimized_offset"]==planned_offset

        #TODO test more of the items in results.
        #TODO test with noise or other factors.

class TestDifferenceGradientAnalysis():
    def test_difference_gradient_analysis_simple(self):
        reference_optimized_relation=(9, -1087)
        reference_initial_relation=(12,-1088)

        image_a=MISImageFile(image_filepath="tests/test_files/test_data/test_image_a01.jpg")
        image_b=MISImageFile(image_filepath="tests/test_files/test_data/test_image_a02.jpg")

        relation=MISRelationRectangular(
            image_pair=(image_a.name,image_b.name),
            rectangular=reference_initial_relation)
        
        dga_results=dr.difference_gradient_analysis(
            image_a=image_a,
            image_b=image_b,
            relation=relation)
        
        assert dga_results['optimized_offset']==reference_optimized_relation
    #TODO Add more comprehensive tests to DGA