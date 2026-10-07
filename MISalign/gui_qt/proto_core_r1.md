---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: .venv (3.10.8)
  language: python
  name: python3
---

# 251031 MisFile-Parameter correlation

```{code-cell} ipython3
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
import pyqtgraph.parametertree.parameterTypes as pTypes
from json import loads,dumps,load
```

```{code-cell} ipython3
from sys import path as syspath
syspath.append("../..")
```

```{code-cell} ipython3
from MISalign.model.mis_file import MisFile, load_mis, mis_from_dict, mis_to_dict
```

```{code-cell} ipython3
mis_file=load_mis(r"C:\Users\drago\Documents\git_gh\MISalign\example\data\set_a\set_a2_calibrated.mis")
```

```{code-cell} ipython3
print(mis_file.image_fps)
print(mis_file._relations)
print(mis_file.calibration)
print(mis_to_dict(mis_file))
```

```{code-cell} ipython3
%gui qt
```

```{code-cell} ipython3
for key,value in mis_to_dict(mis_file).items():
    print(key,value)
```

```{code-cell} ipython3
class MISParameter(pTypes.GroupParameter):
    def __init__(self, mis_file, **opts):
        opts['name'] = 'MIS File'
        opts['type'] = 'group'
        pTypes.GroupParameter.__init__(self,**opts)

        self.set_misfile(mis_file)

    def set_misfile(self,mis_file:MisFile):
        self.clearChildren()
        for key,value in mis_to_dict(mis_file).items():
            if key=="image_fps":
                current_item:pTypes.GroupParameter=self.addChild({'name':key,'type':'group','addText':'Add Files','addList':['From Path','From File Select','Select Multiple']})
                current_item.sigAddNew.connect(self.add_file)
                for shortname,path in mis_file.get_image_paths().items():
                    current_item.addChild({'name':shortname,'type':'str','value':path}).sigValueChanged.connect(self.reload_misfile)
            elif key=="relations": #TODO add "add relation" option.
                current_item=self.addChild({'name':key,'type':'group'})
                for i,i_value in enumerate(value):
                    current_item.addChild({'name':str(i),'type':"str",'value':dumps(i_value),"removable":True})
            elif key=="calibration":
                if len(value)==0:
                    current_item=self.addChild({'name':key,'type':'group',"addText":"Add Calibration","addList":["Add Manual","Add From File"]}) #TODO add 'add calibration'/'update calibration' options.
                    current_item.sigAddNew.connect(self.add_calibration)
                else:
                    current_item=self.addChild({'name':key,'type':'group',"addText":"Update From File"})
                    current_item.sigAddNew.connect(self.add_calibration)
                    for i_key,i_value in value.items():
                        current_item.addChild({'name':i_key,'type':type(i_value).__name__,'value':i_value})

    def get_misfile(self,**mis_kwargs):
        mis_dict=dict()
        mis_dict["image_fps"]=[c.value() for c in self.child("image_fps").children()]
        mis_dict["relations"]=[loads(c.value()) for c in self.child("relations").children()]
        mis_dict["calibration"]={c.name():c.value() for c in self.child("calibration").children()}
        for key,value in mis_kwargs.items():
            mis_dict[key]=value
        return mis_from_dict(mis_dict)
    
    def add_file(self,param:pTypes.GroupParameter,option:str):
        if option=='From Path':
            param.addChild({'name':"New File","type":"str"}).sigValueChanged.connect(self.reload_misfile)
        elif option=='From File Select':
            file_selection=pTypes.file.popupFilePicker()
            if file_selection is not None:
                param.addChild({"name":"New File","type":"str","value":file_selection})
                self.reload_misfile()
        elif option=='Select Multiple':
            files_selection=pTypes.file.popupFilePicker(FileMode="ExistingFiles")
            for i,fp in enumerate(files_selection):
                param.addChild({'name':str(i),"type":"str","value":fp}) 
            self.reload_misfile()

    def reload_misfile(self,**mis_kwargs):
        mis_file=self.get_misfile(**mis_kwargs)
        self.set_misfile(mis_file)

    def add_calibration(self,param:pTypes.GroupParameter,option):
        # option can be one of the drop down selecction "Add Manual","Add From File" or None for the button "Update From File"
        if option=="Add Manual":
            for c_name,c_type in zip(["pixel","length","length_unit"],["float","float","str"]):
                param.addChild({"name":c_name,"type":c_type})
            self.reload_misfile()
        if option=="Add From File" or option==None:
            file_selection=pTypes.file.popupFilePicker()
            print(file_selection)
            self.reload_misfile(calibration_fp=file_selection)

p=MISParameter(MisFile())
# p=MISParameter(mis_file)

t=ParameterTree()
t.setParameters(param=p)

win = pg.Qt.QtWidgets.QMainWindow()
win.setCentralWidget(t)
win.show()
p.get_misfile()
```

```{code-cell} ipython3
p.reload_misfile()
```

```{code-cell} ipython3
mf2=p.get_misfile()
```

```{code-cell} ipython3
mis_to_dict(mf2) == mis_to_dict(mis_file)
```
