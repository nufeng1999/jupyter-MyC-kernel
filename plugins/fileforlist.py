from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import re
import os
from shutil import copyfile,move
class MyFileforlist(IStag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return 'MyFileforlist'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyFileforlist'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDSptag(self) -> List[str]:
        return ['fileforlist','savetoforlist']
    def setKernelobj(self,obj):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_ISpCodescanning(self,key, value,magics,line) -> str:
        # return self.filehander(self,key, value,magics,line)
        try:
            ##获取 list 值
            list=self.kobj.get_magicsbykey(magics,'filelist')
            if len(list)<1:return ''
            newval=value
            self.kobj.addkey2dict(magics,'fileforlist')
            for li in list:
                ##查找替换$list
                newval=value.replace('$fnlist',li.strip()) 
                ##self.kobj._logln(newval)
                if len(newval)>0:
                    magics[key] += [newval[re.search(r'[^/]',newval).start():]]
                else:
                    magics[key] +=['newfile']
        except Exception as e:
            self.kobj._logln(str(e),2)
        return ''
    ##在代码预处理前扫描代码时调用    
    def on_Codescanning(self,magics,code)->Tuple[bool,str]:
        pass
        return False,code
    ##生成文件时调用
    def on_before_buildfile(self,code,magics)->Tuple[bool,str]:
        return False,''
    def on_after_buildfile(self,returncode,srcfile,magics)->bool:
        # self.kobj._log('on_after_buildfile  file\n',2)
        if len(self.kobj.addkey2dict(magics,'fileforlist'))>0:
            # self.kobj._log("srcfile:"+srcfile+"\n")
            newsrcfilename = self._fileshander(self,magics['fileforlist'],srcfile,magics)
            magics['codefilename']=newsrcfilename
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
        magics['fileforlist']=[]
        return False
    def filehander(self,key, value,magics,line):
        self.kobj._write_to_stdout(value+"\n")
        if len(value)>0:
            magics[str(key)] += [value[re.search(r'[^/]',value).start():]]
        else:
            magics[str(key)] +=['newfile']
        return ''
    def _fileshander(self,files:List,srcfilename,magics)->str:
        index=-1
        fristfile=srcfilename
        try:
            for newsrcfilename in files:
                index=index+1
                newsrcfilename = os.path.join(os.path.abspath(''),newsrcfilename)
                if os.path.exists(newsrcfilename):
                    if magics!=None and len(self.kobj.addkey2dict(magics,'overwritefile'))<1:
                        newsrcfilename +=(".new"+self.kobj.language_info['file_extension'])
                if not os.path.exists(os.path.dirname(newsrcfilename)) :
                    os.makedirs(os.path.dirname(newsrcfilename))
                if index==0:
                    move(srcfilename,newsrcfilename)
                    fristfile=newsrcfilename
                    files[0]=newsrcfilename
                else:
                    self.kobj._log("copy to :"+newsrcfilename+"\n")
                    copyfile(fristfile,newsrcfilename)
        except Exception as e:
                self.kobj._log(str(e),2)
        return files[0]
