import pytest
from MISalign.model.relation import Relation, MISRelation, MISRelationReference, MISRelationRectangular, MISRelationPoints, setup_relation, relation_types

class TestRelation():
    def test_relation_init_none(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_relation=Relation(test_img_a,test_img_b)
        assert str(test_relation)=="Image 'test_b.png' relates to image 'test_a.png' by:[None, None, None]"
    def test_relation_init_rectilinear(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="r"
        test_data=(100,100)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert str(test_relation)=="Image 'test_b.png' relates to image 'test_a.png' by:[(100, 100), None, None]"
    def test_relation_get_rel_rectilinear(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="r"
        test_data=(100,100)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert test_relation.get_rel('r')==test_data
    def test_relation_init_rectrota(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="rr"
        test_data_rect=(100,100)
        test_data_rota=45
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data_rect,test_data_rota)
        assert str(test_relation)=="Image 'test_b.png' relates to image 'test_a.png' by:[(100, 100), 45, None]"
    def test_relation_get_rel_rectrota(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="rr"
        test_data_rect=(100,100)
        test_data_rota=45
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data_rect,test_data_rota)
        assert test_relation.get_rel('rr')==[test_data_rect, test_data_rota]
    def test_relation_init_points(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert str(test_relation)=="Image 'test_b.png' relates to image 'test_a.png' by:[None, None, (((0, 0), (100, 100)), ((0, 10), (107, 107)))]"
    def test_relation_get_rel_points(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert test_relation.get_rel('p')==test_data
    def test_relation_get_r_points(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        expected_r=(100,102)
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        assert test_relation.get_rel('r')==expected_r
    def test_relation_get_rr_points(self):
        test_img_a="test_a.png"
        test_img_b="test_b.png"
        test_rel="p"
        test_data=(((0,0),(100,100)),((0,10),(107,107)))
        test_relation=Relation(test_img_a,test_img_b,test_rel,test_data)
        expected_rr=None #TODO implement actual rotation solution algorithm.
        assert test_relation.get_rel('rr')==expected_rr


class Test_setup_relation():
    def test_setup_reference(self):
        assert type(setup_relation(
            image_pair=("test_a","test_b"),
            relation_type=None
            ))==MISRelationReference
    def test_setup_rectangular(self):
        assert type(setup_relation(
            image_pair=("test_a","test_b"),
            relation_type='r',
            rectangular=(100,100)
            ))==MISRelationRectangular
    def test_setup_points(self):
        assert type(setup_relation(
            image_pair=("test_a","test_b"),
            relation_type='p',
            points=(((0,0),(100,100)),((0,10),(100,115)))
            ))==MISRelationPoints
class TestMISRelationReference():
    def test_protocol_isinstance(self):
        assert isinstance(MISRelationReference,MISRelation)
    def test_init(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_relation=MISRelationReference(image_pair=(test_img_a,test_img_b))
        assert str(test_relation)=="Image 'test_b' is related to image 'test_a'."
    def test_get_reference(self):
        test_img_a="test_a"
        test_img_b="test_b"
        expected_reference=("test_a","test_b")
        test_relation=MISRelationReference(image_pair=(test_img_a,test_img_b))
        assert test_relation.get_reference()==expected_reference
    def test_save_dict(self):
        test_img_a="test_a"
        test_img_b="test_b"
        expected_save=dict(image_pair=(test_img_a,test_img_b),relation_type=None)
        test_relation=MISRelationReference(image_pair=(test_img_a,test_img_b))
        assert test_relation.save_dict()==expected_save
class TestMISRelationRectangular():
    def test_protocol_isinstance(self):
        assert isinstance(MISRelationRectangular,MISRelation)
    def test_init(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(100,100)
        test_relation=MISRelationRectangular(
            image_pair=(test_img_a,test_img_b),
            rectangular=test_data)
        assert str(test_relation)=="Image 'test_b' is related to image 'test_a' by (100, 100)."
    def test_get_reference(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(100,100)
        expected_reference=("test_a","test_b")
        test_relation=MISRelationRectangular(
            image_pair=(test_img_a,test_img_b),
            rectangular=test_data)
        assert test_relation.get_reference()==expected_reference
    def test_get_relation_rectangular(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(100,100)
        expected_relation=(100,100)
        test_relation=MISRelationRectangular(
            image_pair=(test_img_a,test_img_b),
            rectangular=test_data)
        assert test_relation.get_relation('r')==expected_relation
    def test_get_relation_points(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(100,100)
        expected_relation=(((100,100),(0,0)))
        test_relation=MISRelationRectangular(
            image_pair=(test_img_a,test_img_b),
            rectangular=test_data)
        assert test_relation.get_relation('p')==expected_relation
    def test_save_relation(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(100,100)
        expected_save=dict(image_pair=("test_a","test_b"),relation_type='r',rectangular=(100,100))
        test_relation=MISRelationRectangular(
            image_pair=(test_img_a,test_img_b),
            rectangular=test_data)
        assert test_relation.save_dict()==expected_save
class TestMISRelationPoints():
    def test_protocol_isinstance(self):
        assert isinstance(MISRelationPoints,MISRelation)
    def test_init(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        test_relation=MISRelationPoints(
            image_pair=(test_img_a,test_img_b),
            points=test_data)
        assert str(test_relation)=="Image 'test_b' is related to image 'test_a' by (((0, 0), (100, 100)), ((0, 10), (100, 115)))."
    def test_get_reference(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        expected_reference=("test_a","test_b")
        test_relation=MISRelationPoints(
            image_pair=(test_img_a,test_img_b),
            points=test_data)
        assert test_relation.get_reference()==expected_reference
    def test_get_relation_rectangular(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        expected_relation=(100,102)
        test_relation=MISRelationPoints(
            image_pair=(test_img_a,test_img_b),
            points=test_data)
        assert test_relation.get_relation('r')==expected_relation
    def test_get_relation_points(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        expected_relation=(((0,0),(100,100)),((0,10),(100,115)))
        test_relation=MISRelationPoints(
            image_pair=(test_img_a,test_img_b),
            points=test_data)
        assert test_relation.get_relation('p')==expected_relation
    def test_save_relation(self):
        test_img_a="test_a"
        test_img_b="test_b"
        test_data=(((0,0),(100,100)),((0,10),(100,115)))
        expected_save=dict(image_pair=("test_a","test_b"),relation_type='p',points=(((0,0),(100,100)),((0,10),(100,115))))
        test_relation=MISRelationPoints(
            image_pair=(test_img_a,test_img_b),
            points=test_data)
        assert test_relation.save_dict()==expected_save