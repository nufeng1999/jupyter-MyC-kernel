##
from math import exp
from queue import Queue
from threading import Thread
from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF
from jinja2 import Environment, PackageLoader, select_autoescape,Template
from abc import ABCMeta, abstractmethod
from typing import List, Dict, Tuple, Sequence
from shutil import copyfile,move
from urllib.request import urlopen
import socket
import copy
import mmap
import contextlib
import atexit
import platform
import atexit
import base64
import urllib.request
import urllib.parse
import pexpect
import signal
import typing 
import typing as t
import re
import signal
import subprocess
import tempfile
import os
import stat
import sys
import traceback
import os.path as path
import codecs
import time
import importlib
import importlib.util
import inspect
from . import ipynbfile
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag,ICodePreproc
from plugins._filter2_magics import Magics
try:
    zerorpc=__import__("zerorpc")
    # import zerorpc
except:
    pass
fcntl = None
msvcrt = None
bLinux = True
if platform.system() != 'Windows':
    fcntl = __import__("fcntl")
    bLinux = True
else:
    msvcrt = __import__('msvcrt')
    bLinux = False
class RPCsrv(object):
    def __init__(self,kobj,magics):
        self.kobj=kobj
        self.magics=magics
    def output(self, contents):
        self.kobj._logln(contents)
        return
    def stdincmd(self,cmdstr,outencode='UTF-8'):
        pass
        if self.kobj._put2stdin_queue.full(): return ''
        self.kobj._put2stdin_queue.put(cmdstr.encode(outencode, errors='ignore'))
        return cmdstr
    def cmd(self,cmdstr,outencode='UTF-8'):
        self.kobj._logln("cmd received:"+cmdstr)
        if cmdstr.strip()=='stopsrv':
            self.kobj.stop_srvmode()
        return cmdstr
    def retryexeccode(self):
        self.kobj.do_retryexeccode()
        return
    def stopsrv(self):
        self.kobj.stop_srvmode()
        return
    
##
class CFileLock:
    def __init__(self, filename):
        self.tmpdir = tempfile.TemporaryDirectory()
        fname=filename+ '.lock'
        fname = os.path.join(self.tmpdir.name, filename)
        self.filename = fname
        self.file = None
    def __del__(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        self.tmpdir.cleanup()
    def lock(self):
        if bLinux is True:
            self.file = open(self.filename, 'wb')
            try:
                fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except:
                return False
        else:
            self.file = open(self.filename, 'wb')
            try:
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            except:
                return False
            return True
 
    def unlock(self):
        try:
            if bLinux is True:
                fcntl.flock(self.file, fcntl.LOCK_UN)
                self.file.close()
            else:
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
        except:
            pass
class IREPLWrapper(replwrap.REPLWrapper):
    def __init__(self, write_to_stdout, write_to_stderr, read_from_stdin,
                cmd_or_spawn,replsetip, orig_prompt, prompt_change,
                extra_init_cmd=None, line_output_callback=None):
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr
        self._read_from_stdin = read_from_stdin
        self.line_output_callback = line_output_callback
        self.replsetip=replsetip
        self.startflag=True
        self.startexpecttimeout=60
        # x = time.localtime(time.time())
        self.start_time = time.time()
        replwrap.REPLWrapper.__init__(self, cmd_or_spawn, orig_prompt,
                                      prompt_change,extra_init_cmd=extra_init_cmd)
    def _expect_prompt(self, timeout=-1):
        if timeout ==None :
            # "None" means we are executing code from a Jupyter cell by way of the run_command
            # in the do_execute() code below, so do incremental output.
            retry=0
            received=False
            cmdstart_time = time.time()
            cmdexectimeout=10
            while True:
                if self.startflag :
                    cmdexectimeout=None
                    run_time = time.time() - cmdstart_time
                    if run_time > self.startexpecttimeout:
                        self.startflag=False
                        self.line_output_callback(self.child.before + '\r\n')
                        # self.line_output_callback("\nEnd of startup process\n")
                        break
                try:
                    pos = self.child.expect_exact([self.prompt, self.continuation_prompt, self.replsetip, pexpect.EOF, pexpect.TIMEOUT],timeout=cmdexectimeout)
                    if pos == 2:
                        # End of line received
                        if self.child.terminated:
                            self.line_output_callback("\nprocess.terminated\n")
                        self.line_output_callback(self.child.before +self.replsetip+ '\r\n')
                        self.line_output_callback("\nEnd of startup process\n")
                        self.replsetip=u'\r\n'
                        cmdexectimeout=None
                        self.startflag=False
                        break
                    elif pos ==3:
                        if len(self.child.before) != 0:
                            self.line_output_callback(self.child.before + '\r\n')
                        self.line_output_callback('The process has exited.\r\n')
                        break
                    elif pos == 0:
                        self.line_output_callback(self.child.before + '\n')
                        cmdstart_time = time.time()
                        if self.prompt!="\r\n":break
                    else:
                        if len(self.child.before) != 0:
                            # prompt received, but partial line precedes it
                            self.line_output_callback(self.child.before)
                            cmdstart_time = time.time()
                        else:
                            if self.startflag :
                                continue
                            run_time = time.time() - cmdstart_time
                            if run_time > 10:
                                break
                except Exception as e:
                    # self.line_output_callback(self.child.before)
                    self._write_to_stderr("[MyCkernel] Error:Executable _expect_prompt error! "+str(e)+"\n")
        else:
            # Otherwise, use existing non-incremental code
            pos = replwrap.REPLWrapper._expect_prompt(self, timeout=timeout)
        # Prompt received, so return normally
        return pos
class RealTimeSubprocess(subprocess.Popen):
    inputRequest = "<inputRequest>"
    kobj=None
    def setkobj(self,k=None):
        self.kobj=k
    def __init__(self, cmd, write_to_stdout, write_to_stderr, read_from_stdin,
        cwd=None,shell=False,env=None,kobj=None,outencode='UTF-8',
        fifoname=None,stdout2fifo=False,fifo2stdin=False):
        self.fifoname=fifoname
        self.stdout2fifo=stdout2fifo
        self.fifo2stdin=fifo2stdin
        self.flock=None
        self.outencode=outencode
        self.kobj=kobj
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr
        self._read_from_stdin = read_from_stdin
        if env!=None and len(env)<1:env=None
        self.foflag=False
        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                            bufsize=0,cwd=cwd,shell=shell,env=env)
        self._stop_send_data=False
        self._stop_read_data=False
        self.fifo_threadproc(self.fifoname,self.stdout2fifo,self.fifo2stdin)
        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue,self))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()
        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue,self))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()
    
    @staticmethod
    def _enqueue_output(stream, queue,robj):
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()
    def write_contents(self,magics=None):
        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res
        if self.fifo2stdin:
            sh_contents = read_all_from_queue(self._fiforead_queue)
            if sh_contents:
                self.stdin.write(sh_contents)
        k_contents = read_all_from_queue(self.kobj._put2stdin_queue)
        if k_contents:
            self.stdin.write(k_contents)
        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            if self.kobj!=None:
                self.kobj._logln(stderr_contents.decode('UTF-8', errors='ignore'),3)
            else:
                self._write_to_stderr(stderr_contents.decode('UTF-8', errors='ignore'))
        stdout_contents = read_all_from_queue(self._stdout_queue)
        self.out_stdout_contents(stdout_contents,magics)
    def fifo_threadproc(self,fifoname=None,stdout2fifo=False,fifo2stdin=False):
        if (fifo2stdin or stdout2fifo) and (fifoname!=None and len(fifoname)>0):
            # if self.flock==None:self.flock=CFileLock(fifoname)
            if self.kobj.flock==None:self.kobj.flock=CFileLock(fifoname)
            if stdout2fifo:
                
                self._sendend=False
                self._fifosent_queue = Queue()
                self.kobj._logln("启动内存通信通道:"+fifoname)
                self._fifosend_thread = Thread(target=RealTimeSubprocess._send_data, args=(self,self._fifosent_queue,fifoname,4096))
                self._fifosend_thread.daemon = True
                self._fifosend_thread.start()
            if fifo2stdin:
                self._fiforead_queue = Queue()
                self.kobj._logln("启动内存通信通道:"+fifoname)
                self._fiforead_thread = Thread(target=RealTimeSubprocess._read_data, args=(self,self._fiforead_queue,fifoname,4096,self.outencode))
                self._fiforead_thread.daemon = True
                self._fiforead_thread.start()
    @staticmethod            
    def _send_data(robj,queue,name,memsize=1024):
        def read_all_from_queue(queue,n):
            robj._sendend=False
            res = b''
            size = queue.qsize()
            sz=size
            if n<=size:
                sz=n
                size=sz
            while sz != 0:
                res += queue.get_nowait()
                sz -= 1
            return res,size
        while not robj._stop_send_data:
            content,size=read_all_from_queue(queue,memsize)
            if size<1:
                robj._sendend=True
                time.sleep(1/1000)
                continue
            bret=robj.kobj.sendmsg2sh(name,memsize,content,robj)
    @staticmethod
    def _read_data(robj,queue,name,memsize=1024,outencode='UTF-8'):
        while not robj._stop_read_data:
            bret=robj.kobj.readdatafromsh(queue,name,memsize=memsize,outencode='UTF-8')
    def write2stdin(self,queue):
        def read_all_from_queue(queue):
            res = b''
            # sz=n
            size = queue.qsize()
            # if n=<size:size=sz
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res,size
        bcontents,size=read_all_from_queue(queue)
        self.stdin.write(bcontents)
    def write2sh(self,name,content):
        self._fifosent_queue.put(content)
    def fifoproc(self,fifoname=None,stdout2fifo=False,fifo2stdin=False,content=None):
        if (fifo2stdin or stdout2fifo) and (fifoname!=None and len(fifoname)>0):
            # if self.flock==None:self.flock=CFileLock(fifoname)
            if stdout2fifo:
                # and self.foflag!=True:
                # self._write_to_stdout("stdout2fifo--->"+str(stdout2fifo)+"\n")
                self.foflag=True
                self.write2sh(fifoname,content)
            if fifo2stdin:
                # and self.foflag!=True:
                # self._write_to_stdout("fifo2stdin--->"+str(fifo2stdin)+"\n")
                self.foflag=True
                self.write2stdin(self._fiforead_queue,fifoname)
    def out_stdout_contents(self,stdout_contents,magics):
        if stdout_contents:
            if self.kobj.get_magicsSvalue(magics,"outputtype").startswith("image"):
                self._write_to_stdout(stdout_contents,magics)
                magics['_st']["outputtype"]="text/plain"
                return
            contents=''
            if self.outencode=='UTF-8':
                contents = stdout_contents.decode('UTF-8', errors='ignore')
            else:
                contents = stdout_contents.decode(self.outencode, errors='ignore')
            # if there is input request, make output and then
            # ask frontend for input
            start = contents.find(self.__class__.inputRequest)
            if(start >= 0):
                contents = contents.replace(self.__class__.inputRequest, '')
                if(len(contents) > 0):
                    self._write_to_stdout(contents,magics)
                readLine = ""
                while(len(readLine) == 0):
                    readLine = self._read_from_stdin()
                # need to add newline since it is not captured by frontend
                readLine += "\n"
                self.stdin.write(readLine.encode())
            else:
                if self.stdout2fifo:
                    self.fifoproc(self.fifoname,self.stdout2fifo,self.fifo2stdin,stdout_contents);
                self._write_to_stdout(contents,magics)
    def wait_end(self,magics):
        while self.poll() is None:
            time.sleep(1/1000)
            if self.kobj.get_magicsSvalue(magics,"outputtype").startswith("text"):
                self.write_contents(magics)
            pass
            continue
        self.write_contents(magics)
        # self.write_contents(magics)
        # wait for threads to finish, so output is always shown
        self._stdout_thread.join()
        self._stderr_thread.join()
        self.wait_stdoutd()
        self._stop_send_data=True
        self._stop_read_data=True
        # self.write_contents(magics)
        # self.clean_namedpipe()
        if self.kobj==None:
            self._write_to_stdout("The process end:"+str(self.pid)+"\n",magics)
        else:
            self.kobj._logln("The process end:"+str(self.pid))
        ############################################
        return self.returncode
    def wait_stdoutd(self):
        time.sleep(1/1000)
        if self.stdout2fifo:
            cmdstart_time = time.time()
            while not (self._fifosent_queue.empty() and self._sendend):
                run_time = time.time() - cmdstart_time
                if run_time > 60: 
                    self.kobj._logln("超时退出")
                    break
                time.sleep(1/1000)
                continue
class MyMagics():
    
    main_head = "\n" \
            "\n" \
            "int main(List<String> arguments){\n"
    main_foot = "\nreturn 0;\n}"
##
    pausestr='''
        get_char()
        {
        SAVEDSTTY=`stty -g`
        stty -echo
        stty cbreak
        dd if=/dev/tty bs=1 count=1 2> /dev/null
        stty -raw
        stty echo
        stty $SAVEDSTTY
        }
        echo ""
        echo "Press any key to start...or Press Ctrl+c to cancel"
        char=`get_char`
        echo "OK"
        '''
##
##
    def get_retinfo(self, rettype:int=0):
        retinfo='OK'
        if len(self.__independent)>0 and self.__jkobj!=None:
            retinfo={'status': 'ok', 'execution_count': self.__jkobj.get_execution_count(), 'payload': [], 'user_expressions': {}}
        elif len(self.__independent)>0 and self.__jkobj==None:
            retinfo='OK'
        elif len(self.__independent)<1 and self.__jkobj!=None:
            retinfo={'status': 'ok', 'execution_count': self.__jkobj.get_execution_count(), 'payload': [], 'user_expressions': {}}
        elif len(self.__independent)<1 and self.__jkobj==None:
            retinfo={'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
        return retinfo
    def chkjoptions(self,magics,jarfile,targetdir):
        if len(self.addmagicsSkey(magics,'joptions'))>-1:
            index=-1
            try:
                index=self.addmagicsSkey(magics,'joptions').index('-cp')
            except Exception as e:
                pass
            if(index<0):
                magics['_st']['joptions']+=['-cp']
                magics['_st']['joptions']+=[':']
                index=index+1
            cpstr=magics['_st']['joptions'][index+1]
            cpstr=cpstr+":"+jarfile+":"+targetdir
            if cpstr.strip().startswith(':'):
                cpstr=cpstr[1:] 
            # self._log(cpstr)
            magics['_st']['joptions'][index+1]=cpstr
    def __init__(self,jkobj,runfiletype='', *args, **kwargs):
        self.runfiletype=runfiletype
        self.__independent='yes'
        self.__jkobj=jkobj
        self.__rpcsrv = None
        self._rpcsrv_thread= None
        self.rpcsrvobj=None
        self.kernelinfo="[MyMagics]"
        if self.__jkobj!=None :
            self.kernelinfo=self.__jkobj.get_kernelinfo()
        self.first_magics=None
        self._put2stdin_queue = Queue(maxsize=1024)
        self.first_cellcodeinfo=None
        self.flock=None
        self._allow_stdin = True
        
        self.readOnlyFileSystem = False
        self.bufferedOutput = True
        self.linkMaths = True # always link math library
        self.wAll = True # show all warnings by default
        self.wError = False # but keep comipiling for warnings
        self.sys = platform.system()
        self.subsys=self.getossubsys()
        self.files = []
        self.__issqm=False ## 清除单引号多行注释
        self.__isdqm=False ##清除双引号多行注释
        self.__istestcode=False
        self.__isdstr=False
        self.__issstr=False
        self.__loglevel='1'
        self.silent=None ##沉默运行，不输出任何信息
        self.jinja2_env = Environment()
        self.g_rtsps={}
        self.g_chkreplexit=True
        
        self.ISplugins={"0":[],
            "1":[],
            "2":[],
            "3":[],
            "4":[],
            "5":[],
            "6":[],
            "7":[],
            "8":[],
            "9":[]}
        self.IDplugins={"0":[],
            "1":[],
            "2":[],
            "3":[],
            "4":[],
            "5":[],
            "6":[],
            "7":[],
            "8":[],
            "9":[]}
        self.IBplugins={"0":[],
            "1":[],
            "2":[],
            "3":[],
            "4":[],
            "5":[],
            "6":[],
            "7":[],
            "8":[],
            "9":[]}
        self.ICodePreprocs={"0":[],
            "1":[],
            "2":[],
            "3":[],
            "4":[],
            "5":[],
            "6":[],
            "7":[],
            "8":[],
            "9":[]}
        self.plugins=[self.ISplugins,self.IDplugins,self.IBplugins]
    
        self.chk_replexit_thread = Thread(target=self.chk_replexit, args=(self.g_rtsps))
        self.chk_replexit_thread.daemon = True
        self.chk_replexit_thread.start()
        self.init_plugin()
        self.mag=Magics(self,self.plugins,self.ICodePreprocs)
    def get_kernelinfo(self):
        self.kernelinfo=self.__jkobj.get_kernelinfo()
        return self.kernelinfo
    def reset(self):
        self.files =None
        self.first_magics=None
        self._put2stdin_queue =None
        self.first_cellcodeinfo=None
        self.flock=None
        self.files = []
        self._put2stdin_queue = Queue(maxsize=1024)
##
    def resolving_enveqval(self, envstr):
        if envstr is None or len(envstr.strip())<1:
            return os.environ
        # env_dict={}
        argsstr=self.replacemany(self.replacemany(self.replacemany(envstr.strip(),('  '),' '),('= '),'='),' =','=')
        pattern = re.compile(r'([^\s*]*)="(.*?)"|([^\s*]*)=(\'.*?\')|([^\s*]*)=(.[^\s]*)')
        for argument in pattern.findall(argsstr):
            li=list(argument)
            li= [i for i in li if i != '']
            # env_dict[str(li[0])]=li[1]
            os.environ.setdefault(str(li[0]),li[1])
        # envstr=str(str(envstr.split("|")).split("=")).replace(" ","").replace("\'","").replace("\"","").replace("[","").replace("]","").replace("\\","")
        # env_list=envstr.split(",")
        # for i in range(0,len(env_list),2):
        #     os.environ.setdefault(env_list[i],env_list[i+1])
        return os.environ
    def resolving_eqval2dict(self,argsstr):
        if not argsstr or len(argsstr.strip())<1:
            return None
        env_dict={}
        argsstr=self.replacemany(self.replacemany(self.replacemany(argsstr.strip(),('  '),' '),('= '),'='),' =','=')
        pattern = re.compile(r'([^\s*]*)="(.*?)"|([^\s*]*)=(\'.*?\')|([^\s*]*)=(.[^\s]*)')
        for argument in pattern.findall(argsstr):
            li=list(argument)
            li= [i for i in li if i != '']
            env_dict[str(li[0])]=li[1]
        return env_dict
    def get_outencode(self,magics):
        encodestr=self.get_magicsSvalue(magics,"outencode")
        if len(encodestr)<1:
            encodestr='UTF-8'
        return encodestr
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
    usleep = lambda x: time.sleep(x/1000000.0)
    def replacemany(self,our_str, to_be_replaced:str, replace_with:str):
        while (to_be_replaced in our_str):
            our_str = our_str.replace(to_be_replaced, replace_with)
        return our_str
    def _filter_dict(self,argsstr):
        if not argsstr or len(argsstr.strip())<1:
            return None
        env_dict={}
        argsstr=self.replacemany(self.replacemany(self.replacemany(argsstr.strip(),('  '),' '),('= '),'='),' =','=')
        pattern = re.compile(r'([^\s*]*)="(.*?)"|([^\s*]*)=(\'.*?\')|([^\s*]*)=(.[^\s]*)')
        for argument in pattern.findall(argsstr):
            li=list(argument)
            li= [i for i in li if i != '']
            env_dict[str(li[0])]=li[1]
        return env_dict
    def _fileshander(self,files:List,srcfilename,magics)->str:
        index=-1
        fristfile=srcfilename
        try:
            for newsrcfilename in files:
                index=index+1
                newsrcfilename = os.path.join(os.path.abspath(''),newsrcfilename)
                if os.path.exists(newsrcfilename):
                    if magics!=None and len(self.addkey2dict(magics,'overwritefile'))<1:
                        newsrcfilename +=".new.py"
                if not os.path.exists(os.path.dirname(newsrcfilename)) :
                    os.makedirs(os.path.dirname(newsrcfilename))
                if index==0:
                    os.rename(srcfilename,newsrcfilename)
                    fristfile=newsrcfilename
                    files[0]=newsrcfilename
                else:
                    self._write_to_stdout("copy to :"+newsrcfilename+"\n")
                    copyfile(fristfile,newsrcfilename)
        except Exception as e:
                self._log(str(e),2)
        return files[0]
    def _is_specialID(self,line):
        if line.strip().startswith('##%') or line.strip().startswith('//%'):
            return True
        return False
    def _is_test_begin(self,line):
        if line==None or line=='':return ''
        return line.strip().startswith('') or line.strip().startswith('')
    def _is_test_end(self,line):
        if line==None or line=='':return ''
        return line.strip().startswith('') or line.strip().startswith('')
    def _is_dqm_begin(self,line):
        if line==None or line=='':return ''
        line=self.replacemany(line.strip(),(' '),'')
        if '=\"\"\"' in line: 
            self.__isdstr=True
            return False
        if '\"\"\"' in line: 
            if self.__isdstr:return False
            self.__isdstr=False
            return True
        return line.lstrip().startswith('\"\"\"')
    def _is_dqm_end(self,line):
        if line==None or line=='':return ''
        if self.__isdqm:
            return line.rstrip().endswith('\"\"\"')
        return False
    def _is_sqm_begin(self,line):
        if line==None or line=='':return ''
        line=self.replacemany(line.strip(),(' '),'')
        if '=\'\'\'' in line: 
            self.issstr=True
            return False
        if '\'\'\'' in line: 
            if self.issstr:return False
            self.issstr=False
            return True
        return line.lstrip().startswith('\'\'\'')
    def _is_sqm_end(self,line):
        if line==None or line=='':return ''
        if self.__issqm:
            return line.rstrip().endswith('\'\'\'')
        return False
    
    def cleanCdqm(self,code):
        return re.sub(r"/\*.*?\*/", "", code, flags=re.M|re.S)
    def cleanCnotes(self,code):
        return re.sub(r"//.*", "", code)
    def cleannotes(self,line):
        ##tmpCode = re.sub(r"//.*", "", line)
        ##tmpCode = re.sub(r"/\*.*?\*/", "", tmpCode, flags=re.M|re.S)
        return '' if (not self._is_specialID(line)) and (line.lstrip().startswith('## ') or line.lstrip().startswith('// ')) else line
    
    def cleandqmA(self,code):
        return re.sub(r"\"\"\".*?\"\"\"", "", code, flags=re.M|re.S)
    def cleandqm(self,line):
        ##tmpCode = re.sub(r"\"\"\".*?\"\"\"", "", line, flags=re.M|re.S)
        if not self.__isdqm:
            istb=self._is_dqm_begin(line)
            if istb: 
                self.__isdqm=True
                if len(line.strip())>5:
                    iste=self._is_dqm_end(line)
                    if iste:self.__isdqm=False
                return ''
        iste=self._is_dqm_end(line)
        if iste:
            self.__isdqm=False
            return ''
        line= "" if self.__isdqm else line
        return line
    def cleansqmA(self,code):
        return re.sub(r"\'\'\'.*?\'\'\'", "", code, flags=re.M|re.S)
    def cleansqm(self,line):
        if not self.__issqm:
            istb=self._is_sqm_begin(line)
            if istb: 
                self.__issqm=True
                if len(line.strip())>5:
                    iste=self._is_sqm_end(line)
                    if iste:self.__issqm=False
                return ''
        iste=self._is_sqm_end(line)
        if iste:
            self.__issqm=False
            return ''
        line= "" if self.__issqm else line
        return line
    
    def cleantestcodeA(self,code):
        code=re.sub(r"\/\/test_begin.*?\/\/test_end", "", code, flags=re.M|re.S)
        return re.sub(r"\#\#test_begin.*?\#\#test_end", "", code, flags=re.M|re.S)
    def cleantestcodeB(self,code):
        code=re.sub(r"\/\/test_begin", "", code, flags=re.M|re.S)
        code=re.sub(r"\/\/test_end", "", code, flags=re.M|re.S)
        code=re.sub(r"\#\#test_begin", "", code, flags=re.M|re.S)
        return re.sub(r"\#\#test_end", "", code, flags=re.M|re.S)
    def cleantestcode(self,line):
        if not self.__istestcode:
            istb=self._is_test_begin(line)
            if istb: 
                self.__istestcode=True
                if len(line.strip())>5:
                    iste=self._is_test_end(line)
                    if iste:self.__istestcode=False
                return ''
        iste=self._is_test_end(line)
        if iste:
            self.__istestcode=False
            return ''
        line= "" if self.__istestcode else line
        return line
    
    def repl_listpid(self,cmd=None):
        if len(self.g_rtsps)>0: 
            self._write_to_stdout("--------All replpid--------\n")
            for key in self.g_rtsps:
                self._write_to_stdout(key+"\n")
        else:
            self._write_to_stdout("--------All replpid--------\nNone\n")
    def chk_replexit(self,grtsps): 
        while self.g_chkreplexit:
            try:
                if len(grtsps)>0: 
                    for key in grtsps:
                        if grtsps[key].child.terminated:
                            pass
                            del grtsps[key]
            finally:
                pass
        if len(grtsps)>0: 
            for key in grtsps:
                if grtsps[key].child.terminated:
                    pass
                    del grtsps[key]
                else:
                    grtsps[key].child.terminate(force=True)
                    del grtsps[key]
    def cleanup_files(self):
        # keep the list of files create in case there is an exception
        # before they can be deleted as usual
        if self.files != None and len(self.files) > 0:
            for file in self.files:
                if(os.path.exists(file)):
                    os.remove(file)
    def new_temp_file(self, **kwargs):
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file
    def create_codetemp_file(self,magics,code,suffix):
        encodestr='UTF-8'
        if magics!=None:
            encodestr=self.get_magicsSvalue(magics,"fileencode")
        if len(encodestr)<1:
            encodestr='UTF-8'
        if (suffix.strip().lower().endswith(".bat") or
            (suffix.strip().lower().endswith(".ps1") and self.sys=="Windows")):
            encodestr="GBK"
        source_file=self.new_temp_file(suffix=suffix,dir=os.path.abspath(''),encoding=encodestr)
        magics['codefilename']=source_file.name
        with  source_file:
            source_file.write(code)
            source_file.flush()
        return source_file
    def rawinput(self):
        if len(self.__independent)>0:
        #     return self.get_raw_input()
        # elif len(self.__independent)>0:
        #     ## 仅独立的
            return sys.stdin.readline()
        elif len(self.__independent)<1:
            return self.get_raw_input()
        # elif len(self.__independent)<1:
        #     ## 非独立的
        return self.get_raw_input()
            
    def sendresponse(self,contents,name='stdout',mimetype=None):
        if mimetype==None:
            # if len(self.get_mymagics().__independent)>0:
            #     self.__jkobj.send_response(self.__jkobj.get_iopub_socket(), 'stream', {'name': name, 'text': contents})
            # elif len(self.__independent)>0 and self.__jkobj==None:
            #     ## 仅独立的
            #     sys.stdout.write(contents)
            #     sys.stdout.flush()
            # elif len(self.get_mymagics().__independent)<1:
            self.send_response(self.iopub_socket, 'stream', {'name': name, 'text': contents})
            # elif len(self.__independent)<1 and self.__jkobj==None:
            #     ## 非独立的
            #     self.send_response(self.iopub_socket, 'stream', {'name': name, 'text': contents})
        else:
            # if len(self.get_mymagics().__independent)>0:
            #     self.__jkobj.send_response(self.__jkobj.get_iopub_socket(), 'display_data', {'data': {mimetype:contents}, 'metadata': {mimetype:{}}})
            # elif len(self.__independent)>0 and self.__jkobj==None:
            #     sys.stdout.write(contents)
            #     sys.stdout.flush()
            # elif len(self.get_mymagics().__independent)<1:
            #     self.__jkobj.send_response(self.__jkobj.get_iopub_socket(), 'display_data', {'data': {mimetype:contents}, 'metadata': {mimetype:{}}})
            # elif len(self.__independent)<1 and self.__jkobj==None:
            self.send_response(self.iopub_socket, 'display_data', {'data': {mimetype:contents}, 'metadata': {mimetype:{}}})
    def _log(self, output,level=1,outputtype='text/plain'):
        if self.__loglevel=='0': return
        streamname='stdout'
        if not self.silent:
            prestr=self.get_kernelinfo()+' Info:'
            if level==2:
                prestr=self.get_kernelinfo()+' Warning:'
                streamname='stderr'
            elif level==3:
                prestr=self.get_kernelinfo()+' Error:'
                streamname='stderr'
            else:
                prestr=self.get_kernelinfo()+' Info:'
                streamname='stdout'
            # if len(outputtype)>0 and (level!=2 or level!=3):
                # self._write_display_data(mimetype=outputtype,contents=prestr+output)
                # return
            # Send standard output
            stream_content = {'name': streamname, 'text': prestr+output}
            self.__jkobj.sendresponse(prestr+output,name=streamname)
    def _logln(self, output,level=1,outputtype='text/plain'):
        self._log(output+"\n",level=1,outputtype='text/plain')
    def _write_display_data(self,mimetype='text/html',contents=""):
        try:
            if mimetype.startswith('image'):
                metadata ={mimetype:{}}
                # contents=contents
                # self._logln(base64.encodebytes(contents))
                # contents=base64.encodebytes(contents)
                # contents=urllib.parse.quote(base64.b64encode(contents))
                header="<div><img alt=\"Output\" src=\"data:"+mimetype+";base64,"
                end="\"></div>"
                contents=header+base64.b64encode(contents).decode( errors='ignore')+end
                # base64.b64encode(image_bytes).decode('utf8')
                mimetype='text/html'
                metadata = {mimetype:{}}
        except Exception as e:
            self._logln("_write_display_data err "+str(e),3)
            return
        self.__jkobj.sendresponse(contents,mimetype=mimetype)
    def _write_to_stdout(self,contents,magics=None):
        if magics !=None and len(magics['_st']['outputtype'])>0:
                self._write_display_data(mimetype=magics['_st']['outputtype'],contents=contents)
        else:
            self.__jkobj.sendresponse(contents,name='stdout')
    def _write_to_stderr(self, contents):
        self.__jkobj.sendresponse(contents,name='stderr')
    def _read_from_stdin(self):
        return self.__jkobj.rawinput()
    def readcodefile(self,filename,spacecount=0):
        filecode=''
        codelist1=None
        if not os.path.exists(filename):
            return ''
        with open(os.path.join(os.path.abspath(''),filename), 'r',encoding="UTF-8") as codef1:
            codelist1 = codef1.readlines()
        if len(codelist1)>0:
            for t in codelist1:
                filecode+=' '*spacecount + t
        return filecode
    def loadurl(self,url):
        content=''
        try:
            request=urllib.request.Request(url)
            myURL = urlopen(request)
            lines = myURL.readlines()
            for line in lines:
                print(line)
                content+=line.decode()+"\n"
        except Exception as e:
            self._logln("loadurl error! "+str(e),3)
        return content
    def _start_replprg(self,command,args,magics):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that bash and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.silent = None
        try:
            child = pexpect.spawn(command, args,timeout=60, echo=False,
                                  encoding='utf-8')
            self._write_to_stdout("replchild pid:"+str(child.pid)+"\n")
            self._write_to_stdout("--------process info---------\n")
            self.replwrapper = IREPLWrapper(
                                    self._write_to_stdout,
                                    self._write_to_stderr,
                                    self._read_from_stdin,
                                    child,
                                    replsetip=magics['_st']['replsetip'],
                                    orig_prompt='\r\n', 
                                    prompt_change=None,
                                    extra_init_cmd=None,
                                    line_output_callback=self.process_output)
            # self._write_to_stdout("replchild pid:"+str(self.replwrapper.child.pid)+"\n")
            self.g_rtsps[str(self.replwrapper.child.pid)]=self.replwrapper
        except Exception as e:
            self._write_to_stderr("[MyPythonkernel] Error:Executable _start_replprg error! "+str(e)+"\n")
        finally:
            signal.signal(signal.SIGINT, sig)
    def process_output(self, output,magics=None):
        if not self.silent:
            if magics !=None and len(magics['_st']['outputtype'])>0:
                self._write_display_data(mimetype=magics['_st']['outputtype'],contents=output)
                return
            self.__jkobj.sendresponse(output)
    def send_replcmd(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False,magics=None):
        self.silent = silent
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
        interrupted = False
        try:
            # Note: timeout=None tells IREPLWrapper to do incremental
            # output.  Also note that the return value from
            # run_command is not needed, because the output was
            # already sent by IREPLWrapper.
            self._write_to_stdout("send replcmd:"+code.rstrip()+"\n")
            self._write_to_stdout("---Received information after send repl cmd---\n")
            if magics and len(magics['_st']['replchildpid'])>0 :
                if self.g_rtsps[magics['_st']['replchildpid']] and \
                    self.g_rtsps[magics['_st']['replchildpid']].child and \
                    not self.g_rtsps[magics['_st']['replchildpid']].child.terminated :
                    self.g_rtsps[magics['_st']['replchildpid']].run_command(code.rstrip(), timeout=None)
            else:
                if self.replwrapper and \
                    self.replwrapper.child and \
                    not self.replwrapper.child.terminated :
                    self.replwrapper.run_command(code.rstrip(), timeout=None)
            pass
        except KeyboardInterrupt:
            self.gdbwrapper.child.sendintr()
            interrupted = True
            self.gdbwrapper._expect_prompt()
            output = self.gdbwrapper.child.before
            self.process_output(output)
        except EOF:
            # output = self.gdbwrapper.child.before + 'Restarting GDB'
            # self._start_gdb()
            # self.process_output(output)
            pass
        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}
        # try:
        #     exitcode = int(self.replwrapper.run_command('echo $?').rstrip())
        # except Exception as e:
        #     self.process_output("[MyPythonkernel] Error:Executable send_replcmd error! "+str(e)+"\n")
        exitcode = 0
        if exitcode:
            error_content = {'execution_count': self.execution_count,
                             'ename': '', 'evalue': str(exitcode), 'traceback': []}
            self.send_response(self.iopub_socket, 'error', error_content)
            error_content['status'] = 'error'
            return error_content
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
    def do_shell_command(self,commands,cwd=None,shell=False,env=True,magics=None):
        ##self._write_to_stdout('do_shell_command '.join((' '+ str(s) for s in commands)))
        try:
            if len(magics['_bt']['replcmdmode'])>0:
                findObj= commands[0].split(" ",1)
                if findObj and len(findObj)>1:
                    cmd=findObj[0]
                    arguments=findObj[1]
                    cmdargs=[]
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', arguments):
                        cmdargs += [argument.strip('"')]
                    self._write_to_stdout(cmd)
                    self._write_to_stdout(''.join((' '+ str(s) for s in cmdargs))+"\n")
                    self._start_replprg(cmd,cmdargs,magics)
                    return
            cmds=[]
            for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', commands.strip()):
                cmds += [argument.strip('"')]
            p = self.create_jupyter_subprocess(cmds,cwd,shell,env=env,magics=magics)
            if magics!=None and len(self.get_magicsbykey(magics,'showpid'))>0:
                self._write_to_stdout("The process PID:"+str(p.pid)+"\n")
            self.g_rtsps[str(p.pid)]=p
            returncode=p.wait_end(magics)
            del self.g_rtsps[str(p.pid)]
            if returncode != 0:
                self._logln("Executable command exited with code {}\n".format(returncode),3)
            else:
                self._logln("command success.\n")
            return
        except Exception as e:
            self._logln("Executable command error! "+str(e)+"\n",3)
    def do_Py_command(self,commands,cwd=None,shell=False,env=True,magics=None):
        try:
            cmds=[]
            for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', commands.strip()):
                cmds += [argument.strip('"')]
            p = self.create_jupyter_subprocess(['python']+cmds,cwd,shell,env=env,magics=magics)
            if magics!=None and len(self.get_magicsbykey(magics,'showpid'))>0:
                self._write_to_stdout("The process PID:"+str(p.pid)+"\n")
            self.g_rtsps[str(p.pid)]=p
            returncode=p.wait_end(magics)
            del self.g_rtsps[str(p.pid)]
            if returncode != 0:
                self._logln("Executable python exited with code {}".format(returncode))
            else:
                self._logln("command python success.")
        except Exception as e:
            self._logln("Executable python command error! "+str(e)+"\n",3)
        return
    def send_cmd(self,pid,cmd):
        try:
            # self._write_to_stdout("send cmd PID:"+pid+"\n cmd:"+cmd)
            # if self.g_rtsps.has_key(pid):
                # self._write_to_stderr("[MyPythonkernel] Info:exist! "+pid+"\n")
            # self.g_rtsps[pid].stdin.write(cmd.encode())
            self.g_rtsps[pid]._write_to_stdout(cmd)
        except Exception as e:
            self._log("Executable send_cmd error! "+str(e)+"\n")
    
        return
    def create_jupyter_subprocess(self, cmd,cwd=None,shell=False,env=None,magics=None,outencode=None):
        try:
            if env==None or len(env)<1:env=os.environ
            newcwd=self.get_magicsSvalue(magics,'cwd')
            if len(newcwd)>1:cwd=newcwd.strip()
            if cwd==None:cwd=os.path.abspath('')
            if magics!=None and magics['status']=='' and len(self.addmagicsBkey(magics,'runinterm'))>0:
                self.inittermcmd(magics)
                if len(magics['_st']['term'])<1:
                    self._logln("no term！",2)
                execfile=''
                for x in cmd:
                    execfile+=x+" "
                cmdshstr=self.create_termrunsh(execfile,magics)
                if self.sys=='Windows':
                    cmd=magics['_st']['term']+[cmdshstr]
                elif self.sys=='Linux':
                    cmd=magics['_st']['term']+['--',cmdshstr]
                else:
                    cmd=magics['_st']['term']+['--',cmdshstr]
            cstr=''
            for x in cmd: cstr+=x+" "
            self._logln(cstr)
            if(magics!=None and (outencode==None or len(outencode)<0)):
                outencode=self.get_outencode(magics)
            if(outencode==None or len(outencode)<0):
                outencode='UTF-8'
            stdout2fifo=False
            fifo2stdin=False
            fifoname=''
            stdoutd=self.get_magicsSvalue(magics,'stdout->')
            stdind =self.get_magicsSvalue(magics,'stdin<-')
            if len(stdoutd)>0:
                fifoname=stdoutd
                stdout2fifo=True
            if len(stdind)>0:
                fifoname=stdind
                fifo2stdin =True
            bstdout2fifo=False
            bfifo2stdin=False
            if stdout2fifo and len(fifoname)>0:
                bstdout2fifo=True
            if fifo2stdin and len(fifoname)>0 and bstdout2fifo==False:
                bfifo2stdin=True
            return RealTimeSubprocess(cmd,
                    self._write_to_stdout,
                    self._write_to_stderr,
                    self._read_from_stdin,cwd,shell,env,self,outencode=outencode,
                    fifoname=fifoname,stdout2fifo=bstdout2fifo,fifo2stdin=bfifo2stdin)
        except Exception as e:
            self._logln("RealTimeSubprocess err:"+str(e),3)
            raise
    def getossubsys(self):
        uname=''
        try:
            u=os.popen('bash -c "uname"')
            uname=u.read()
        except Exception as e:
            self._logln(""+str(e),3)
        return uname
    def inittermcmd(self,magics):
        if len(magics['_st']['term'])>0:return ''
        termcmd=''
        try:
            if self.subsys.startswith('MINGW64') or self.subsys.startswith('CYGWIN'):
                termcmd='mintty "/usr/bin/bash" --login'
            if self.sys=='Linux':
                termcmd='gnome-terminal'
            elif self.sys=='Windows':
                termcmd='c:\\Windows\\System32\\cmd.exe /c start'
        except Exception as e:
            self._logln(""+str(e),3)
        if len(termcmd)>1:
            magics['_st']['term']=[]
            for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', termcmd):
                magics['_st']['term'] += [argument.strip('"')]
        return termcmd
    def create_termrunsh(self,execfile,magics):
        fil_ename=execfile
        uname=''
        try:
            u=os.popen('bash -c "uname"')
            uname=u.read()
        except Exception as e:
            self._logln(""+str(e),3)
        if self.subsys.startswith('MINGW64') or self.subsys.startswith('CYGWIN'):
            pausestr=self.pausestr
            termrunsh="\n"+execfile+"\n"+pausestr+"\n"
            termrunsh_file=self.create_codetemp_file(magics,termrunsh,suffix='.sh')
            newsrcfilename=termrunsh_file.name
            fil_ename=newsrcfilename
        elif self.sys=='Windows' :
            termrunsh="echo off\r\ncls\r\n"+execfile+"\r\npause\r\nexit\r\n"
            if execfile.strip().lower().endswith(".bat"):
                termrunsh="echo off\r\ncls\r\ncall "+execfile+"\r\npause\r\nexit\r\n"
            termrunsh_file=self.create_codetemp_file(magics,termrunsh,suffix='.bat')
            newsrcfilename=termrunsh_file.name
            fil_ename=newsrcfilename
        elif self.sys=='Linux':
            pausestr=self.pausestr
            termrunsh="\n"+execfile+"\n"+pausestr+"\n"
            termrunsh_file=self.create_codetemp_file(magics,termrunsh,suffix='.sh')
            newsrcfilename=termrunsh_file.name
            fil_ename=newsrcfilename
        else:
            self._logln("Cannot create terminal!",3)
        self._logln(fil_ename)
        os.chmod(newsrcfilename,stat.S_IRWXU+stat.S_IRGRP+stat.S_IXGRP+stat.S_IXOTH)
        return fil_ename
    # def clean_namedpipe(self,robj):
    #     if hasattr(robj,'fifow'):
    #         robj.fifow.close()
    #     if hasattr(robj,'fifor'):
    #         robj.fifor.close()
    #     if hasattr(self,'fifofile'):
    #         os.remove(filename)
    def generate_Pythonfile(self, source_filename, binary_filename, cflags=None, ldflags=None):
        return
    def _add_main(self, magics, code):
        # remove comments
        tmpCode = re.sub(r"//.*", "", code)
        tmpCode = re.sub(r"/\*.*?\*/", "", tmpCode, flags=re.M|re.S)
        x = re.search(r".*\s+main\s*\(", tmpCode)
        if not x:
            if self.__jkobj!=None and hasattr(self.__jkobj, 'main_head') and hasattr(self.__jkobj, 'main_foot'):
                code = self.__jkobj.get_main_head() + code + self.__jkobj.get_main_foot()
            else:
                code = self.main_head + code + self.main_foot
            # magics['_st']['cflags'] += ['-lm']
        return magics, code
    def raise_plugin(self,code,magics,returncode=None,filename='',ifunc=1,ieven=1)->Tuple[bool,str]:
        bcancel_exec=False
        bretcancel_exec=False
        retstr=''
        for pluginlist in self.plugins:
            for pkey,pvalue in pluginlist.items():
                # print( pkey +":"+str(len(pvalue))+"\n")
                for pobj in pvalue:
                    newline=''
                    try:
                        # if key in pobj.getIDSptag(pobj):
                        if ifunc==1 and ieven==1:
                                bretcancel_exec,retstr=pobj.on_before_buildfile(pobj,code,magics)
                        elif ifunc==2 and ieven==1:
                                bretcancel_exec,retstr=pobj.on_before_compile(pobj,code,magics)
                        elif ifunc==3 and ieven==1:
                                bretcancel_exec,retstr=pobj.on_before_exec(pobj,code,magics)
                        elif ifunc==1 and ieven==2:
                                bretcancel_exec=pobj.on_after_buildfile(pobj,returncode,filename,magics)
                        elif ifunc==2 and ieven==2:
                                bretcancel_exec=pobj.on_after_compile(pobj,returncode,filename,magics)
                        elif ifunc==3 and ieven==2:
                                bretcancel_exec=pobj.on_after_exec(pobj,returncode,filename,magics)
                        elif ifunc==3 and ieven==3:
                                bretcancel_exec=pobj.on_after_completion(pobj,returncode,filename,magics)        
                        bcancel_exec=bretcancel_exec & bcancel_exec
                        if bcancel_exec:
                            return bcancel_exec,""
                    except Exception as e:
                        self._log(pobj.getName(pobj)+"---"+str(e)+"\n")
                    finally:pass
        return bcancel_exec,retstr
##
    def do_execute_script(self, code, magics,silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        try:
            ##预处理
            bcancel_exec,retinfo,magics, code=self.__jkobj.do_preexecute(
                code,magics, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            
            return_code=0
            fil_ename=''
            retstr=''
            ##生成文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,1,1)
            if bcancel_exec:return  self.get_retinfo()
            ##生成代码文件
            bcancel_exec,retinfo,magics, code,fil_ename,retstr=self.__jkobj.do_create_codefile(
                magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            code,magics,return_code,fil_ename
            ##生成文件后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,1,2)
            if bcancel_exec:return  self.get_retinfo()
            fil_ename=magics['codefilename']
            if len(self.get_magicsbykey(magics,'noruncode'))>0:
                bcancel_exec=True
                return self.get_retinfo()
            ##编译文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,2,1)
            if bcancel_exec:return  self.get_retinfo()
            ##编译文件
            bcancel_exec,retinfo,magics, code,fil_ename,retstr=self.__jkobj.do_compile_code(
                return_code,fil_ename,magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return  retinfo
            ##编译文件后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,2,2)
            if bcancel_exec:return  self.get_retinfo()
            if len(self.get_magicsbykey(magics,'onlycompile'))>0:
                self._log("only run compile \n")
                bcancel_exec=True
                return retinfo
                
            ##运行文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,1)
            if bcancel_exec:return self.get_retinfo()
            ##运行代码
            self._logln("The process :"+fil_ename)
            bcancel_exec,retinfo,magics, code,fil_ename,retstr=self.__jkobj.do_runcode(
                return_code,fil_ename,magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            ##文件执行结束后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,3)
            if bcancel_exec:return self.get_retinfo()
        except Exception as e:
            self._log(""+str(e),3)
        return self.get_retinfo()
    def do_execute_class(self, code, magics,silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        try:
            return_code=0
            fil_ename=''
            outpath=''
            
            bcancel_exec,retinfo,magics, code=self.__jkobj.do_preexecute(
                code, magics,
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            return_code=0
            fil_ename=''
            
            ##生成文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,1,1)
            if bcancel_exec:return  self.get_retinfo()
            ##生成代码文件
            bcancel_exec,retinfo,magics, code,fil_ename,class_filename,outpath,retstr=self.do_create_codefile(
                magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            ##生成文件后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,1,2)
            if bcancel_exec:return  self.get_retinfo()
            fil_ename=magics['codefilename']
            if len(self.get_magicsbykey(magics,'noruncode'))>0:
                bcancel_exec=True
                return self.get_retinfo()
            
            ##编译文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,2,1)
            if bcancel_exec:return  self.get_retinfo()
            ##编译文件
            bcancel_exec,retinfo,magics, code,fil_ename,class_filename,outpath,retstr=self.__jkobj.do_compile_code(
                return_code,fil_ename,magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return  self.get_retinfo()
            ##编译文件后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,2,2)
            if bcancel_exec:return  self.get_retinfo()
            if len(self.get_magicsbykey(magics,'onlycompile'))>0:
                self._log("only run compile \n")
                bcancel_exec=True
                return retinfo
            ##运行文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,1)
            if bcancel_exec:return self.get_retinfo()
            ##运行代码
            self._logln("The process :"+class_filename)
            bcancel_exec,retinfo,magics, code,fil_ename,retstr=self.__jkobj.do_runcode(
                return_code,fil_ename,class_filename,outpath,magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            ##文件执行结束后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,3)
            if bcancel_exec:return self.get_retinfo()
        except Exception as e:
            self._log("???"+str(e),3)
        return self.get_retinfo()
    def do_execute_runprg(self, code, magics,silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        try:
            ##预处理
            bcancel_exec,retinfo,magics, code=self.dor_preexecute(
                code,magics, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            
            return_code=0
            fil_ename=''
            ##生成文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,1,1)
            if bcancel_exec:return  self.get_retinfo()
            ##生成代码文件
            bcancel_exec,retinfo,magics, code,fil_ename,retstr=self.dor_create_codefile(
                magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            ##生成文件后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,1,2)
            if bcancel_exec:return  self.get_retinfo()
            fil_ename=magics['codefilename']
            if len(self.get_magicsbykey(magics,'noruncode'))>0:
                bcancel_exec=True
                return self.get_retinfo()
            
            ##运行文件前通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,1)
            if bcancel_exec:return self.get_retinfo()
            ##运行代码
            self._logln("The process :"+fil_ename)
            bcancel_exec,retinfo,magics, code,fil_ename,retstr=self.dor_runcode(
                return_code,fil_ename,magics,code, 
                silent, store_history,user_expressions, allow_stdin)
            if bcancel_exec:return retinfo
            ##文件执行结束后通知插件
            bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,3)
            if bcancel_exec:return self.get_retinfo()
        except Exception as e:
            self._log(""+str(e),3)
        return self.get_retinfo()
##
    def dor_runcode(self,return_code,fil_ename,magics,code, silent, store_history=True,
                    user_expressions=None, allow_stdin=True):    
        ##runprg
        ##runprgargs
        return_code=return_code
        fil_ename=fil_ename
        bcancel_exec=False
        retinfo=self.get_retinfo()
        retstr=''
        runprg=self.get_magicsSvalue(magics,'runprg')
        runprgargs=self.get_magicsSvalue(magics,'runprgargs')
        if (len(runprgargs)<1):
            self._logln("No label runprgargs!",2)
        # self._logln(runprgargs[0])
        ##代码运行前
        p = self.create_jupyter_subprocess([runprg]+ runprgargs,cwd=None,shell=False,env=self.addkey2dict(magics,'env'),magics=magics)
        self.g_rtsps[str(p.pid)]=p
        return_code=p.returncode
        ##代码启动后
        bcancel_exec,retstr=self.raise_plugin(code,magics,return_code,fil_ename,3,2)
        
        if len(self.addkey2dict(magics,'showpid'))>0:
            self._logln("The process PID:"+str(p.pid))
        return_code=p.wait_end(magics)
        # self._logln("The process end:"+str(p.pid))
        ##
        ##调用接口
        # return_code=p.returncode
        ##代码运行结束
        if p.returncode != 0:
            self._logln("Executable exited with code {}".format(p.returncode),2)
        return bcancel_exec,retinfo,magics, code,fil_ename,retstr
    def dor_create_codefile(self,magics,code, silent, store_history=True,
                    user_expressions=None, allow_stdin=True):    
        ##runprg
        ##runprgargs
        return_code=0
        fil_ename=''
        bcancel_exec=False
        retinfo=self.get_retinfo()
        retstr=''
        ##调生成文件前接口
        source_file=self.create_codetemp_file(magics,code,suffix='.sh')
        newsrcfilename=source_file.name
        fil_ename=newsrcfilename
        return_code=True
        
        return bcancel_exec,retinfo,magics, code,fil_ename,retstr
    def dor_preexecute(self,code,magics,silent, store_history=True,
                user_expressions=None, allow_stdin=False):        
        ##runprg
        ##runprgargs
        bcancel_exec=False
        retinfo=self.get_retinfo()
        return bcancel_exec,retinfo,magics, code
##
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        if self.first_cellcodeinfo==None:
            self.first_cellcodeinfo={
                "code":code, 
                "silent":silent, 
                "store_history":store_history,
                "user_expressions":user_expressions,
                "allow_stdin":allow_stdin
            }
        retinfo= self.do_executecode(code)
        self.do_atparentexit(self.first_magics)
        rpcsrvfollowcode=''
        if self.first_magics!=None:
            rpcsrvfollowcode=self.get_magicsBvalue(self.first_magics,'rpcsrvfollowcode')
        if len(rpcsrvfollowcode)>0 and self.__rpcsrv != None:
            self.stop_srvmode()
        if self.__rpcsrv != None:
            self._rpcsrv_thread.join()
        self.__rpcsrv =None
        self._rpcsrv_thread = None
        return retinfo
    def run_forlist(self,magics):
        runforlist=self.get_magicsSvalue(magics,'runforlist')
        if len(runforlist)>0:
            self._run_forlist(runforlist,magics,singlecell=False)
        return
    def _run_forlist(self,files:List,magics,singlecell=True)->str:
        def runcellcode(fileitem,origcwd):
            try:
                cwd=origcwd
                filename,code=ipynbfile.loadnb(fileitem)
                if code==None or len(code.strip())<1:
                    return False
                if filename!=None and len(filename.strip())>0:
                    cwd=os.path.dirname(filename)
                if cwd==None or len(cwd.strip())<1:
                    cwd=origcwd
                os.chdir(cwd)
                self.do_executecode(code)
                os.chdir(origcwd)
            except Exception as e:
                os.chdir(origcwd)
                self._log(str(e),2)
            return True
        origcwd=os.getcwd()
        index=-1
        try:
            if(len(files)<1):return 
            for sli in files:
                cwd=origcwd
                fileitem=sli
                self._logln("---------\nExecute associated fileitem:"+fileitem)
                if not singlecell:
                    fcellcount=ipynbfile.getnbcodecount(fileitem)
                    index=0
                    while index<fcellcount:
                        realfileitem=fileitem+" "+str(index)
                        runcellcode(realfileitem,origcwd)
                        index+=1
                else:
                    if not runcellcode(fileitem,origcwd):continue
                os.chdir(origcwd)
        except Exception as e:
                self._log(str(e),2)
        os.chdir(origcwd)
        return 
    def run_assfile(self,magics):
        files=self.get_magicsSvalue(magics,'assfile')
        if(len(files)<1):return 
        self._run_forlist(files,magics)
        return
    def do_retryexeccode(self):
        if self.cellcodeinfo!=None:
            self.do_executecode(self.first_cellcodeinfo['code'])
    def do_atparentexit(self,magics):
        self.run_forlist(magics)
        self.run_assfile(magics)
        self.srmsgafterexec(magics)
        self.smsgafterexec(magics)
    def do_atexit(self,magics):
        pass
    def do_executecode(self, code):
        silent=None
        store_history=True
        user_expressions=None
        allow_stdin=True
        if self.first_cellcodeinfo!=None:
            silent=self.first_cellcodeinfo['silent']
            store_history=self.first_cellcodeinfo['store_history'],
            user_expressions=self.first_cellcodeinfo['user_expressions']
            allow_stdin=self.first_cellcodeinfo['allow_stdin']
        self._put2stdin_queue = Queue(maxsize=1024)
        self.silent = silent
        retinfo=self.get_retinfo()
        if len(code.strip())<1:return retinfo
        magics, code = self.mag.filter(code)
        if self.first_magics==None:
            self.first_magics={}
            self.first_magics=magics.copy()
            self.first_magics['_sline']=copy.deepcopy(magics['_sline'])
            self.first_magics['_bt']=copy.deepcopy(magics['_bt'])
            self.first_magics['_dt']=copy.deepcopy(magics['_dt'])
            self.first_magics['_st']=copy.deepcopy(magics['_st'])
        rurl=self.get_magicsSvalue(magics,'srvmode')
        if rurl!=None and len(rurl)>0 and self.__rpcsrv == None:
            rpcsrvobj=RPCsrv(self,magics)
            self.start_srvmode(magics,rpcsrvobj)
        if (len(self.get_magicsbykey(magics,'onlyrunmagics'))>0 or len(self.get_magicsbykey(magics,'onlyruncmd'))>0):
            bcancel_exec=True
            self.do_atexit(magics)
            return retinfo
        if len(self.get_magicsBvalue(magics,'replcmdmode'))>0:
            bcancel_exec=True
            retinfo= self.send_replcmd(code, silent, store_history,user_expressions, allow_stdin)
            self.do_atexit(magics)
            return retinfo
        
        if(len(self.get_magicsSvalue(magics,'runprg'))>0):
            retinfo=self.do_execute_runprg(code, magics,silent, store_history,
                   user_expressions, allow_stdin)
            self.cleanup_files()
            self.do_atexit(magics)
            return retinfo
        if(self.runfiletype=='script'):
            retinfo=self.do_execute_script(code, magics,silent, store_history,
                   user_expressions, allow_stdin)
        elif(self.runfiletype=='class'):
            retinfo=self.do_execute_class(code, magics,silent, store_history,
                   user_expressions, allow_stdin=True)
        elif(self.runfiletype=='exe'):
            retinfo=self.do_execute_script(code, magics,silent, store_history,
                   user_expressions, allow_stdin)
        
        self.do_atexit(magics)
        self.cleanup_files()
        return retinfo
    def srmsgafterexec(self,magics):
        srmafterexec=self.get_magicsSvalue(magics,'srmafterexec')
        if len(srmafterexec)<1 :return
        msg=''
        rpcurl=''
        outencode='UTF-8'
        outencode=self.get_outencode(magics)
        if(outencode==None or len(outencode)<0):outencode='UTF-8'
        for sli in srmafterexec:
            if len(sli.strip())<1:continue
            li=sli.split(" ", 1)
            if len(li)<2:continue
            rpcurl=li[0]
            msg=li[1]+"\n"
            self.send_stdincmd(magics,rpcurl,msg)
    def smsgafterexec(self,magics):
        smafterexec=self.get_magicsSvalue(magics,'smafterexec')
        if len(smafterexec)<1 :return
        msg=''
        fifoname=''
        outencode='UTF-8'
        outencode=self.get_outencode(magics)
        if(outencode==None or len(outencode)<0):outencode='UTF-8'
        for sli in smafterexec:
            if len(sli.strip())<1:continue
            li=sli.split(" ", 1)
            if len(li)<2:continue
            fifoname=li[0]
            msg=li[1]+"\n"
            self.sendmsg(fifoname,msg,outencode)
    def sendmsg(self,fifoname,msg='',outencode='UTF-8'):
        if len(fifoname.strip())<1 or len(msg)<1 :return
        contents=msg.encode(outencode, errors='ignore')
        
        self.sendmsg2sh(fifoname.strip(),4096,contents)
##
    def do_shutdown(self):
        self.g_chkreplexit=False
        self.chk_replexit_thread.join()
        self.cleanup_files()
        self.reset()
##
    def sendmsg2sh(self,name,memsize,content,robj=None):
        if self.flock==None:self.flock=CFileLock(name)
        def iswrite_state(m,bsf=b'\x00'):
            ret=False
            flag=b''
            m.seek(0)
            flag=m.read(1)
            if flag==bsf:return True
            return ret
        def waitwrite_state(m,timeout):
            self.timeout(to=timeout,
                retryfunc=iswrite_state,
                condfunc=None,
                argdict={"args":(m,b'\x00'),
                    "kwargs":None,
                    "cargs":None,
                    "ckwargs":None
                })
        def writedata(m,content,robj=None):
            ret=False
            if self.flock.lock():
                waitwrite_state(m,1)
                m.seek(0)
                m.write(b'\x02')
                m.flush()
                m.seek(1)
                m.write(content)
                m.flush()
                m.seek(0)
                m.write(b'\x01')
                m.flush()
                time.sleep(1/1000)
                # m.seek(1)
                # w=m.read()
                # ww=w.decode()
                # if robj==None:
                #     self._logln(ww.strip(b'\x00'.decode()))
                if robj!=None:robj._sendend=True
                self.flock.unlock()
                ret=True
            return ret
        bret=False
        with contextlib.closing(mmap.mmap(-1, memsize, tagname=name, access=mmap.ACCESS_DEFAULT)) as m:
            bret=self.timeout(to=5,
                retryfunc=writedata,
                condfunc=None,
                argdict={"args":(m,content,None),
                    "kwargs":None,
                    "cargs":None,
                    "ckwargs":None
                })
        return bret
    def readdatafromsh(self,queue,name,memsize=1024,outencode='UTF-8'):
        def isread_state(m,bsf=b'\x01'):
            ret=False
            flag=b''
            m.seek(0)
            flag=m.read(1)
            if flag==bsf:return True
            return ret
        def waitread_state(m,timeout):
            return self.timeout(to=timeout,
                retryfunc=isread_state,
                condfunc=None,
                argdict={"args":(m,b'\x01'),
                    "kwargs":None,
                    "cargs":None,
                    "ckwargs":None
                })
        def readdata(m,queue,memsize):
            ret=False
            if self.flock.lock():
                bret=waitread_state(m,1)
                if not bret:
                    self.flock.unlock()
                    return 
                m.seek(0)
                m.write(b'\x02')
                m.flush()
                m.seek(1)
                content = m.read()
                cstr=content.decode(outencode, errors='ignore').strip(b'\x00'.decode())
                if (len(cstr)>1):
                    queue.put(cstr.encode(outencode, errors='ignore'))
                m.seek(0)
                m.write(b'\x00'*memsize)
                m.flush()
                time.sleep(1/1000)
                self.flock.unlock()
                ret=True
            return ret
        bret=False
        with contextlib.closing(mmap.mmap(-1, memsize, tagname=name, access=mmap.ACCESS_DEFAULT)) as m:
            bret=self.timeout(to=5,
                retryfunc=readdata,
                condfunc=None,
                argdict={"args":(m,queue,memsize),
                    "kwargs":None,
                    "cargs":None,
                    "ckwargs":None
                })
        return bret
    def timeout(self,to=60,retryfunc=None,condfunc=None,argdict=
                {"args":None,
                 "kwargs":None,
                 "cargs":None,
                 "ckwargs":None
                }):
        bret=False
        cmdstart_time = time.time()
        while True:
            try:
                if condfunc!=None and condfunc(*argdict["cargs"]):break
                run_time = time.time() - cmdstart_time
                if run_time > to:break
                time.sleep(1/1000)
                if retryfunc!=None and retryfunc(*argdict["args"]):
                    bret=True
                    break
                continue
            except Exception as e:
                break
        return bret
     
    def start_srvmode(self,magics,rpcsrvobj,rpcurl=None):
        if self._rpcsrv_thread != None:
            return
        self._rpcsrv_thread = Thread(target=MyMagics.rpc_srv, args=(self,magics,rpcsrvobj,rpcurl))
        self._rpcsrv_thread.daemon = True
        self._rpcsrv_thread.start()
        self._logln("srvmode start...")
    def rpc_srv(kobj,magics,rpcsrvobj,rpcurl=None):
        rurl=rpcurl
        # kobj.__rpcsrv = None
        if rpcurl==None:
            rurl=kobj.get_magicsSvalue(magics,'srvmode')
        if rpcsrvobj!=None and rurl!=None and len(rurl)>0:
            try:
                kobj.__rpcsrv = zerorpc.Server(rpcsrvobj)
                kobj.__rpcsrv._context.setsockopt(socket.SO_REUSEADDR, 1)
                kobj.__rpcsrv.bind(rurl)
                kobj.__rpcsrv.run()
            except Exception as e:
                kobj._logln("start_srvmode err:"+str(e),3)
                if kobj.__rpcsrv!=None :kobj.__rpcsrv.close()
        return 
    def stop_srvmode(self):
        if self.__rpcsrv!=None :
            try:
                rurl=self.get_magicsSvalue(self.first_magics,'srvmode')
                self.__rpcsrv.disconnect(rurl)
                self.__rpcsrv.stop()
                self.__rpcsrv.close()
                self.__rpcsrv._context.destroy()
                # self._put2stdin_queue = None
            except Exception as e:
                pass
        # self._rpcsrv_thread.join()
    def get_rpcsrvobj(self,magics,rpcurl=None):
        rpcsrvobj=None
        if rpcurl==None:
            rpcurl=self.get_magicsSvalue(magics,'srvurl')
        if rpcurl!=None and len(rpcurl)>0:
            try:
                rpcsrvobj = zerorpc.Client()
                rpcsrvobj.connect(rpcurl)
            except Exception as e:
                if rpcsrvobj!=None :rpcsrvobj.close()
                rpcsrvobj=None
        return rpcsrvobj
    def send_stdincmd(self,magics,rpcurl,cmdstr):
        if rpcurl==None or len(rpcurl.strip())<3:
            rpcurl=self.get_magicsSvalue(magics,'srvurl')
        if rpcurl!=None and len(rpcurl.strip())>0:
            try:
                rpcsrvobj=self.get_rpcsrvobj(magics,rpcurl)
                if rpcsrvobj!=None:
                    rpcsrvobj.stdincmd(cmdstr)
                    rpcsrvobj.close()
            except Exception as e:
                pass
    def send_cmd(self,magics,rpcurl,cmdstr):
        if rpcurl==None or len(rpcurl.strip())<3:
            rpcurl=self.get_magicsSvalue(magics,'srvurl')
        if rpcurl!=None and len(rpcurl.strip())>0:
            try:
                rpcsrvobj=self.get_rpcsrvobj(magics,rpcurl)
                if rpcsrvobj!=None:
                    rpcsrvobj.cmd(cmdstr)
                    rpcsrvobj.close()
            except Exception as e:
                pass
    def exec_rpccmd(self,magics,rpcurl=None,func=None,*args,**kwargs):
        if self.rpcsrvobj==None and rpcurl!=None and len(rpcurl)>0:
            self.rpcsrvobj=self.get_rpccli(magics,rpcurl=rpcurl)
        if self.rpcsrvobj!=None and func!=None:
            ret=func(*args,**kwargs)
            return ret
        return None
##
    def pluginRegister(self,obj):
        if obj==None:return
        try:
            obj.setKernelobj(obj,self)
            priority=obj.getPriority(obj)
            if not inspect.isabstract(obj) and issubclass(obj,IStag):
                self.ISplugins[str(priority)]+=[obj]
            elif not inspect.isabstract(obj) and issubclass(obj,IDtag):
                self.IDplugins[str(priority)]+=[obj]
            elif not inspect.isabstract(obj) and issubclass(obj,IBtag):
                self.IBplugins[str(priority)]+=[obj]
            elif not inspect.isabstract(obj) and issubclass(obj,ICodePreproc):
                self.ICodePreprocs[str(priority)]+=[obj]
        except Exception as e:
            pass
        pass
    def pluginISList(self):
        self._log("---------pluginISList--------\n")
        for key,value in self.ISplugins.items():
            # print( key +":"+str(len(value))+"\n")
            for obj in value:
                self._log(obj.getName(obj)+"\n")
    def pluginIDList(self):
        self._log("---------pluginIDList--------\n")
        for key,value in self.IDplugins.items():
            # print( key +":"+str(len(value))+"\n")
            for obj in value:
                self._log(obj.getName(obj)+"\n")
    def pluginIBList(self):
        self._log("---------pluginIBList--------\n")
        for key,value in self.IBplugins.items():
            # print( key +":"+str(len(value))+"\n")
            for obj in value:
                self._log(obj.getName(obj)+"\n")
    def onkernelshutdown(self,restart):
        for key,value in self.IDplugins.items():
            # print( key +":"+str(len(value))+"\n")
            for obj in value:
                try:
                    newline=obj.on_shutdown(obj,restart)
                    if newline=='':break
                except Exception as e:
                    pass
                finally:pass
    def callIDplugin(self,magics,line):
        newline=line
        for key,value in self.IDplugins.items():
            # print( key +":"+str(len(value))+"\n")
            for obj in value:
                try:
                    newline=obj.on_IDpReorgCode(obj,magics,newline)
                    if newline=='':break
                except Exception as e:
                    pass
                finally:pass
        return newline
    def init_plugin(self):
        mypath = os.path.dirname(os.path.abspath(__file__))
        idir=os.path.join(mypath,'../plugins')
        sys.path.append(mypath)
        sys.path.append(idir)
        for f in os.listdir(idir):
            if os.path.isfile(os.path.join(idir,f)):
                try:
                    name=os.path.splitext(f)[0]
                    if name!='pluginmng' and name!='kernel' and(spec := importlib.util.find_spec(name)) is not None:
                        module = importlib.import_module(name)
                        for name1, obj in inspect.getmembers(module,
                            lambda obj: 
                                callable(obj) 
                                and inspect.isclass(obj) 
                                and not inspect.isabstract(obj) 
                                and issubclass(obj,ITag)
                                ):
                            # self._write_to_stdout("\n"+obj.__name__+"\n")
                            self.pluginRegister(obj)
                    else:
                        pass
                except Exception as e:
                    pass
                finally:
                    pass
    def _start_gdb(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that bash and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            if hasattr(self, 'gdbwrapper'):
                if not self.gdbwrapper.child.terminated:
                    return
        finally:
            pass
        try:
            # self._write_to_stdout("------exec gdb-----\n")
            child = pexpect.spawn('gdb', ['-q'], echo=False,encoding='utf-8')
            self.gdbwrapper = IREPLWrapper(
                                    self._write_to_stdout,
                                    self._write_to_stderr,
                                    self._read_from_stdin,
                                    child, 
                                    replsetip=u'(gdb)',
                                    orig_prompt=u'(gdb)',
                                    prompt_change=None,
                                    extra_init_cmd='set pagination off',
                                    line_output_callback=self.process_output)
        except Exception as e:
            self._logln(" IREPLWrapper error! \n"+str(e))
            exitcode = 1
        finally:
            signal.signal(signal.SIGINT, sig)
    def do_replexecutegdb(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        self.silent = silent
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
        interrupted = False
        try:
            # Note: timeout=None tells IREPLWrapper to do incremental
            # output.  Also note that the return value from
            # run_command is not needed, because the output was
            # already sent by IREPLWrapper.
            self.gdbwrapper.run_command(code.rstrip(), timeout=None)
        except KeyboardInterrupt:
            self.gdbwrapper.child.sendintr()
            interrupted = True
            self.gdbwrapper._expect_prompt()
            output = self.gdbwrapper.child.before
            self.process_output(output)
        except EOF:
            output = self.gdbwrapper.child.before + 'Restarting GDB'
            self._start_gdb()
            self.process_output(output)
        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}
        try:
            if code.rstrip().startswith('shell'):
                exitcode = int(self.gdbwrapper.run_command('shell echo $?').rstrip())
            else:
                exitcode = int(self.gdbwrapper.run_command('echo $?').rstrip())
        except Exception:
            exitcode = 1
        if exitcode:
            error_content = {'execution_count': self.execution_count,
                             'ename': '', 'evalue': str(exitcode), 'traceback': []}
            self.send_response(self.iopub_socket, 'error', error_content)
            error_content['status'] = 'error'
            return error_content
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
    def replgdb_sendcmd(self,code,silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        self._start_gdb()
        return self.do_replexecutegdb( code.replace('//%rungdb', ''), silent, store_history,
                   user_expressions, False)
