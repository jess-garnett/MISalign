from misalign.model.project import MISProject, MISProjectJSON
from misalign.model.image import MISImageFile
from misalign.model.relation import MISRelationReference

class TestMISProjectJSON():
    # def test_protocol_isinstance(self):
    #     assert isinstance(MISProjectJSON,MISProject)
    def test_init_none(self):
        test_mis=MISProjectJSON()
        assert str(test_mis)=="An empty misalign project."
    def test_init_images(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_images=[MISImageFile(image_filepath=x) for x in test_image_fps]
        test_mis=MISProjectJSON(
            images=test_images
            )
        expected_result="""A misalign project with:
Images:
    test_a.png
    test_b.png
    test_c.png
Relations:

Calibration:

Project Path:
    None"""
        result=str(test_mis)
        assert result==expected_result
    def test_init_relations(self):
        test_relations=[MISRelationReference(image_pair=("test_a.png","test_b.png")),
                        MISRelationReference(image_pair=("test_b.png","test_c.png"))]
        test_mis=MISProjectJSON(
            relations=test_relations
            )
        expected_result="""A misalign project with:
Images:

Relations:
    ('test_a.png', 'test_b.png')
    ('test_b.png', 'test_c.png')
Calibration:

Project Path:
    None"""
        result=str(test_mis)
        assert result==expected_result
    def test_init_calibrations(self):
        test_calibration={
                            "pixel": 600,
                            "length": 1,
                            "length_unit": "mm"
                        }
        test_mis=MISProjectJSON(
            calibration=test_calibration
            )
        expected_result="""A misalign project with:
Images:

Relations:

Calibration:
    pixel : 600
    length : 1
    length_unit : mm
Project Path:
    None"""
        result=str(test_mis)
        assert result==expected_result
    def test_init_filepath(self):
        test_project_path="project.json"
        test_mis=MISProjectJSON(
            file_path=test_project_path
            )
        expected_result="""A misalign project with:
Images:

Relations:

Calibration:

Project Path:
    project.json"""
        result=str(test_mis)
        assert result==expected_result
    def test_init_all(self):
        test_image_fps=["test_a.png","test_b.png","test_c.png"]
        test_images=[MISImageFile(image_filepath=x) for x in test_image_fps]
        test_relations=[MISRelationReference(image_pair=("test_a.png","test_b.png")),
                        MISRelationReference(image_pair=("test_b.png","test_c.png"))]
        test_calibration={
                            "pixel": 600,
                            "length": 1,
                            "length_unit": "mm"
                        }
        test_project_path="project.json"
        test_mis=MISProjectJSON(
            images=test_images,
            relations=test_relations,
            calibration=test_calibration,
            file_path=test_project_path
            )
        expected_result="""A misalign project with:
Images:
    test_a.png
    test_b.png
    test_c.png
Relations:
    ('test_a.png', 'test_b.png')
    ('test_b.png', 'test_c.png')
Calibration:
    pixel : 600
    length : 1
    length_unit : mm
Project Path:
    project.json"""
        result=str(test_mis)
        assert result==expected_result