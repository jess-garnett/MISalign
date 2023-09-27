import pytest
from MISalign.model.relation import Relation

class TestRelation():
    def test_relation_init_none(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_relation=Relation(test_img_a,test_img_b)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[None, None, None]"
    def test_relation_init_rectilinear(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="r"
        test_data=(100,100)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[(100, 100), None, None]"
    def test_relation_get_rel_rectilinear(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="r"
        test_data=(100,100)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert test_relation.get_rel('r')==test_data
    def test_relation_init_rectrota(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="rr"
        test_data_rect=(100,100)
        test_data_rota=45
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data_rect,test_data_rota)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[(100, 100), 45, None]"
    def test_relation_get_rel_rectrota(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="rr"
        test_data_rect=(100,100)
        test_data_rota=45
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data_rect,test_data_rota)
        assert test_relation.get_rel('rr')==[test_data_rect, test_data_rota]
    def test_relation_init_points(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert str(test_relation)=="Image 'test_a.png' relates to image 'test_a.png' by:[None, None, (((0, 0), (100, 100)), ((0, 10), (107, 107)))]"
    def test_relation_get_rel_points(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert test_relation.get_rel('p')==test_data
    def test_relation_get_r_points(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        expected_r=(100,102)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert test_relation.get_rel('r')==expected_r
    def test_relation_get_rr_points(self):
        test_img_a="test_a.png"
        test_img_b="test_a.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        expected_rr=None #TODO implement actual rotation solution algorithm.
        assert test_relation.get_rel('rr')==expected_rr