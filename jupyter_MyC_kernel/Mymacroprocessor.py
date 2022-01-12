import re
import os,sys
class Mymacroprocessor():
    def __init__(self, *args, **kwargs):
        self.macrologiclines=[]
        self.origcontents=[]
        self.iflables=[
            'if',
            'ifdef',
            'ifndef'
        ]
        self.ellables=[
            'elif',
            'else'
        ]
        self.alldefine={}
        self.indentchar='    '
    def reset(self):
        self.macrologiclines=[]
        self.origcontents=[]
        self.alldefine={}
    def macrorepalce(self,code):
        for key,val in self.alldefine.items():
            # print(key+":"+val)
            if val=='':continue
            if (r"(" in val):
                # print(val)
                code=self.interchange_s(r'.*\(',key,val,code)
                continue
            if (r"[" in val):
                # print(val)
                code=self.interchange_s(r'.*\[',key,val,code)
                continue
            if (r"{" in val):
                # print(val)
                code=self.interchange_s(r'.*\{',key,val,code)
                continue
            pattern = re.compile(key)
            code=re.sub(pattern, val, code)
            # code=code.replace(key,val)
        return code
    def adddefine(self,key,val):
        if not self.alldefine.__contains__(key):
            ##添加 key相关回调函数
            d={key:val}
            self.alldefine.update(d)
        else:
            self.alldefine[key]=val
    def undef(self,key):
        res=None
        if self.alldefine.__contains__(key):
            res=self.alldefine.pop(key)
        return res
    def get_realstatement(self,line,type):
        s=''
        if type==0:
            s=''
            _G = globals()
        elif type==1:
            s=''
        elif type==2:
            s=''
        return s
    def isifdef(self,line):
        line=self.movtags(line)
        if line.lstrip().startswith('ifdef'): 
            return True
        return False
    def isifndef(self,line):
        line=self.movtags(line)
        if line.lstrip().startswith('ifndef'): 
            return True
        return False
    def isdefined(self,line):
        line=self.movtags(line)
        if 'defined ' in line.lstrip(): 
            return True
        return False
    def isdefine(self,line):
        line=self.movtags(line)
        if 'define ' in line.lstrip(): 
            return True
        return False
    def isundef(self,line):
        line=self.movtags(line)
        if 'undef ' in line.lstrip(): 
            return True
        return False
    def isendif(self,line):
        line=self.movtags(line)
        if line.lstrip().startswith('endif'): 
            return True
        return False
    def get_indentunit(self,line):
        unit=4
        line=self.movtags(line)
        if line.lstrip().startswith('indentunit'): 
            li=line.split()
            if len(li)<2:return unit
            unit=int(li[1].strip())
            self.indentchar=' '*unit
        return unit
    def movtags(self,line:str):
        if line==None or len(line)<1: return line
        return line.replace("#%", "",1).replace("//#", "",1)
    def ismacrostatement(self,line:str):
        if (line.lstrip().startswith('#%') or
            line.lstrip().startswith('//#')):
            return True
        return False
    def ismif_begin(self,line):
        bret=False
        line=self.movtags(line)
        # map(lambda lable: (if line.lstrip().startswith(lable):return True)  ,self.iflables)
        for lable in self.iflables:
            if line.lstrip().startswith(lable):
                return True
        return False
    def iselmacro(self,line):
        bret=False
        line=self.movtags(line)
        for lable in self.ellables:
            if line.lstrip().startswith(lable):
                return True
        return False
    def ismif_end(self,line):
        bret=False
        line=self.movtags(line)
        if line.lstrip().startswith('endif'):
            bret=True
        return bret
    def addcode2macrologiclines(self,lmline:str):
        self.macrologiclines.append(
            {
                'content':lmline,
                'includeline':None
            }
        )
    def add2macrologiclines(self,lmline:str,includeline=None):
        incline=includeline
        if includeline!=None:
            incline=includeline.copy()
        self.macrologiclines.append(
            {
                'content':lmline,
                'includeline':incline
            }
        )
    def add2origcontents(self,line:str,need=False):
        if self.ismacrostatement(line):
            line="## "
            need=False
        self.origcontents.append(
            {
                'line':line,
                'need':need
            }
        )
    def getstartspace(self,line:str):
        pattern = re.compile(r'\S')
        spacechar=' '
        spacecount=0
        if len(line)>0 :
            m = pattern.search(line)
            if m!=None:
                spacecount=m.start(0)
            else:
                spacecount=len(line)
        if spacecount<1:return ''
        return spacechar*spacecount
    def convert_ifndef(self,line:str):
        line=self.movtags(line)
        ret=''
        varname=''
        if line.lstrip().startswith('ifndef'):
            li=line.split()
            if len(li)<2:return ret
            varname=li[1].strip()
            varname=varname.replace(":","")
            ret=self.getstartspace(line)+'if not self._isdefined("{0}"):'.format(varname)
        return ret
    def convert_ifdef(self,line:str):
        line=self.movtags(line)
        ret=''
        varname=''
        if line.lstrip().startswith('ifdef'):
            li=line.split()
            if len(li)<2:return ret
            varname=li[1].strip()
            varname=varname.replace(":","")
            ret=self.getstartspace(line)+'if self._isdefined("{0}"):'.format(varname)
        return ret
    def convert_defined(self,line:str):
        line=self.movtags(line)
        ret=''
        varname=''
        if ' defined ' in line.lstrip():
            li=line.split()
            if len(li)<3:return ret
            varname=li[2].strip()
            varname=varname.replace(":","")
            ret= ' self._isdefined("{0}"): '.format(varname)
            ret=line.replace(' defined ', ret)
            index=ret.find(":")
            if index >0:
                ret=ret[:index+1]
        return ret
    def convert_define(self,line:str):
        realstatement=''
        line=self.movtags(line)
        if line.lstrip().startswith('define '):
            li=line.split()
            if len(li)<2:
                realstatement="## "
            if len(li)==2:
                realstatement=self.getstartspace(line)+"self.adddefine('"+li[1].strip()+"','')"
            if len(li)>2:
                li=line.split(' ',2)
                realstatement=self.getstartspace(line)+"self.adddefine('"+li[1].strip()+"','"+li[2].strip()+"')"
        return realstatement
    def convert_undef(self,line:str):
        realstatement=''
        line=self.movtags(line)
        if line.lstrip().startswith('undef '):
            li=line.split()
            if len(li)<2:
                realstatement="## "
            else:
                realstatement=self.getstartspace(line)+"self.undef('"+li[1].strip()+"')"
        return realstatement
    def convert_endif(self,line:str):
        self.realstatement=''
        line=self.movtags(line)
        if line.lstrip().startswith('endif'): 
            realstatement=self.getstartspace(line)+"## "
        return realstatement
    def _isdefined(self,varname:str):
        return self.alldefine.__contains__(varname)
    def chgreject(self,origcontents,llnum):
        for num in llnum:
            self.origcontents[num]['need']=True
    def generate_code(self,macrologiclines):
        contents=''
        for lm in self.macrologiclines:
            line=lm["content"]
            if self.isifdef(line):  
                line=self.convert_ifdef(line)
                contents+=line+'\n'
                continue
            if self.isundef(line):  
                line=self.convert_undef(line)
                contents+=line+'\n'
                continue
            if self.isdefined(line):
                line=self.convert_defined(line)
                contents+=line+'\n'
                continue
            if self.isifndef(line): 
                line=self.convert_ifndef(line)
                contents+=line+'\n'
                continue
            if self.isdefine(line): 
                line=self.convert_define(line)
                contents+=line+'\n'
                continue
            if self.isendif(line): 
                line=self.convert_endif(line)
                contents+=line+'\n'
                continue
            # print("原始："+lm["content"])
            contents+=self.movtags(lm["content"])+"\n"
        return contents
    def exec_mcode(self,mcode):
        c = compile(mcode,'','exec')
        exec(c) 
        # ,globals(),locals())
    def macro_proc(self,code):
        lmline=''
        includeline=[]
        index=0
        nestlevel=0
        pattern = re.compile(r'\S')
        spacechar=' '
        for line in code.splitlines():
            need=True
            mline=''
            if self.ismacrostatement(line):
                self.get_indentunit(line)
                line=self.movtags(line)
                if line.lstrip().startswith('indentunit'): 
                    self.addcode2macrologiclines("## ")
                    self.add2origcontents("## ")
                    index+=1
                    continue
                mline=line
                if self.ismif_begin(mline):
                    nestlevel+=1
                if self.ismif_end(mline):
                    nestlevel-=1
                self.addcode2macrologiclines(mline)
                self.add2origcontents("## ")
            else:
                self.add2origcontents(line)
                # spaces=self.getstartspace(line)
                mline="#%self.chgreject(self.origcontents,["+str(index)+"])"
                if nestlevel>0:
                    mline=self.indentchar*nestlevel+mline
                self.addcode2macrologiclines(mline)
            index+=1
        #
        #
    def generate_newcontents(self,origcontents):
        contents=''
        for origline in self.origcontents:
            if not origline['need']:
                continue
            line=origline['line']
            if line.strip()=='':
                continue
            contents+=line+'\n'
        contents=self.macrorepalce(contents)
        return contents 
    def pymprocessor(self,code:str)->str:
        self.reset()
        self.macro_proc(code)
        # print(str(self.macrologiclines))
        # print(str(self.origcontents))
        lcode=self.generate_code(self.macrologiclines)
        # return lcode
        # print(lcode)
        self.exec_mcode(lcode)
        # print(str(self.origcontents))
        newcode=self.generate_newcontents(self.origcontents)
        # print(newcode)
        return newcode
    def pyfmprocessor(self,filename:str):
        if not os.path.exists(filename):
            return ''
        newdata=''
        with open(os.path.join(os.path.abspath(''),filename), 'r',encoding="UTF-8") as f:
            data = f.read()
            newdata=self.pymprocessor(data)
        return newdata
    def interchange_s(self,findstr,orgi,repl,content):
        try:
            pattern_s = re.compile(findstr)
            search_os=re.search(pattern_s,orgi)
            search_ns=re.search(pattern_s,repl)
            s_os=search_os.group(0)
            s_ns=search_ns.group(0)
            # print(s_os)
            # print(repr(s_ns))
            # l_os=search_os.start()
            # l_ns=search_ns.start()
            newcontent=''
            pattern =re.compile(s_os[:-1])
            newcontent=re.sub(pattern, s_ns[:-1], content)
            return newcontent
        except Exception as e:
            print(e)
        return content
# if __name__=="__main__":
#     filename=''
#     if len(sys.argv)>1:
#         filename=sys.argv[0]
#     else:
#         reurn
#     pyp=Mymacroprocessor()
#     newdata=pyp.pyfmprocessor(filename)
#     print(newdata)
