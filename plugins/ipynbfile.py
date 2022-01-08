##
import json
import os
from json import JSONDecoder
def loadnb(fileitem):
    if len(fileitem.strip())<1:return None,None
    li=fileitem.split(" ", 1)
    if len(li)<2:return None,None
    filename=li[0]
    index=int(li[1])
    return filename,loadnbcellcode(filename,index)
def getnbcodecount(filename):
    count=0
    try:
        with open(filename, 'r',encoding='UTF-8') as f:
            jsc = json.load(f)
            count=len(jsc['cells'])
    except Exception as e:
        raise
    return count
def loadnbcellcode(filename,index):
    code=''
    decoder = JSONDecoder()
    try:
        with open(filename, 'r',encoding='UTF-8') as f:
            jsc = json.load(f)
            if jsc['cells'][index]["cell_type"]=="code":
                source=jsc['cells'][index]["source"]
                source=eval(str(source))
                for c in source:
                    code+=c
    except Exception as e:
        raise
        code=''
    return code
