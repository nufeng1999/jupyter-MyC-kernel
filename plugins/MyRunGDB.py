##//%file:../../jupyter-MyPython-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyDart-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyKotlin-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyGroovy-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyJava-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyGjs-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyVala-kernel/plugins/MyRunGDB.py
##//%file:../../jupyter-MyNodejs-kernel/plugins/MyRunGDB.py
from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import os
class MyRunGDB(IBtag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        
        return 'MyShowpid'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyShowpid'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDBptag(self) -> List[str]:
        return ['rungdb','gdb']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_IBpCodescanning(self,magics,line) -> str:
        # self.kobj._write_to_stdout(line+" on_ISpCodescanning\n")
        self.kobj.addkey2dict(magics,'rungdb')
        magics['rungdb'] = ['true']
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
    
