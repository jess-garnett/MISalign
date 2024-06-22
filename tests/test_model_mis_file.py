import pytest
from MISalign.model.mis_file import MisFile,save_mis,load_mis
from MISalign.model.relation import Relation
from os.path import abspath

class TestMisFile():
    ### Initialization Testing
    def test_mis_init_none(self):
        test_mis=MisFile()
        assert str(test_mis)=="An empty MISalign project."
    def test_mis_init_image_fps(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_mis=MisFile(image_fps=test_image_fps)
        assert str(test_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], [], {}]"
    def test_mis_init_relations(self):
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(relations=test_relations)
        assert str(test_mis)=="A MISalign project with:[[], [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], {}]"
    def test_mis_init_img_rel(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(image_fps=test_image_fps,relations=test_relations)
        assert str(test_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], {}]"

    ### Save & Load Testing
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
        assert str(sl_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], [], {}]"

    def test_mis_save_load_relations(self):
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(relations=test_relations)
        
        mis_fp=r".\tests\test_files\sl_rel.mis"
        save_mis(mis_fp,test_mis)
        sl_mis=load_mis(mis_fp)
        assert str(sl_mis)=="A MISalign project with:[[], [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], {}]"

    def test_mis_save_load_img_rel(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_relations=[Relation("test_a.png","test_b.png"),Relation("test_b.png","test_c.png")]
        test_mis=MisFile(image_fps=test_image_fps,relations=test_relations)
        
        mis_fp=r".\tests\test_files\sl_img_rel.mis"
        save_mis(mis_fp,test_mis)
        sl_mis=load_mis(mis_fp)
        assert str(sl_mis)=="A MISalign project with:[['test_a.png', 'test_b.png', 'test_c.png'], [('test_a.png', 'test_b.png'), ('test_b.png', 'test_c.png')], {}]"
    
    #TODO add tests for relations with values
    ### Usage Testing
    def test_get_image_paths(self):
        #Tests function that returns {name:path} dictionary.
        mis_fp=r".\tests\test_files\get_image_paths.mis"
        usage_mis=load_mis(mis_fp)

        correct_paths={}
        um_paths=usage_mis.get_image_paths()
        assert um_paths==correct_paths
    def test_get_image_names(self):
        #Tests function that returns [name] list.
        mis_fp=r".\tests\test_files\get_image_names.mis"
        usage_mis=load_mis(mis_fp)

        correct_names=[]
        um_names=usage_mis.get_image_names()
        assert um_names==correct_names
    def test_check_image_paths(self):
        #Tests function that returns {name:{found:boolean,path:boolean}} dictionary.
        mis_fp=r".\tests\test_files\check_image_paths.mis"
        usage_mis=load_mis(mis_fp)

        correct_check={}
        um_check_paths=usage_mis.check_image_paths()
        assert um_check_paths==correct_check
        assert False
