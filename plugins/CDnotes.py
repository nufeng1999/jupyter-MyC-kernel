from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
from jupyter_MyC_kernel.kernel import CKernel
class MyCDnotes(IDtag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        
        return 'MyCDnotes'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyCDnotes'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDDpbegintag(self) -> List[str]:
        return ['/*']
    def getIDDpendtag(self) -> List[str]:
        return ['*/']
    def setKernelobj(self,obj:CKernel):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_IDpReorgCode(self,line) -> str:
        # self.kobj._write_to_stdout(line+" hon_IDpReorgCode\n")
        #  self.addkey2dict(magics,'dartcmd')
        return self.cleancqm(self,line)
        # return ''
    ##在代码预处理前扫描代码时调用     
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
    def _is_cqm_begin(self,line):
        if line==None or line=='':return ''
        return line.lstrip().startswith('/*')
    def _is_cqm_end(self,line):
        if line==None or line=='':return ''
        return line.rstrip().endswith('*/')
    iscqm=False
    def cleancqm(self,line):
        # self.kobj._write_to_stdout(line+"\n")
        if not self.iscqm:
            istb=self._is_cqm_begin(self,line)
            if istb: 
                self.iscqm=True
                if len(line.strip())>5:
                    iste=self._is_cqm_end(self,line)
                    if iste:self.iscqm=False
                return ''
        iste=self._is_cqm_end(self,line)
        if iste:
            self.iscqm=False
            return ''
        line= "" if self.iscqm else line
        return line
