import pytest
from MISalign.model.mis_file import MisFile
from MISalign.model.relation import Relation

class TestMisFile():
    def test_mis_init_none(self):
        test_mis=MisFile()
        assert str(test_mis)=="An empty MISalign project."
    def test_mis_init_image_fps(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_mis=MisFile(image_fps=test_image_fps)
        assert str(test_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], None, None]"
    def test_mis_init_relations(self):
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(relations=test_relations)
        assert str(test_mis)=="A MISalign project with:[None, [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], None]"
    def test_mis_init_img_rel(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(image_fps=test_image_fps,relations=test_relations)
        assert str(test_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], None]"