##
from typing import Dict, Tuple, Sequence,List, Set
from abc import ABCMeta, abstractmethod
class IMyKernel():
    @abstractmethod
    def get_runfiletype(self)->str:
        pass
    @abstractmethod
    def get_kernelinfo(self)->str:
        pass
    @abstractmethod
    def get_main_head(self)->str:
        pass
    @abstractmethod
    def get_main_foot(self)->str:
        pass
    
    @abstractmethod
    def get_mymagics(self)->object:
        pass
    @abstractmethod
    def set_mymagics(self,object):
        pass
    
    @abstractmethod
    def get_execution_count(self):
        pass
    @abstractmethod
    def rawinput(self):
        pass
    @abstractmethod
    def sendresponse(self,contents,name='stdout',mimetype=None):
        pass
    @abstractmethod
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=True)->Dict:
        pass
    @abstractmethod
    def do_shutdown(self, restart):
        pass
    @abstractmethod
    def do_runcode(self,return_code,file_name,
                    magics,code, 
                    silent, store_history=True,
                    user_expressions=None, 
                    allow_stdin=True)->Dict:
        pass
    @abstractmethod
    def do_compile_code(self,return_code,file_name,
                    magics,code, silent, store_history=True,
                    user_expressions=None, 
                    allow_stdin=True)->Tuple[bool,Dict,Dict, str,str,str]:
        pass
    @abstractmethod
    def do_create_codefile(self,magics,code, 
                    silent, store_history=True,
                    user_expressions=None, 
                    allow_stdin=True)->Tuple[bool,Dict,Dict, str,str,str]:
        pass
    @abstractmethod
    def do_preexecute(self,code,magics,
                silent, store_history=True,
                user_expressions=None, 
                allow_stdin=False)->Tuple[bool,Dict,Dict,str]:
        pass
