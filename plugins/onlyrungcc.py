from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import os
class Myonlyrungcc(IBtag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return 'Myonlyrungcc'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'Myonlyrungcc'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDBptag(self) -> List[str]:
        return ['onlyrungcc']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_IBpCodescanning(self,magics,line) -> str:
        # self.kobj._write_to_stdout(line+" on_IBpCodescanning\n")
        self.kobj.addkey2dict(magics,'onlyrungcc')
        magics['onlyrungcc'] = ['true']
        # self.kobj._log(magics['onlyrungcc']+" on_IBpCodescanning\n")
        return ''
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        pass
        return False,code
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
