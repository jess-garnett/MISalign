from MISalign.model.project import MISProject, MISProjectJSON, load_mis_project_json, save_mis_project_json

class TestMISProjectJSON():
    def test_protocol_isinstance(self):
        assert isinstance(MISProjectJSON,MISProject)
    def test_mis_init_none(self):
        test_mis=MISProjectJSON()
        assert str(test_mis)=="An empty MISalign project."