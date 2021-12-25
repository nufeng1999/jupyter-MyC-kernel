## %file:src/MyMDDFile.py
from typing import Dict, Tuple, Sequence,List
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
from jupyter_MyC_kernel.kernel import CKernel
import re
import os
from shutil import copyfile,move
class MyMDDFile(IDtag):
    kobj=None
    def getName(self) -> str:
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        
        return 'MyMDDFile'
    def getAuthor(self) -> str:
        return 'Author'
    def getIntroduction(self) -> str:
        return 'MyMDDFile'
    def getPriority(self)->int:
        return 0
    def getExcludeID(self)->List[str]:
        return []
    def getIDDpbegintag(self) -> List[str]:
        return ['##mdf:','//mdf:']
    def getIDDpendtag(self) -> List[str]:
        return ['##mdfend','//mdfend']
    def setKernelobj(self,obj:CKernel):
        self.kobj=obj
        # self.kobj._write_to_stdout("setKernelobj setKernelobj setKernelobj\n")
        return
    def on_shutdown(self, restart):
        return
    def on_IDpReorgCode(self,magics,line) -> str:
        ## 记录mdf:与mdfend之间的内容，并保存到文件中
        ## self.kobj._write_to_stdout(line+"记录mdf on_IDpReorgCode\n")
        ##  self.addkey2dict(magics,'dartcmd')
        return self.recodemdf(self,magics,line)
        ## return ''
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
   ##
    mdcontent=''
    bmdf=False
    linecount=-1
    mdfname=''
    def _is_mdf_begin(self,line):
        if line==None or line=='':return ''
        lh=line.lstrip()[:6]
        if lh.lower() in self.getIDDpbegintag(self):
            self.mdfname=line[6:]
            pass
            ##line.lstrip().startswith('/*')
            self.mdcontent=''
            self.linecount=-1
            self.bmdf=True
            return True
        return False
    def _is_mdf_end(self,line):
        lh=line.lstrip()[:8]
        if lh.lower() in self.getIDDpendtag(self):
            pass
            ##line.lstrip().startswith('/*')
            self.bmdf=False
            return True
        return False

    def recodemdf(self,magics,line):
        try:
            ## self.kobj._logln(line+"\n")
            if not self.bmdf:
                ## 开始标签
                istb=self._is_mdf_begin(self,line)
                if istb: 
                    self.linecount+=1
                    ## self.bmdf=True
                    ## if len(line.strip())>5:
                        ## iste=self._is_mdf_end(self,line)
                        ## if iste:self.bmdf=False
                    return ''
            ## 结束标签
            iste=self._is_mdf_end(self,line)
            if iste:
                ## 将mdcontent内存保存到文件中
                ## self.kobj._logln(self.mdcontent)
                if len(self.mdfname)>0:
                    md_file=self.kobj.create_codetemp_file(magics,self.mdcontent,suffix='.md')
                    newmdfilename = os.path.join(os.path.abspath(''),self.mdfname)
                    if not os.path.exists(os.path.dirname(newmdfilename)) :
                        os.makedirs(os.path.dirname(newmdfilename))
                    ## mdfname=md_file.name
                    move(md_file.name,newmdfilename)
                    self.kobj._logln(newmdfilename+" generated successfully.")
                return ''
            if self.bmdf:
                orgline=line
                if line.lstrip().startswith('//') or line.lstrip().startswith('##'):
                    line=line[2:]
                if line.lstrip().startswith('#```'):
                    line='```'

                ## 记录标签内的内容
                self.mdcontent+=line+'  \n'
                line=orgline
        except Exception as e:
            self.kobj._logln(str(e),3)
        return line
