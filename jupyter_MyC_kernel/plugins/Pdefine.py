## %file:src/Pdefine.py
import typing as t
import os
from typing import Dict, Tuple, Sequence,List
from jinja2 import Environment, PackageLoader, select_autoescape,Template
import re

from plugins.ISpecialID import IStag,IDtag,IBtag,ITag,ICodePreproc
class MyPDefine(ICodePreproc):
    kobj=None
    def getName(self) -> str:
        return 'MyPDefine'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyPDefine'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    ##在代码预处理前扫描代码时调用    
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        ##扫描源码
        # self.kobj._logln("----on_Codescanning----")
        actualCode =''
        # self.kobj._logln(code)
        for line in code.splitlines():
            ##扫描源码每行行
            orgline=line
            if not (line.strip().startswith('##$') or line.strip().startswith('//$')):
                actualCode += line + '\n'
                continue
            name=''
            argsstr=''

            li = line.strip()[3:].strip().split(" ", 1)
            if len(li)>0:
                name = li[0].strip()
            if len(li)>1:
                argsstr = li[1].strip()
            args=self.kobj.resolving_eqval2dict(argsstr)
            line=self.macrorender(self,magics,name,args)
            ##替换所有 name 为 line
            actualCode += line + '\n'
        # self.kobj._logln(actualCode)
        return False,actualCode
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
    def macrorender(self,magics,name:str,args:Dict)->str:
        if not magics['define'].__contains__(name):
            return ''
        content=magics['define'][name]
        # env = Environment()
        template = Template(content)
        ret=template.render(args)
        return ret
    def _is_specialID(self,line):
        if line.strip().startswith('##%') or line.strip().startswith('//%'):
            return True
        return False

