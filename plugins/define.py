## %file:src/define.py
from jinja2 import Environment, PackageLoader, select_autoescape,Template
from typing import List,Dict, Tuple, Sequence
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import os
import re
class MyMacro():
    name=''
    content=''
    lastargs={}
    def render(self,args):
        env = Environment()
        template = Template(self.content)
        ret=template.render(args)
        # print('ret'+'\n')
        return ret
class Mydefine(IStag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return 'Mydefine'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'Mydefine'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDSptag(self) -> List[str]:
        return ['define']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        # self.kobj._write_to_stdout(line+"define on_ISpCodescanning\n")
        # self.kobj.addkey2dict(magics,'define')
        if not magics.__contains__('define'):
            d={'define':{}}
            magics.update(d)
        # envdict=self.kobj.resolving_eqval2dict(value)
        # self.kobj._logln('addmacro')
        self.addmacro(self,magics,line)
        # magics[key] =dict(envdict)
        return ''
    ##在代码预处理前扫描代码时调用    
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        pass
        return False,code
    ##生成文件时调用
    def on_before_buildfile(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_buildfile(self,returncode,srcfile,magics)->bool:
        return False
    def on_before_compile(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_compile(self,returncode,binfile,magics)->bool:
        return False
    def on_before_exec(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_exec(self,returncode,srcfile,magics)->bool:
        return False
    def on_after_completion(self,returncode,execfile,magics)->bool:
        return False


    def loadmacrofile(self,file:str):
        pass
    def delmacro(self,magics,name:str):
        del magics['define'][name]
    def addmacro(self,magics,macrostr:str)->bool:
        # self.kobj.addkey2dict(magics,'define')
        name=''
        args=''
        content=''
        #TODO 解析 macrostr
        if self.kobj._is_specialID(macrostr):
            findObj= re.search( r':(.*)',macrostr)
            if not findObj or len(findObj.group(0))<2:
                return False
        else:
            return False
        key, value = macrostr.strip()[3:].split(":", 2)
        key = key.strip().lower()
        if key != "define":
            return False
        name=''
        content=''
        li = value.strip().split(" ", 1)
        if len(li)>0:
            name = li[0].strip()
        if len(li)>1:
            content = li[1].strip()
        # m.args=args
        # if not self.magics['define'].__contains__(name):
        #     d={name:content}
        #     magics['define'].update(d)
        # else:
        magics['define'][name]=content        
        return True

