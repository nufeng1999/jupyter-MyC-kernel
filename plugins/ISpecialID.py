##接口定义部分
from typing import Dict, Tuple, Sequence,List, Set
from abc import ABCMeta, abstractmethod
class ITag(metaclass=ABCMeta):
    @abstractmethod
    def getName(self) -> str:
        pass
    @abstractmethod
    def getAuthor(self) -> str:
        pass
    @abstractmethod
    def getIntroduction(self) -> str:
        pass
    @abstractmethod
    def getPriority(self)->int:
        pass
    def getExcludeID(self)->List[str]:
        pass
    @abstractmethod
    def setKernelobj(self,kobj):
        pass
##在代码预处理前扫描代码时调用
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        return False,code
##生成文件时调用
    def on_before_buildfile(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_buildfile(self,returncode,srcfile,magics)->bool:
        return False
##内核shutdown时调用
    def on_shutdown(self, restart):
        return False
##编译代码时调用
    def on_before_compile(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_compile(self,returncode,binfile,magics)->bool:
        return False
##执行代码时调用
    def on_before_exec(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_exec(self,returncode,execfile,magics)->bool:
        return False
    def on_after_completion(self,returncode,execfile,magics)->bool:
        return False
class ICodePreproc(ITag):
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        return False,code
class IStag(ITag):
    @abstractmethod
    def getIDSptag(self) -> List[str]:
        pass
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        return line
class IDtag(ITag):
    @abstractmethod
    def getIDDpbegintag(self) -> List[str]:
        pass
    @abstractmethod
    def getIDDpendtag(self) -> List[str]:
        pass
    ##在整理代码时调用双标签接口
    def on_IDpReorgCode(self,magics,line) -> str:
        return line
class IBtag(ITag):
    @abstractmethod
    def getIDBptag(self) -> List[str]:
        pass
    ##在扫描代码时调用
    def on_IBpCodescanning(self,magics,line) -> str:
        return line
