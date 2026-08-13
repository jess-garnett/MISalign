import numpy as np
import pytest
from misalign.model.project import MISProjectJSON
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
            axy_bxy_spans=dr.overlap_spans(
                    offset_vector=(1600,0),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            axy_bxy_spans=dr.overlap_spans(
                    offset_vector=(-1600,0),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            axy_bxy_spans=dr.overlap_spans(
                    offset_vector=(0,1200),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
        with pytest.raises(expected_exception=ValueError):
            axy_bxy_spans=dr.overlap_spans(
                    offset_vector=(0,-1200),
                    a_shape=(1200,1600),
                    b_shape=(1200,1600)
                )
    #TODO diversify offsets/shapes tested.
    


    def test_overlap_evaluate_simple(self):
        """
        Tests `overlap_compare` with a simplified metric and array.
        """
        def metric_sum(overlap_a,overlap_b):
            return np.sum((overlap_a,overlap_b))
        overlap_metric=dr.overlap_evaluate(
            array_a=np.full(shape=(100,100),fill_value=100,dtype=np.uint8),
            array_b=np.full(shape=(100,100),fill_value=200,dtype=np.uint8),
            offset_ab=(50,50),
            metric=metric_sum
        )
        assert overlap_metric==(100*50*50)+(200*50*50)



    def test_overlap_difference_simple(self):
        """
        Tests `overlap_difference` with a simplified array.
        """
        def metric_sum(overlap_a,overlap_b):
            return np.sum((overlap_a,overlap_b))
        difference=dr.overlap_difference(
            array_a=np.full(shape=(100,100),fill_value=100,dtype=np.uint8),
            array_b=np.full(shape=(100,100),fill_value=200,dtype=np.uint8),
            offset_ab=(50,50),
        )
        assert np.all(difference==-100)