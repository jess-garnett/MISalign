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
        Tests `overlap_spans` with one negative and one positive offset.

        Based on `('image_a01.jpg', 'image_a02.jpg')` in `example/project_a/project_a-relations-calibrated.mis.json`.
        """
        (ax_span,ay_span),(bx_span,by_span)=dr.overlap_spans(
                offset_vector=(12,-1088),
                a_shape=(1200,1600),
                b_shape=(1200,1600)
            )
        assert ax_span==(0,1600-12) and bx_span==(12,1600) and ay_span==(1088,1200) and by_span==(0,1200-1088)
    #TODO diversify offsets/shapes tested.