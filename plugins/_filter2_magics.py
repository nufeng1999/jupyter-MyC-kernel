#_filter2_magics
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
                  'bt':{
                    'repllistpid':'',
                    'onlyrunmagics':'',
                    'runinterm':'',
                    'replcmdmode':'',
                    'replprompt':''
                    },
                  'st':{
                    'ldflags':[],
                    'cflags':[],
                    'coptions':[],
                    'joptions':[],
                    'runmode':[],
                    'replsetip':[],
                    'replchildpid':"0",
                    'pidcmd':[],
                    'term':[],
                    'outputtype':'text/plain',
                    'log':[],
                    'loadurl':[],
                    'runprg':[],
                    'runprgargs':[],
                    'args':[]
                    },
                  'dt':{},
                  'btf':{
                    'repllistpid':[self.kobj.repl_listpid],
                    'onlyrunmagics':[],
                    'runinterm':[],
                    'replcmdmode':[],
                    'replprompt':[]
                    },
                  'stf':{
                    'ldflags':[],
                    'cflags':[],
                    'coptions':[],
                    'joptions':[],
                    'runmode':[],
                    'replsetip':[],
                    'replchildpid':[],
                    'pidcmd':[],
                    'term':[],
                    'outputtype':[],
                    'log':[],
                    'loadurl':[],
                    'runprg':[],
                    'runprgargs':[],
                    'args':[]
                    },
                  'dtf':{},
                  'codefilename':'',
                  'classname':'',
                #   'cflags': [],
                #   'ldflags': [],
                #   'term': [],
                  'dlrun': [],
                #   'coptions': [],
                #   'joptions': [],
                  'package': '',
                  'main': '',
                  'pubclass': '',
                #   'runprg': '',
                #   'runprgargs': [],
                #   'log': '',
                #   'repllistpid': [],
                #   'replsetip': "\r\n",
                #   'replchildpid':"0",
                #   'outputtype':'text/plain',
                #   'runmode': [],
                  'pid': [],
                #   'pidcmd': [],
                #   'args': [],
                #   'rungdb': []
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
    def get_magicsSvalue(self,magics:Dict,key:str):
        return self.addmagicsSkey(magics,key)
    def addmagicsSkey(self,magics:Dict,key:str,func=None):
        return self.addmagicskey2(magics=magics,key=key,type='st',func=func)
    def addmagicsBkey(self,magics:Dict,key:str,func=None):
        return self.addmagicskey2(magics=magics,key=key,type='bt',func=func)
    def addmagicskey2(self,magics:Dict,key:str,type:str,func=None):
        if not magics[type].__contains__(key):
            d={key:[]}
            magics[type].update(d)
        if not magics[type+'f'].__contains__(key):
            d={key:[]}
            magics[type+'f'].update(d)
        if func!=None:
            magics[type+'f'][key]+=[func]
        return magics[type][key]
    def kfn_ldflags(self,key,value,magics,line):
        for flag in value.split():
            magics[key] += [flag]
        return ''
    def kfn_cflags(self,key,value,magics,line):
        for flag in value.split():
            magics[key] += [flag]
        return ''
    def kfn_coptions(self,key,value,magics,line):
        for flag in value.split():
            magics[key] += [flag]
        return ''
    def kfn_joptions(self,key,value,magics,line):
        for flag in value.split():
            magics[key] += [flag]
        return ''
    def kfn_runmode(self,key,value,magics,line):
        if len(value)>0:
            magics[key] = value[re.search(r'[^/]',value).start():]
        else:
            magics[key] ='real'
        return ''
    def kfn_replsetip(self,key,value,magics,line):
        magics['replsetip'] = value
        return ''
    def kfn_replchildpid(self,key,value,magics,line):
        magics['replchildpid'] = value
        return ''
    def kfn_pidcmd(self,key,value,magics,line):
        magics['pidcmd'] = [value]
        if len(magics['pidcmd'])>0:
            findObj= value.split(",",1)
        if findObj and len(findObj)>1:
            pid=findObj[0]
            cmd=findObj[1]
            self.kobj.send_cmd(pid=pid,cmd=cmd)
        return ''
    def kfn_term(self,key,value,magics,line):
        magics['term']=[]
        for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
            magics['term'] += [argument.strip('"')]
        return ''
    def kfn_outputtype(self,key,value,magics,line):
        magics[key]=value
        return ''
    def kfn_log(self,key,value,magics,line):
        magics['log'] = value.strip()
        self.kobj._loglevel= value.strip()
        return ''
    def kfn_loadurl(self,key,value,magics,line):
        url=value
        if(len(url)>0):
            line=self.kobj.loadurl(url)
            return line
        return ''
    def kfn_runprg(self,key,value,magics,line):
        magics['runprg'] = value
        return ''
    def kfn_runprgargs(self,key,value,magics,line):
        for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
            magics['runprgargs'] += [argument.strip('"')]
        return ''
    def kfn_args(self,key,value,magics,line):
        for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
            magics['args'] += [argument.strip('"')]
        return ''
    def init_filter(self,magics):
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
        self.addmagicsSkey(magics,'log',self.kfn_log)
        self.addmagicsSkey(magics,'loadurl',self.kfn_loadurl)
        self.addmagicsSkey(magics,'runprg',self.kfn_runprg)
        self.addmagicsSkey(magics,'runprgargs',self.kfn_runprgargs)
        self.addmagicsSkey(magics,'args',self.kfn_args)
    def reset_filter(self):
        self.magics = {
                  'bt':{
                    'repllistpid':'',
                    'onlyrunmagics':'',
                    'runinterm':'',
                    'replcmdmode':'',
                    'replprompt':''
                    },
                  'st':{
                    'ldflags':[],
                    'cflags':[],
                    'coptions':[],
                    'joptions':[],
                    'runmode':[],
                    'replsetip':[],
                    'replchildpid':"0",
                    'pidcmd':[],
                    'term':[],
                    'outputtype':'text/plain',
                    'log':[],
                    'loadurl':[],
                    'runprg':[],
                    'runprgargs':[],
                    'args':[]
                    },
                  'dt':{},
                  'btf':{
                    'repllistpid':[self.kobj.repl_listpid],
                    'onlyrunmagics':[],
                    'runinterm':[],
                    'replcmdmode':[],
                    'replprompt':[]
                    },
                  'stf':{
                    'ldflags':[],
                    'cflags':[],
                    'coptions':[],
                    'joptions':[],
                    'runmode':[],
                    'replsetip':[],
                    'replchildpid':[],
                    'pidcmd':[],
                    'term':[],
                    'outputtype':[],
                    'log':[],
                    'loadurl':[],
                    'runprg':[],
                    'runprgargs':[],
                    'args':[]
                    },
                  'dtf':{},
                  'codefilename':'',
                  'classname':'',
                  'dlrun': [],
                  'package': '',
                  'main': '',
                  'pubclass': '',
                  'pid': []
                  }
    def call_btproc(self,magics,line)->bool:
        if len(magics['bt'])<1:return False
        try:
            key= line.strip()[3:]
            if magics['bt'].__contains__(key):
                magics['bt'][key]='true'
                if len(magics[type+'f'][key])>0:
                    for kfunc in magics[type+'f'][key]:
                        kfunc(line)
                return True
        except Exception as e:
            self.kobj._logln(str(e))
        finally:pass
        return False
    def call_stproc(self,magics,line,key,value)->str:
        if len(magics['st'])<1:return line
        newline=line
        try:
            if magics['st'].__contains__(key):
                if len(magics['stf'][key])>0:
                    for kfunc in magics['stf'][key]:
                        # self.kobj._logln("call--------"+key)
                        newline=kfunc(key,value,magics,newline)
                return newline
        except Exception as e:
            self.kobj._logln("call_stproc "+str(e))
        finally:pass
        return newline
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
        actualCode = ''
        newactualCode = ''
        self.reset_filter()
        self.init_filter(self.magics)
        magics =self.magics
        for line in code.splitlines():
            orgline=line
            if line==None or line.strip()=='': continue
            if line.strip().startswith('package'):
                qline=self.kobj.replacemany(line,'; ', ';')
                qline=self.kobj.replacemany(qline,' ;', ';')
                qline= qline[:len(qline)-1]
                li=qline.strip().split()
                if(len(li)>1):
                    magics[li[0].strip()] = li[1].strip()
                actualCode += line + '\n'
                continue
            if line.strip().startswith('public'):
                qline = self.kobj.replacemany(line, 's  ', 's ')
                li = qline.strip().split()
                if(len(li) > 2 and li[1].strip() == 'class'):
                    magics[li[0].strip()] = li[1].strip()
                    pubclass = li[2].strip()
                    if pubclass.strip().endswith('{'):
                        pubclass = pubclass[:len(pubclass)-1]
                    magics['pubclass'] = pubclass
                actualCode += line + '\n'
                continue
            if self._is_specialID(line):
                if self.call_btproc(magics,line):continue
                # if line.strip()[3:] == "repllistpid":
                #     magics['repllistpid'] += ['true']
                #     self.kobj.repl_listpid('')
                #     continue
                # elif line.strip()[3:] == "onlyrunmagics":
                #     magics['onlyrunmagics'] = 'true'
                #     continue
                # elif line.strip()[3:] == "runinterm":
                #     magics['runinterm'] = 'true'
                #     continue
                # elif line.strip()[3:] == "replcmdmode":
                #     magics['replcmdmode'] = 'true'
                #     continue
                # elif line.strip()[3:] == "replprompt":
                #     magics['replprompt'] += ['replprompt']
                else:
                    #_filter2_magics_i1
                    for pkey,pvalue in self.IBplugins.items():
                        # print( pkey +":"+str(len(pvalue))+"\n")
                        for pobj in pvalue:
                            newline=''
                            try:
                                if line.strip()[3:] in pobj.getIDBptag(pobj):
                                    newline=pobj.on_IBpCodescanning(pobj,magics,line)
                                    if newline=='':continue
                            except Exception as e:
                                pass
                            finally:pass
                            # if newline!=None and newline!='':
                            #     actualCode += newline + '\n'
                findObj= re.search( r':(.*)',line)
                if not findObj or len(findObj.group(0))<2:
                    continue
                key, value = line.strip()[3:].split(":", 1)
                key = key.strip().lower()
                newline=self.call_stproc(magics,line,key,value)
                if newline!=line and len(newline)>0:
                    actualCode += newline + '\n'
                    continue
                # else:
                #     actualCode += newline + '\n'
                # if key in ['ldflags', 'cflags','coptions','joptions']:
                #     for flag in value.split():
                #         magics[key] += [flag]
                # elif key == "runmode":
                #     if len(value)>0:
                #         magics[key] = value[re.search(r'[^/]',value).start():]
                #     else:
                #         magics[key] ='real'
                # elif key == "replsetip":
                #     magics['replsetip'] = value
                # elif key == "replchildpid":
                #     magics['replchildpid'] = value
                # elif key == "pidcmd":
                #     magics['pidcmd'] = [value]
                #     if len(magics['pidcmd'])>0:
                #         findObj= value.split(",",1)
                #         if findObj and len(findObj)>1:
                #             pid=findObj[0]
                #             cmd=findObj[1]
                #             self.kobj.send_cmd(pid=pid,cmd=cmd)
                # elif key == "term":
                #     magics['term']=[]
                #     for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                #         magics['term'] += [argument.strip('"')]
                # elif key == "outputtype":
                #     magics[key]=value
                # elif key == "log":
                #     magics['log'] = value.strip()
                #     self.kobj._loglevel= value.strip()
                # elif key == "loadurl":
                #     url=value
                #     if(len(url)>0):
                #         line=self.kobj.loadurl(url)
                #         actualCode += line + '\n'
                # elif key == "runprg":
                #     magics['runprg'] = value
                # elif key == "runprgargs":
                #     ## Split arguments respecting quotes
                #     for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                #         magics['runprgargs'] += [argument.strip('"')]
                # elif key == "args":
                #     ## Split arguments respecting quotes
                #     for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                #         magics['args'] += [argument.strip('"')]
                # else:
                pass
                #_filter2_magics_i2
                for pkey,pvalue in self.ISplugins.items():
                    # print( pkey +":"+str(len(pvalue))+"\n")
                    for pobj in pvalue:
                        newline=''
                        try:
                            if key in pobj.getIDSptag(pobj):
                                newline=pobj.on_ISpCodescanning(pobj,key,value,magics,line)
                                if newline=='':continue
                        except Exception as e:
                            pass
                        finally:pass
                        if newline!=None and newline!='':
                            actualCode += newline + '\n'
                # always add empty line, so line numbers don't change
                # actualCode += '\n'
            else:
                actualCode += line + '\n'
        newactualCode=actualCode
        bcancel_exec,newcode=self.raise_ICodescan(magics,newactualCode)
        if not bcancel_exec:
            newactualCode=newcode
        #_filter2_magics_pend
        if len(self.addkey2dict(magics,'file'))>0 :
            newactualCode=''
            for line in actualCode.splitlines():
                try:
                    # if len(self.addkey2dict(magics,'test'))<1:
                    line=self.kobj.cleantestcode(line)
                    if line=='':continue
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
        return magics, newactualCode
