from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import os
class MyDartcommand(IStag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return 'MyDartcommand'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyDartcommand'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDSptag(self) -> List[str]:
        return ['dartcmd']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        # self.kobj._write_to_stdout(line+" on_ISpCodescanning\n")
        self.kobj.addkey2dict(magics,'dartcmd')
        return self.commandhander(self,key, value,magics,line)
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
    def commandhander(self,key, value,magics,line):
        # self.kobj._write_to_stdout(value+"\n")
        for flag in value.split():
            magics[key] += [flag]
        if len(magics['dartcmd'])>0:
            self.kobj.do_dart_command(magics['dartcmd'],magics=magics)
        return ''
