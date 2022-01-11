## %file:src/ptemplate.py
import typing as t
import os
from typing import Dict, Tuple, Sequence,List
from jinja2 import Environment, PackageLoader, select_autoescape,Template

from plugins.ISpecialID import IStag,IDtag,IBtag,ITag,ICodePreproc
class MyPTemplate(ICodePreproc):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        
        return 'MyPTemplate'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyPTemplate'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    isjj2code=False
    def _is_jj2_begin(self,line):
        if line==None or line=='':return ''
        return line.strip().startswith('##jj2_begin') or line.strip().startswith('//jj2_begin')
    def _is_jj2_end(self,line):
        if line==None or line=='':return ''
        return line.strip().startswith('##jj2_end') or line.strip().startswith('//jj2_end')
    jj2code_cache=[]
    jj2code_args={}
    def cleanjj2code_cache(self):
        self.jj2code_cache.clear()
        self.jj2code_args={}
    def addjj2codeline(self,line):
        self.jj2code_cache+=[line]
    def getjj2code(self):
        if len(self.jj2code_cache)<1:return ''
        code=''.join(line+'\n' for line in self.jj2code_cache)
        return code
    def execjj2code_cache(self) -> str:
        code=self.getjj2code(self)
        if code==None or code.strip()=='': return code
        env = Environment()
        template = Template(code)
        # self.process_output('render\n')
        # for key in self.jj2code_args:
            # self.process_output(key+':'+self.jj2code_args[key])
        ret=template.render(self.jj2code_args)
        # self.process_output('ret'+'\n')
        return ret
    def forcejj2code(self,line): 
        if not self.isjj2code:
            istb=self._is_jj2_begin(self,line)
            if istb: 
                self.isjj2code=True
                # self.kobj._logln(line+' .....\n')
                if len(line.strip())>14:
                    argline =line.split(":",1)
                    # self.process_output(line+'\n')
                    if len(argline)>1:
                        argsstr=argline[1]
                        # self.kobj._logln(argsstr+' is argsstr\n')
                        tplargs=self.kobj.resolving_eqval2dict(argsstr)
                        self.jj2code_args.update(tplargs)
                        # self.process_output('jj2code_args.update\n')
                        # for key in self.jj2code_args:
                            # self.process_output(key+':'+self.jj2code_args[key])
                    iste=self._is_jj2_end(self,line)
                    if iste:
                        self.cleanjj2code_cache(self)
                        self.isjj2code=False
                        return ''
                line= ''
        iste=self._is_jj2_end(self,line)
        if iste:
            self.isjj2code=False
            line= ''
            line=self.execjj2code_cache(self)
            self.cleanjj2code_cache(self)
            return line
        if self.isjj2code: self.addjj2codeline(self,line)
        line= "" if self.isjj2code else line
        return line

    ##在代码预处理前扫描代码时调用    
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        ##扫描源码
        actualCode = ''
        for line in code.splitlines():
            ##扫描源码每行行
            orgline=line
            line=self.forcejj2code(self,line)
            actualCode += line + '\n'
        return False,actualCode
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
            templateargsdict=self._filter_dict(argsstr)
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
