import pytest
from MISalign.model.mis_file import MisFile,save_mis,load_mis
from MISalign.model.relation import Relation
from os.path import abspath

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
    
    def test_mis_save_load_none(self):
        test_mis=MisFile()

        mis_fp=abspath(r".\tests\test_files\sl_none.mis")
        save_mis(mis_fp,test_mis)
        sl_mis=load_mis(mis_fp)
        assert str(sl_mis)=="An empty MISalign project."

    def test_mis_save_load_image_fps(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_mis=MisFile(image_fps=test_image_fps)
        
        mis_fp=r".\tests\test_files\sl_img.mis"
        save_mis(mis_fp,test_mis)
        sl_mis=load_mis(mis_fp)
        assert str(sl_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], None, None]"

    def test_mis_save_load_relations(self):
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(relations=test_relations)
        
        mis_fp=r".\tests\test_files\sl_rel.mis"
        save_mis(mis_fp,test_mis)
        sl_mis=load_mis(mis_fp)
        assert str(sl_mis)=="A MISalign project with:[None, [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], None]"

    def test_mis_save_load_img_rel(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(image_fps=test_image_fps,relations=test_relations)
        
        mis_fp=r".\tests\test_files\sl_img_rel.mis"
        save_mis(mis_fp,test_mis)
        sl_mis=load_mis(mis_fp)
        assert str(sl_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], None]"