## %file:src/shellcommand.py
from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import os
class MyShellcommand(IStag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        
        return 'MyShellcommand'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyShellcommand'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDSptag(self) -> List[str]:
        return ['command']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        # self.kobj._write_to_stdout(line+" on_ISpCodescanning\n")
        self.kobj.addkey2dict(magics,'command')
        return self.commandhander(self,key, value,magics,line)
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
    def commandhander(self,key, value,magics,line):
        # self.kobj._write_to_stdout(value+"\n")
        try:
            magics['command'] = value.strip()
            if len(magics['command'])>0:
                env=self.kobj.get_magicsSvalue(magics,'env')
                if len(env)<1:env=None
                self.kobj.do_shell_command(magics['command'],env=env,magics=magics)
        except Exception as e:
            self.kobj._logln("commandhander  "+str(e))
        return ''

    
