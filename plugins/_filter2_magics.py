#_filter2_magics
## %file:../src/_filter2_magics.py
##########################
from math import exp
from queue import Queue
from threading import Thread
    
from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF
from jinja2 import Environment, PackageLoader, select_autoescape,Template
from abc import ABCMeta, abstractmethod
from typing import List, Dict, Tuple, Sequence
from shutil import copyfile
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag
import pexpect
import signal
import typing 
import typing as t
import re
import signal
import subprocess
import tempfile
import os
import sys
import traceback
import os.path as path
import codecs
import time
import importlib
import importlib.util
import inspect

###############################
class Magics():
    plugins=None
    ISplugins=None
    IDplugins=None
    IBplugins=None
    kobj=None
    
    plugins=[ISplugins,IDplugins,IBplugins]
    def __init__(self,kobj,plugins:List,ICodePreprocs):
        self.kobj=kobj
        self.plugins=plugins
        self.ICodePreprocs=ICodePreprocs
        self.ISplugins=self.plugins[0]
        self.IDplugins=self.plugins[1]
        self.IBplugins=self.plugins[2]
        self.magics = {
            ##magics_define
              ##
                '_sline':{
                  'package':'0',
                  'public':'0'
                },
                '_slinef':{
                  'package':[],
                  'public':[]
                },
                '_bt':{
                'repllistpid':'',
                'runinterm':'',
                'replcmdmode':'',
                'replprompt':''
                },
                '_st':{
                'ldflags':[],
                'cflags':[],
                'coptions':[],
                'joptions':[],
                'runmode':[],
                'replsetip':[],
                'replchildpid':"0",
                'pidcmd':[],
                'term':[],
                'fileencode':'UTF-8',
                'outencode':'UTF-8',
                'outputtype':'text/plain',
                'log':[],
                'loadurl':[],
                'runprg':[],
                'runprgargs':[],
                'args':[]
                },
                '_dt':{},
                '_btf':{
                'repllistpid':[self.kobj.repl_listpid],
                'runinterm':[],
                'replcmdmode':[],
                'replprompt':[]
                },
                '_stf':{
                'ldflags':[],
                'cflags':[],
                'coptions':[],
                'joptions':[],
                'runmode':[],
                'replsetip':[],
                'replchildpid':[],
                'pidcmd':[],
                'term':[],
                'fileencode':[],
                'outencode':[],
                'outputtype':[],
                'log':[],
                'loadurl':[],
                'runprg':[],
                'runprgargs':[],
                'args':[]
                },
                '_dtf':{},
                'codefilename':'',
                'classname':'',
                'dlrun': [],
                'package': '',
                'main': '',
                'pubclass': '',
                'pid': []

            }
        self.init_filter(self.magics)
    def _is_specialID(self,line):
        if line.strip().startswith('##%') or line.strip().startswith('//%'):
            return True
        return False

    def addkey2dict(self,magics:Dict,key:str):
        if not magics.__contains__(key):
            d={key:[]}
            magics.update(d)
        return magics[key]
    
##内核公共代码部分2
    def get_magicsSvalue(self,magics:Dict,key:str):
        return self.addmagicsSkey(magics,key)
    def get_magicsBvalue(self,magics:Dict,key:str):
        return self.addmagicsBkey(magics,key)
    def get_magicsbykey(self,magics:Dict,key:str):
        return self.addkey2dict(magics,key)
    
    def addmagicsSLkey(self,magics:Dict,key:str,value=None,func=None):
        return self.addmagicskey2(magics=magics,key=key,type='_sline',func=func,value=value)
    def addmagicsSkey(self,magics:Dict,key:str,func=None):
        return self.addmagicskey2(magics=magics,key=key,type='_st',func=func)
    def addmagicsBkey(self,magics:Dict,key:str,value=None,func=None):
        return self.addmagicskey2(magics=magics,key=key,type='_bt',func=func,value=value)
    
    def addmagicskey2(self,magics:Dict,key:str,type:str,func=None,value=None):
        if not magics[type].__contains__(key):
            ##添加 key
            d={key:[]}
            if value!=None:
                d={key:value}
            magics[type].update(d)
        if not magics[type+'f'].__contains__(key):
            ##添加 key相关回调函数
            d={key:[]}
            magics[type+'f'].update(d)
        if func!=None:
            magics[type+'f'][key]+=[func]
        return magics[type][key]
    def addkey2dict(self,magics:Dict,key:str,type:str=None):
        if not magics.__contains__(key):
            d={key:[]}
            if type!=None and type=="dict":
                d={key:{}}
            magics.update(d)
        return magics[key]

##特殊行处理
    def slfn_package(self,key,magics,line):
        qline=self.kobj.replacemany(line,'; ', ';')
        qline=self.kobj.replacemany(qline,' ;', ';')
        qline= qline[:len(qline)-1]
        li=qline.strip().split()
        if(len(li)>1):
            magics['package'] = li[1].strip()
        return ''
    def slfn_public(self,key,magics,line):
        qline = self.kobj.replacemany(line, 's  ', 's ')
        li = qline.strip().split()
        if(len(li) > 2 and li[1].strip().lower() == 'class'):
            magics[li[0].strip()] = li[1].strip()
            pubclass = li[2].strip()
            if pubclass.strip().endswith('{'):
                pubclass = pubclass[:len(pubclass)-1]
            magics['pubclass'] = pubclass
        return ''

##关键字相关函数
    def kfn_ldflags(self,key,value,magics,line):
        for flag in value.split():
            magics['_st'][key] += [flag]
        return ''
    def kfn_cflags(self,key,value,magics,line):
        for flag in value.split():
            magics['_st'][key] += [flag]
        return ''
    def kfn_coptions(self,key,value,magics,line):
        for flag in value.split():
            magics['_st'][key] += [flag]
        return ''
    def kfn_joptions(self,key,value,magics,line):
        for flag in value.split():
            magics['_st'][key] += [flag]
        return ''
    def kfn_runmode(self,key,value,magics,line):
        if len(value)>0:
            magics['_st'][key] = value[re.search(r'[^/]',value).start():]
        else:
            magics['_st'][key] ='real'
        return ''
    def kfn_replsetip(self,key,value,magics,line):
        magics['_st']['replsetip'] = value
        return ''
    def kfn_replchildpid(self,key,value,magics,line):
        magics['_st']['replchildpid'] = value
        return ''
    def kfn_pidcmd(self,key,value,magics,line):
        magics['_st']['pidcmd'] = [value]
        if len(magics['_st']['pidcmd'])>0:
            findObj= value.split(",",1)
        if findObj and len(findObj)>1:
            pid=findObj[0]
            cmd=findObj[1]
            self.kobj.send_cmd(pid=pid,cmd=cmd)
        return ''
    def kfn_term(self,key,value,magics,line):
        magics['_st']['term']=[]
        for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
            magics['_st']['term'] += [argument.strip('"')]
        return ''
    def kfn_fileencode(self,key,value,magics,line):
        magics['_st']['fileencode']=value.strip()
        return ''
    def kfn_outencode(self,key,value,magics,line):
        magics['_st']['outencode']=value.strip()
        return ''
    def kfn_outputtype(self,key,value,magics,line):
        magics['_st']['outputtype']=value.strip()
        return ''
    def kfn_log(self,key,value,magics,line):
        magics['_st']['log'] = value.strip()
        self.kobj._loglevel= value.strip()
        return ''
    def kfn_loadurl(self,key,value,magics,line):
        url=value
        if(len(url)>0):
            line=self.kobj.loadurl(url)
            return line
        return ''
    def kfn_runprg(self,key,value,magics,line):
        magics['_st']['runprg'] = value
        return ''
    def kfn_runprgargs(self,key,value,magics,line):
        # self.kobj._logln(value)
        for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
            magics['_st']['runprgargs'] += [argument.strip('"')]
        return ''
    def kfn_args(self,key,value,magics,line):
        for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
            magics['_st']['args'] += [argument.strip('"')]
        return ''
    def init_filter(self,magics):
        self.addmagicsSLkey(magics,'package','0',self.slfn_package)
        self.addmagicsSLkey(magics,'public','0',self.slfn_public)
        self.addmagicsSkey(magics,'ldflags',self.kfn_ldflags)
        self.addmagicsSkey(magics,'cflags',self.kfn_cflags)
        self.addmagicsSkey(magics,'coptions',self.kfn_coptions)
        self.addmagicsSkey(magics,'joptions',self.kfn_joptions)
        self.addmagicsSkey(magics,'runmode',self.kfn_runmode)
        self.addmagicsSkey(magics,'replsetip',self.kfn_replsetip)
        self.addmagicsSkey(magics,'replchildpid',self.kfn_replchildpid)
        self.addmagicsSkey(magics,'pidcmd',self.kfn_pidcmd)
        self.addmagicsSkey(magics,'term',self.kfn_term)
        self.addmagicsSkey(magics,'outputtype',self.kfn_outputtype)
        self.addmagicsSkey(magics,'fileencode',self.kfn_fileencode)
        self.addmagicsSkey(magics,'outencode',self.kfn_outencode)
        self.addmagicsSkey(magics,'log',self.kfn_log)
        self.addmagicsSkey(magics,'loadurl',self.kfn_loadurl)
        self.addmagicsSkey(magics,'runprg',self.kfn_runprg)
        self.addmagicsSkey(magics,'runprgargs',self.kfn_runprgargs)
        self.addmagicsSkey(magics,'args',self.kfn_args)
    def reset_filter(self):
        self.magics = {
            ##magics_define
              ##
                '_sline':{
                  'package':'0',
                  'public':'0'
                },
                '_slinef':{
                  'package':[],
                  'public':[]
                },
                '_bt':{
                'repllistpid':'',
                'runinterm':'',
                'replcmdmode':'',
                'replprompt':''
                },
                '_st':{
                'ldflags':[],
                'cflags':[],
                'coptions':[],
                'joptions':[],
                'runmode':[],
                'replsetip':[],
                'replchildpid':"0",
                'pidcmd':[],
                'term':[],
                'fileencode':'UTF-8',
                'outencode':'UTF-8',
                'outputtype':'text/plain',
                'log':[],
                'loadurl':[],
                'runprg':[],
                'runprgargs':[],
                'args':[]
                },
                '_dt':{},
                '_btf':{
                'repllistpid':[self.kobj.repl_listpid],
                'runinterm':[],
                'replcmdmode':[],
                'replprompt':[]
                },
                '_stf':{
                'ldflags':[],
                'cflags':[],
                'coptions':[],
                'joptions':[],
                'runmode':[],
                'replsetip':[],
                'replchildpid':[],
                'pidcmd':[],
                'term':[],
                'fileencode':[],
                'outencode':[],
                'outputtype':[],
                'log':[],
                'loadurl':[],
                'runprg':[],
                'runprgargs':[],
                'args':[]
                },
                '_dtf':{},
                'codefilename':'',
                'classname':'',
                'dlrun': [],
                'package': '',
                'main': '',
                'pubclass': '',
                'pid': []
            }

   ## 特殊行(非标签行)处理
    def call_slproc(self,magics,line)->Tuple[bool,str]:
        type='_sline'
        if len(magics[type])<1:return False,line
        newline=line
        ismatch=False
        try:
            for key,value in magics[type].items():
               ## startswith
                if (len(value)>0 and value.strip()=='0' 
                    and (line.strip().startswith(key))
                    and len(magics[type+'f'][key])>0):
                    ismatch=True
                    for kfunc in magics[type+'f'][key]:
                        newline=kfunc(key,magics,newline)
               ## in
                elif (len(value)>0 and value.strip()=='1' 
                    and (key in line.strip())
                    and len(magics[type+'f'][key])>0):
                    ismatch=True
                    for kfunc in magics[type+'f'][key]:
                        newline=kfunc(key,magics,newline)
               ## endswith
                elif (len(value)>0 and value.strip()=='2' 
                    and (line.strip().endswith(key))
                    and len(magics[type+'f'][key])>0):
                    ismatch=True
                    for kfunc in magics[type+'f'][key]:
                        newline=kfunc(key,magics,newline)
                if ismatch:
                    return ismatch,newline
        except Exception as e:
            self.kobj._logln("call_slproc "+str(e),3)
        finally:pass
        return ismatch,newline
   ## Bool型标签行处理
    def call_btproc(self,magics,line)->bool:
        type='_bt'
        if len(magics[type])<1:return False
        try:
            key= line.strip()[3:]
            if magics[type].__contains__(key):
                magics[type][key]='true'
                if len(magics[type+'f'][key])>0:
                    ##处理关键字相关的函数
                    for kfunc in magics[type+'f'][key]:
                        kfunc(line)
                return True
        except Exception as e:
            self.kobj._logln('call_btproc '+str(e),3)
        finally:pass
        return False
   ## 赋值类型标签行处理
    def call_stproc(self,magics,line,key,value)->str:
        type='_st'
        if len(magics[type])<1:return line
        newline=line
        try:
            if magics[type].__contains__(key):
                if len(magics[type+'f'][key])>0:
                    for kfunc in magics[type+'f'][key]:
                        # self.kobj._logln("call--------"+key)
                        newline=kfunc(key,value,magics,newline)
                return newline
        except Exception as e:
            self.kobj._logln("call_stproc "+str(e),3)
        finally:pass
        return newline

    ##触发接口调用
    def raise_ICodescan(self,magics,code)->Tuple[bool,str]:
        bcancel_exec=False
        bretcancel_exec=False
        newcode=code
        # for pluginlist in self.plugins:
        for pkey,pvalue in self.ICodePreprocs.items():
            # print( pkey +":"+str(len(pvalue))+"\n")
            for pobj in pvalue:
                try:
                    bretcancel_exec,newcode=pobj.on_Codescanning(pobj,magics,newcode)
                    bcancel_exec=bretcancel_exec & bcancel_exec
                    if bcancel_exec:
                        return bcancel_exec,newcode
                except Exception as e:
                    self.kobj._logln(pobj.getName(pobj)+"---"+str(e))
                finally:pass
        return bcancel_exec,newcode
        

    def filter(self, code):
        ##魔法字典
        ## magics={}
        actualCode = ''
        newactualCode = ''
        self.reset_filter()
        self.init_filter(self.magics)
        magics =self.magics
        
       ##扫描源码 进行标签行，特殊行处理
        for line in code.splitlines():
            ##扫描源码每行行
            orgline=line

            if line==None or line.strip()=='': 
                actualCode += line + '\n'
                continue
           ## 特殊行处理
            ismatch,retstr=self.call_slproc(magics,line)
            if ismatch:
                if len(retstr)>0:
                    actualCode += retstr + '\n'
                else:
                    actualCode += line + '\n'
                continue
           ## 标签行处理
            if self._is_specialID(line):
               ## 对Bool型标签进行处理
                if self.call_btproc(magics,line):continue
 
               ## 通知(Bool型插件)进行预处理
                
                ##通知插件进行预处理
                ##preprocessor
                ##通知BOOL型标签插件处理
                ##on_IBpCodescanning
                ##调用BOOL标签接口
                #_filter2_magics_i1
                for pkey,pvalue in self.IBplugins.items():
                    print( pkey +":"+str(len(pvalue))+"\n")
                    for pobj in pvalue:
                        newline=''
                        try:
                            lin=pobj.getIDBptag(pobj)
                            if line.lower().strip()[3:] in lin:
                                newline=pobj.on_IBpCodescanning(pobj,magics,line)
                                if newline=='':continue
                        except Exception as e:
                            self._logln(str(e))
                        finally:pass
                        # if newline!=None and newline!='':
                        #     actualCode += newline + '\n'
                ##

                ##获得BOOL关键字
                ##登记Bool型参数和值

               ## 获得赋值型 关键字和其参数
                findObj= re.search( r':(.*)',line)
                if not findObj or len(findObj.group(0))<2:
                    continue
                key, value = line.strip()[3:].split(":", 1)
                key = key.strip().lower()
               
               ## 对赋值类型标签进行处理
                newline=self.call_stproc(magics,line,key,value)
                if newline!=line and len(newline)>0:
                    actualCode += newline + '\n'
                    continue

               ##通知(赋值型插件)进行预处理
                ##登记参数和值
                ##处理参数和值 ？？？
                ##合并处理结果
                ##调用单标签接口
                #_filter2_magics_i2
                for pkey,pvalue in self.ISplugins.items():
                    for pobj in pvalue:
                        newline=''
                        try:
                            li=pobj.getIDSptag(pobj)
                            if key.lower() in li:
                                newline=pobj.on_ISpCodescanning(pobj,li[0],value,magics,line)
                                if newline=='':continue
                        except Exception as e:
                            pass
                        finally:pass
                        if newline!=None and newline!='':
                            actualCode += newline + '\n'

            else:
                ## keep lines which did not contain magics
                actualCode += line + '\n'
        newactualCode=actualCode

       ##第二次扫描源代码，进行预处理，比如宏标签处理，模板标签处理
        bcancel_exec,newcode=self.raise_ICodescan(magics,newactualCode)
        if not bcancel_exec:
            newactualCode=newcode

       ##第三次扫描源代码，进行代码格式化
            ##扫描源码每行行
            ##清理测试代码 test_begin test_end
            ##清理单行注释 // #
            ##清理多行注释 /* */ ''' """
        #_filter2_magics_pend
        if len(self.addkey2dict(magics,'file'))>0 :
            newactualCode=''
            for line in actualCode.splitlines():
                try:
                    # if len(self.addkey2dict(magics,'test'))<1:
                    line=self.kobj.cleantestcode(line)
                    if line=='':continue
                    ##调用双标签接口
                    line=self.kobj.callIDplugin(line)
                    if line=='':continue
                    if len(self.addkey2dict(magics,'discleannotes'))>0 :continue
                    line=self.kobj.cleandqm(line)
                    if line=='':continue
                    line=self.kobj.cleansqm(line)
                    if line=='':continue
                    if self.kobj.cleannotes(line)=='':
                        continue
                    else:
                        newactualCode += line + '\n'
                except Exception as e:
                    self.kobj._log(str(e),3)

       ##返回 magics, newactualCode
        return magics, newactualCode
