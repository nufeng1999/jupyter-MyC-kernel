from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import re
class MyFile(IStag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return 'MyFile'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyFile'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDSptag(self) -> List[str]:
        return ['file']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        # return self.filehander(self,key, value,magics,line)
        try:
            self.kobj.addkey2dict(magics,'file')
            if len(value)>0:
                magics[key] += [value[re.search(r'[^/]',value).start():]]
            else:
                magics[key] +=['newfile']
        except Exception as e:
            self.kobj._log(str(e),2)
        return ''
    def on_before_buildfile(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_buildfile(self,returncode,srcfile,magics)->bool:
        # self.kobj._log('on_after_buildfile  file\n',2)
        if len(self.kobj.addkey2dict(magics,'file'))>0:
                self.kobj._log("srcfile:"+srcfile+"\n")
                newsrcfilename = self.kobj._fileshander(magics['file'],srcfile,magics)
                self.kobj._log("file "+ newsrcfilename +" created successfully\n")
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
    def filehander(self,key, value,magics,line):
        self.kobj._write_to_stdout(value+"\n")
        if len(value)>0:
            magics[str(key)] += [value[re.search(r'[^/]',value).start():]]
        else:
            magics[str(key)] +=['newfile']
        return ''
