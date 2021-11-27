from typing import Dict, Tuple, Sequence
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
    @abstractmethod
    def setKernelobj(self,kobj,magics):
        pass
    @abstractmethod
    def on_shutdown(self, restart):
        pass
    @abstractmethod
    def on_before_compile(self,code)->Tuple[bool,str]:
        pass
    @abstractmethod
    def on_after_compile(self,returncode,binfile)->bool:
        pass
    @abstractmethod
    def on_before_exec(self,code)->Tuple[bool,str]:
        pass
    @abstractmethod
    def on_after_exec(self,returncode,execfile)->bool:
        pass
class IStag(ITag):
    @abstractmethod
    def getIDSptag(self) -> str:
        pass
    @abstractmethod
    def on_ISpCodescanning(self,key,line) -> str:
        pass
class IDtag(ITag):
    @abstractmethod
    def getIDDpbegintag(self) -> str:
        pass
    @abstractmethod
    def getIDDpendtag(self) -> str:
        pass
    @abstractmethod
    def on_IDpReorgCode(self,line) -> str:
        pass
class IBtag(ITag):
    @abstractmethod
    def getIDBptag(self) -> str:
        pass
    @abstractmethod
    def on_IBpCodescanning(self,key,line) -> str:
        pass
