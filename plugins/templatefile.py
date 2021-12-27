import typing as t
from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import os
class MyTemplatefile(IStag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        
        return 'MyTemplatefile'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyTemplatefile'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDSptag(self) -> List[str]:
        return ['templatefile']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        # self.kobj._write_to_stdout(line+" on_ISpCodescanning\n")
        self.kobj.addkey2dict(magics,'templatefile')
        return self.templatehander(self,key, value,magics,line)
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
    def templatehander(self,key, value,magics,line):
        # self.kobj._write_to_stdout(value+"\n")
        newline=line
        index1=line.find('//%')
        if len(value)>0:
            magics[key] =value.split(" ",1)
        else:
            magics[key] =None
            return ''
        templatefile=magics['templatefile'][0]
        if len(magics['templatefile'])>1:
            argsstr=magics['templatefile'][1]
            templateargsdict=self.kobj.resolving_eqval2dict(argsstr)
        else:
            templateargsdict=None
        if len(magics['templatefile'])>0:
            newline=self.readtemplatefile(self,templatefile,index1,templateargsdict)
        return newline + '\n'
    def readtemplatefile(self,filename,spacecount=0,*args: t.Any, **kwargs: t.Any):
        filecode=''
        newfilecode=''
        codelist1=None
        filenm=os.path.join(os.path.abspath(''),filename);
        if not os.path.exists(filenm):
            return filecode;
        template = self.jinja2_env.get_template(filenm)
        filecode=template.render(*args,**kwargs)
        for line in filecode.splitlines():
            if len(line)>0:
                for t in line:
                    newfilecode+=' '*spacecount + t+'\n'
        return newfilecode
