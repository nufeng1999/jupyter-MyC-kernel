from queue import Queue
from threading import Thread

from ipykernel.kernelbase import Kernel
import re
import subprocess
import tempfile
import os
import sys
import traceback
import os.path as path


class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    inputRequest = "<inputRequest>"

    def __init__(self, cmd, write_to_stdout, write_to_stderr, read_from_stdin,cwd=None,shell=False):
        """
        :param cmd: the command to execute
        :param write_to_stdout: a callable that will be called with chunks of data from stdout
        :param write_to_stderr: a callable that will be called with chunks of data from stderr
        """
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr
        self._read_from_stdin = read_from_stdin

        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=0,cwd=cwd,shell=shell)

        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    @staticmethod
    def _enqueue_output(stream, queue):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()

    def write_contents(self):
        """
        Write the available content from stdin and stderr where specified when the instance was created
        :return:
        """

        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res

        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            self._write_to_stderr(stderr_contents.decode())

        stdout_contents = read_all_from_queue(self._stdout_queue)
        if stdout_contents:
            contents = stdout_contents.decode()
            # if there is input request, make output and then
            # ask frontend for input
            start = contents.find(self.__class__.inputRequest)
            if(start >= 0):
                contents = contents.replace(self.__class__.inputRequest, '')
                if(len(contents) > 0):
                    self._write_to_stdout(contents)
                readLine = ""
                while(len(readLine) == 0):
                    readLine = self._read_from_stdin()
                # need to add newline since it is not captured by frontend
                readLine += "\n"
                self.stdin.write(readLine.encode())
            else:
                self._write_to_stdout(contents)


class CKernel(Kernel):
    implementation = 'jupyter_c_kernel'
    implementation_version = '1.0'
    language = 'C'
    language_version = 'C11'
    language_info = {'name': 'text/x-csrc',
                     'mimetype': 'text/x-csrc',
                     'file_extension': '.c'}
    banner = "C kernel.\n" \
             "Uses gcc, compiles in C11, and creates source code files and executables in temporary folder.\n"

    main_head = "#include <stdio.h>\n" \
            "#include <math.h>\n" \
            "int main(int argc, char* argv[], char** env){\n"

    main_foot = "\nreturn 0;\n}"

    def __init__(self, *args, **kwargs):
        super(CKernel, self).__init__(*args, **kwargs)
        self._allow_stdin = True
        self.readOnlyFileSystem = False
        self.bufferedOutput = True
        self.linkMaths = True # always link math library
        self.wAll = True # show all warnings by default
        self.wError = False # but keep comipiling for warnings
        self.files = []
        mastertemp = tempfile.mkstemp(suffix='.out')
        os.close(mastertemp[0])
        self.master_path = mastertemp[1]
        self.resDir = path.join(path.dirname(path.realpath(__file__)), 'resources')
        filepath = path.join(self.resDir, 'master.c')
        subprocess.call(['gcc', filepath, '-std=c11', '-rdynamic', '-ldl', '-o', self.master_path])

    def cleanup_files(self):
        """Remove all the temporary files created by the kernel"""
        # keep the list of files create in case there is an exception
        # before they can be deleted as usual
        for file in self.files:
            if(os.path.exists(file)):
                os.remove(file)
        os.remove(self.master_path)

    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file

    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': contents})

    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': contents})

    def _read_from_stdin(self):
        return self.raw_input()

    def readcodefile(self,filename,spacecount=0):
        filecode=''
        codelist1=None
        with open(os.path.join(os.path.abspath(''),filename), 'r') as codef1:
            codelist1 = codef1.readlines()
        if len(codelist1)>0:
            for t in codelist1:
                filecode+=' '*spacecount + t
        return filecode
   
    def do_shell_command(self,commands,cwd=None,shell=True):
        # self._write_to_stdout(''.join((' '+ str(s) for s in commands)))
        try:
            p = RealTimeSubprocess(commands,
                                  self._write_to_stdout,
                                  self._write_to_stderr,
                                  self._read_from_stdin,cwd,shell)
            while p.poll() is None:
                p.write_contents()
            # wait for threads to finish, so output is always shown
            p._stdout_thread.join()
            p._stderr_thread.join()

            p.write_contents()

            if p.returncode != 0:
                self._write_to_stderr("[C kernel] Error: Executable command exited with code {}".format(p.returncode))
            else:
                self._write_to_stdout("[C kernel] Info: command success.")
            return
        except Exception as e:
            self._write_to_stderr("[C kernel] Error:Executable command error! "+str(e))
    
    def create_jupyter_subprocess(self, cmd,cwd=None,shell=False):
        return RealTimeSubprocess(cmd,
                                  self._write_to_stdout,
                                  self._write_to_stderr,
                                  self._read_from_stdin,cwd,shell)
    
    def generate_file(self, source_filename, binary_filename, cflags=None, ldflags=None):

        return
    
    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(cmd,
                                  self._write_to_stdout,
                                  self._write_to_stderr,
                                  self._read_from_stdin)

    def compile_with_gcc(self, source_filename, binary_filename, cflags=None, ldflags=None):
        # cflags = ['-std=c89', '-pedantic', '-fPIC', '-shared', '-rdynamic'] + cflags
        # cflags = ['-std=c99', '-Wdeclaration-after-statement', '-Wvla', '-fPIC', '-shared', '-rdynamic'] + cflags
        # cflags = ['-std=iso9899:199409', '-pedantic', '-fPIC', '-shared', '-rdynamic'] + cflags
        # cflags = ['-std=c99', '-pedantic', '-fPIC', '-shared', '-rdynamic'] + cflags
        # cflags = ['-std=c11', '-pedantic', '-fPIC', '-shared', '-rdynamic'] + cflags
        outfile=''
        if self.linkMaths:
            cflags = cflags + ['-lm']
        if self.wError:
            cflags = cflags + ['-Werror']
        if self.wAll:
            cflags = cflags + ['-Wall']
        if self.readOnlyFileSystem:
            cflags = ['-DREAD_ONLY_FILE_SYSTEM'] + cflags
        if self.bufferedOutput:
            cflags = ['-DBUFFERED_OUTPUT'] + cflags

        for s in cflags:
                if s.startswith('-o'):
                    if(len(s)>2):
                        outfile=s[2:]
                    else:
                        outfile=cflags[cflags.index('-o')+1]
                        if outfile.startswith('-'):
                            outfile=binary_filename
                binary_filename=outfile
        args = ['gcc', source_filename] + cflags + ['-o', binary_filename] + ldflags
        # self._write_to_stdout(''.join((' '+ str(s) for s in args))+"\n")
        return self.create_jupyter_subprocess(args),binary_filename,args

    def _filter_magics(self, code):

        magics = {'cflags': [],
                  'ldflags': [],
                  'file': [],
                  'norun': [],
                  'include': [],
                  'command': [],
                  'args': []}

        actualCode = ''

        for line in code.splitlines():
            orgline=line
            if line.strip().startswith('//%'):
                if line.strip()[3:] == "norun":
                    magics['norun'] += ['true']
                    continue

                key, value = line.strip()[3:].split(":", 2)
                key = key.strip().lower()

                if key in ['ldflags', 'cflags']:
                    for flag in value.split():
                        magics[key] += [flag]
                elif key == "file":
                    for flag in value.split():
                        magics[key] += [flag]
                elif key == "include":
                    for flag in value.split():
                        magics[key] += [flag]
                    if len(magics['include'])>0:
                        index1=line.find('//%')
                        line=self.readcodefile(magics['include'][0],index1)
                        actualCode += line + '\n'
                elif key == "command":
                    # for flag in value.split():
                    magics[key] += [value]
                    if len(magics['command'])>0:
                        self.do_shell_command(magics['command'])
                elif key == "args":
                    # Split arguments respecting quotes
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        magics['args'] += [argument.strip('"')]

                # always add empty line, so line numbers don't change
                actualCode += '\n'

            # keep lines which did not contain magics
            else:
                actualCode += line + '\n'

        return magics, actualCode
    # check whether int main() is specified, if not add it around the code
    # also add common magics like -lm
    def _add_main(self, magics, code):
        # remove comments
        tmpCode = re.sub(r"//.*", "", code)
        tmpCode = re.sub(r"/\*.*?\*/", "", tmpCode, flags=re.M|re.S)

        x = re.search(r".*\s+main\s*\(", tmpCode)

        if not x:
            code = self.main_head + code + self.main_foot
            magics['cflags'] += ['-lm']

        return magics, code
    def _exec_gcc_(self,source_filename,magics):
        with self.new_temp_file(suffix='.out') as binary_file:
            p,outfile,gcccmd = self.compile_with_gcc(source_filename, binary_file.name, magics['cflags'], magics['ldflags'])
            while p.poll() is None:
                p.write_contents()
            p.write_contents()
            binary_file.name=os.path.join(os.path.abspath(''),outfile)
            if p.returncode != 0:  # Compilation failed
                self._write_to_stdout(''.join((' '+ str(s) for s in gcccmd))+"\n")
                self._write_to_stderr("[C kernel] GCC exited with code {}, the executable will not be executed".format(p.returncode))

                # delete source files before exit
                os.remove(source_filename)
                os.remove(binary_file.name)
        return p.returncode,binary_file.name
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
 
        magics, code = self._filter_magics(code)
        if len(magics['norun'])<1:
            magics, code = self._add_main(magics, code)

        # magics, code = self._add_main(magics, code)

        # replace stdio with wrapped version
        # headerDir = "\"" + self.resDir + "/stdio_wrap.h" + "\""
        # code = code.replace("<stdio.h>", headerDir)
        # code = code.replace("\"stdio.h\"", headerDir)

        with self.new_temp_file(suffix='.c') as source_file:
            source_file.write(code)
            source_file.flush()
            newsrcfilename=source_file.name

            # if len(magics['norun'])>0:
            if len(magics['file'])>0:
                newsrcfilename = magics['file'][0]
                # for x in jfile: self._write_to_stderr("file " + x + " ")
                os.rename(source_file.name,os.path.join(os.path.abspath(''),newsrcfilename))
                newsrcfilename=os.path.join(os.path.abspath(''),newsrcfilename)
                self._write_to_stdout("[C kernel] Info:file created successfully\n")
            if len(magics['norun'])>0:
                if len(magics['file'])<1:
                    self._write_to_stderr("[C kernel] Warning: no file name parameter\n")
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
            returncode,binary_filename=self._exec_gcc_(newsrcfilename,magics)
            if returncode!=0:
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],'user_expressions': {}}
        # p = self.create_jupyter_subprocess([self.master_path, binary_file.name] + magics['args'])
        p = self.create_jupyter_subprocess([binary_filename] + magics['args'])
        while p.poll() is None:
            p.write_contents()

        # wait for threads to finish, so output is always shown
        p._stdout_thread.join()
        p._stderr_thread.join()

        p.write_contents()

        # now remove the files we have just created
        if len(magics['file'])<1:
            os.remove(newsrcfilename)
            os.remove(binary_filename)

        if p.returncode != 0:
            self._write_to_stderr("[C kernel] Executable exited with code {}".format(p.returncode))
        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        self.cleanup_files()
