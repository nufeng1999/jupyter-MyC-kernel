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
    @abstractmethod
    def on_before_buildfile(self,code,magics)->Tuple[bool,str]:
        pass
    @abstractmethod
    def on_after_buildfile(self,returncode,srcfile,magics)->bool:
        pass
    @abstractmethod
    def on_shutdown(self, restart):
        pass
    @abstractmethod
    def on_before_compile(self,code,magics)->Tuple[bool,str]:
        pass
    @abstractmethod
    def on_after_compile(self,returncode,binfile,magics)->bool:
        pass
    @abstractmethod
    def on_before_exec(self,code,magics)->Tuple[bool,str]:
        pass
    @abstractmethod
    def on_after_exec(self,returncode,execfile,magics)->bool:
        pass
    @abstractmethod
    def on_after_completion(self,returncode,execfile,magics)->bool:
        pass
class IStag(ITag):
    @abstractmethod
    def getIDSptag(self) -> List[str]:
        pass
    @abstractmethod
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        pass
class IDtag(ITag):
    @abstractmethod
    def getIDDpbegintag(self) -> List[str]:
        pass
    @abstractmethod
    def getIDDpendtag(self) -> List[str]:
        pass
    @abstractmethod
    def on_IDpReorgCode(self,line) -> str:
        pass
class IBtag(ITag):
    @abstractmethod
    def getIDBptag(self) -> List[str]:
        pass
    @abstractmethod
    def on_IBpCodescanning(self,magics,line) -> str:
        pass
