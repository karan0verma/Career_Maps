import urllib.request
import re

content = urllib.request.urlopen("https://career.infosys.com/main.js").read().decode('utf-8', errors='ignore')

idx = content.find("class Je{") # Je is JobdescriptionComponent
if idx == -1:
    idx = content.find("JobdescriptionComponent:()=>")
    # find class name
    cls_name = content[idx+29:idx+31]
    print("Class name:", cls_name)
    idx = content.find(f"class {cls_name}")

if idx != -1:
    snippet = content[idx:idx+4000]
    print("--- Class definition ---")
    print(snippet)
