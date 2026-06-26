from pathlib import Path
from misalign.model.project import MISProject, MISProjectJSON, MISProjectHDF5
from misalign.model.image import MISImageFile
from misalign.model.relation import MISRelationReference
import numpy as np


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

class TestMISProjectHDF5():
    # def test_protocol_isinstance(self):
    #     assert isinstance(MISProjectHDF5,MISProject)
    def test_load_str(self):
        test_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5"
        project_hdf5path="MISContainer0/MISProjectJSON0"
        mp=MISProjectHDF5.load(test_filepath,project_hdf5path=project_hdf5path)
        expected_result=f"""A misalign project with:
Images:
    image_a01.jpg
    image_a02.jpg
    image_a03.jpg
Relations:
    ('image_a01.jpg', 'image_a02.jpg')
    ('image_a02.jpg', 'image_a03.jpg')
Calibration:
    pixel : 600
    length : 1
    length_unit : mm
Project Path:
    {Path(test_filepath)}"""
        assert str(mp)==expected_result
    def test_build_empty(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-empty.hdf5"
        try:
            mis_project=MISProjectHDF5.build(mis_filepath=test_filepath)
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-empty.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(
                mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
        finally:
            Path(test_filepath).unlink()
    def test_build_include_image_filepaths(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-include_image_filepaths.hdf5"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                include_image_filepaths=[
                    'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                    'tests/test_files/canvas_rectangular/test_image_a01_h_r.png'])
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-include_image_filepaths.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [
                    {'image_filepath': 'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                        'image_type': 'file'},
                    {'image_filepath': 'tests/test_files/canvas_rectangular/test_image_a01_h_r.png',
                        'image_type': 'file'}
                    ],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
        finally:
            Path(test_filepath).unlink()
    def test_build_ingest_image_filepaths(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-ingest_image_filepaths.hdf5"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                ingest_image_filepaths=[
                    'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                    'tests/test_files/canvas_rectangular/test_image_a01_h_r.png'])
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_filepaths.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_filepaths.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_l.png',
                        'image_name': 'test_image_a01_h_l.png',
                        'image_type': 'hdf5'},
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_filepaths.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_r.png',
                        'image_name': 'test_image_a01_h_r.png',
                        'image_type': 'hdf5'}
                    ],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
            assert test_mis_project.get_image(test_mis_project.get_image_names()[0]).shape==(1200,850,3)
        finally:
            Path(test_filepath).unlink()
    def test_build_include_image_objects(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-ingest_image_objects.hdf5"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                include_image_objects=[MISImageFile(image_filepath=x) for x in [
                    'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                    'tests/test_files/canvas_rectangular/test_image_a01_h_r.png']])
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_objects.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [
                    {'image_filepath': 'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                        'image_type': 'file'},
                    {'image_filepath': 'tests/test_files/canvas_rectangular/test_image_a01_h_r.png',
                        'image_type': 'file'}
                    ],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
        finally:
            Path(test_filepath).unlink()
    def test_build_ingest_image_objects(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-ingest_image_objects.hdf5"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                ingest_image_objects=[MISImageFile(image_filepath=x) for x in [
                    'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                    'tests/test_files/canvas_rectangular/test_image_a01_h_r.png']])
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_objects.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_objects.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_l.png',
                        'image_name': 'test_image_a01_h_l.png',
                        'image_type': 'hdf5'},
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_image_objects.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_r.png',
                        'image_name': 'test_image_a01_h_r.png',
                        'image_type': 'hdf5'}
                    ],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
            assert test_mis_project.get_image(test_mis_project.get_image_names()[0]).shape==(1200,850,3)
        finally:
            Path(test_filepath).unlink()
    def test_build_ingest_arrays(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-ingest_arrays.hdf5"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                ingest_arrays={x.split("/")[-1]:np.asarray(MISImageFile(image_filepath=x)) for x in [
                    'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                    'tests/test_files/canvas_rectangular/test_image_a01_h_r.png']})
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_arrays.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_arrays.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_l.png',
                        'image_name': 'test_image_a01_h_l.png',
                        'image_type': 'hdf5'},
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-build-ingest_arrays.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_r.png',
                        'image_name': 'test_image_a01_h_r.png',
                        'image_type': 'hdf5'}
                    ],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
            assert test_mis_project.get_image(test_mis_project.get_image_names()[0]).shape==(1200,850,3)
        finally:
            Path(test_filepath).unlink()
    def test_build_calibration_filepath(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-calibration_filepath.hdf5"
        test_calibration_filepath="tests/test_files/test_data/test_calibration.miscal.json"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                calibration_filepath=test_calibration_filepath)
            assert mis_project.for_json()=={
                'calibration': {
                            "pixel": 600,
                            "length": 1,
                            "length_unit": "mm"
                            },
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-calibration_filepath.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(
                mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
        finally:
            Path(test_filepath).unlink()
    def test_build_calibration_dict(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-build-calibration_dict.hdf5"
        test_calibration={
                            "pixel": 600,
                            "length": 1,
                            "length_unit": "mm"
                        }
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                calibration_dict=test_calibration)
            assert mis_project.for_json()=={
                'calibration': {
                            "pixel": 600,
                            "length": 1,
                            "length_unit": "mm"
                            },
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-build-calibration_dict.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [],
                'relations': []}
            test_mis_project=MISProjectHDF5.load(
                mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
        finally:
            Path(test_filepath).unlink()

#TODO Consider checking the contents off ingested arrays.
    # Currently shape is checked as a proxy for "correct data" but that doesn't validate the contents.

    def test_save_added_relations(self):
        test_filepath="tests/test_files/test_hdf5/temp-test-project-save-added_relations.hdf5"
        try:
            mis_project=MISProjectHDF5.build(
                mis_filepath=test_filepath,
                ingest_image_filepaths=[
                    'tests/test_files/canvas_rectangular/test_image_a01_h_l.png',
                    'tests/test_files/canvas_rectangular/test_image_a01_h_r.png'])
            mis_project.add_relation(
                relation=MISRelationReference(
                    image_pair=('test_image_a01_h_l.png','test_image_a01_h_r.png')))
            assert mis_project.for_json()=={
                'calibration': {},
                'file_path': 'tests/test_files/test_hdf5/temp-test-project-save-added_relations.hdf5',
                'hdf5_path': 'MISContainer0/project',
                'images': [
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-save-added_relations.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_l.png',
                        'image_name': 'test_image_a01_h_l.png',
                        'image_type': 'hdf5'},
                    {'hdf5_filepath': 'tests/test_files/test_hdf5/temp-test-project-save-added_relations.hdf5',
                        "hdf5path": 'MISContainer0/images/test_image_a01_h_r.png',
                        'image_name': 'test_image_a01_h_r.png',
                        'image_type': 'hdf5'}
                    ],
                'relations': [
                    {'image_pair': ['test_image_a01_h_l.png','test_image_a01_h_r.png',],
                    'relation_type': None,},
                    ]}
            mis_project.save(mis_filepath=test_filepath)
            test_mis_project=MISProjectHDF5.load(
                mis_filepath=test_filepath)
            assert mis_project.for_json()==test_mis_project.for_json()
        finally:
            Path(test_filepath).unlink()