import pytest
from MISalign.model.relation import Relation

class TestRelation():
    def test_offset_init_rectilinear(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="r"
        test_data=(100,100)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[(100, 100), None, None]"
    def test_offset_init_rectrota(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="rr"
        test_data_rect=(100,100)
        test_data_rota=45
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data_rect,test_data_rota)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[(100, 100), 45, None]"
    def test_offset_init_points(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="r"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[(((0, 0), (100, 100)), ((0, 10), (107, 107))), None, None]"