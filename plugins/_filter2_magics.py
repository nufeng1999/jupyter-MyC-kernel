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
    def __init__(self,kobj,plugins:List):
        self.kobj=kobj
        self.plugins=plugins
        self.ISplugins=self.plugins[0]
        self.IDplugins=self.plugins[1]
        self.IBplugins=self.plugins[2]
        pass
    def _is_specialID(self,line):
        if line.strip().startswith('##%') or line.strip().startswith('//%'):
            return True
        return False
    def addkey2dict(self,magics:Dict,key:str):
        if not magics.__contains__(key):
            d={key:[]}
            magics.update(d)
        return magics[key]
    def filter(self, code):
        actualCode = ''
        newactualCode = ''
        magics = {'cflags': [],
                  'ldflags': [],
                  'dlrun': [],
                  'coptions': [],
                  'joptions': [],
                  'package': '',
                  'main': '',
                  'pubclass': '',
                  'runprg': '',
                  'runprgargs': [],
                  'repllistpid': [],
                  'replcmdmode': [],
                  'replprompt': [],
                  'replsetip': "\r\n",
                  'replchildpid':"0",
                  'outputtype':'text/plain',
                  'runmode': [],
                  'pid': [],
                  'pidcmd': [],
                  'args': [],
                  'rungdb': []}
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
                if line.strip()[3:] == "repllistpid":
                    magics['repllistpid'] += ['true']
                    self.repl_listpid()
                    continue
                elif line.strip()[3:] == "replcmdmode":
                    magics['replcmdmode'] += ['replcmdmode']
                    continue
                elif line.strip()[3:] == "replprompt":
                    magics['replprompt'] += ['replprompt']
                    continue
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
                if key in ['ldflags', 'cflags','coptions','joptions']:
                    for flag in value.split():
                        magics[key] += [flag]
                elif key == "runmode":
                    if len(value)>0:
                        magics[key] = value[re.search(r'[^/]',value).start():]
                    else:
                        magics[key] ='real'
                elif key == "replsetip":
                    magics['replsetip'] = value
                elif key == "replchildpid":
                    magics['replchildpid'] = value
                elif key == "pidcmd":
                    magics['pidcmd'] = [value]
                    if len(magics['pidcmd'])>0:
                        findObj= value.split(",",1)
                        if findObj and len(findObj)>1:
                            pid=findObj[0]
                            cmd=findObj[1]
                            self.kobj.send_cmd(pid=pid,cmd=cmd)
                elif key == "outputtype":
                    magics[key]=value
                elif key == "runprg":
                    magics['runprg'] = value
                elif key == "runprgargs":
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        magics['runprgargs'] += [argument.strip('"')]
                elif key == "args":
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        magics['args'] += [argument.strip('"')]
                else:
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
        #_filter2_magics_pend
        if len(self.addkey2dict(magics,'file'))>0 :
            newactualCode=''
            for line in actualCode.splitlines():
                try:
                    if len(self.addkey2dict(magics,'test'))<1:
                        line=self.kobj.cleantestcode(line)
                    if line=='':continue
                    line=self.kobj.callIDplugin(line)
                    if line=='':continue
                    line=self.kobj.cleandqm(line)
                    if line=='':continue
                    line=self.kobj.cleansqm(line)
                    if self.kobj.cleannotes(line)=='':
                        continue
                    else:
                        newactualCode += line + '\n'
                except Exception as e:
                    self.kobj._log(str(e),3)
        return magics, newactualCode
