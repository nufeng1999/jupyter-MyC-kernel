##
# MyPython Jupyter Kernel
##
from ipykernel.kernelbase import Kernel
from .MyMagics import *
from plugins._filter2_magics import Magics
import platform
import sys
class MyKernel(Kernel):
    implementation = 'jupyter-MyPython-kernel'
    implementation_version = '1.0'
    language = 'Python'
    language_version = sys.version.split()[0]
    language_info = {'name': 'python',
                     'version': sys.version.split()[0],
                     'mimetype': 'text/x-python',
                     'codemirror_mode': {
                         'name': 'ipython',
                         'version': sys.version_info[0]
                     },
                     'pygments_lexer': 'ipython%d' % 3,
                     'nbconvert_exporter': 'python',
                     'file_extension': '.py'}
    banner = "MyPython kernel.\n" \
             "Uses , compiles in , and creates source code files and executables in temporary folder.\n"
    kernelinfo = "[MyPython]"
    main_head = "\n" \
        "\n" \
        "int main(List<String> arguments){\n"
    main_foot = "\nreturn 0;\n}"
    def __init__(self, *args, **kwargs):
        super(MyKernel, self).__init__(*args, **kwargs)
        self.runfiletype = 'script'
        self.kernelinfo = '[MyKernel]'
        self.mymagics = MyMagics(jkobj=self, runfiletype=self.runfiletype)
    def get_language_info(self):
        return self.language_info
    def get_runfiletype(self) -> str:
        return self.runfiletype
    def get_kernelinfo(self) -> str:
        return self.kernelinfo
    def get_main_head(self) -> str:
        return self.main_head
    def get_main_foot(self) -> str:
        return self.main_foot
    def get_mymagics(self):
        return self.mymagics
    def set_mymagics(self, object):
        self.mymagics = object
    def get_execution_count(self):
        return self.execution_count
    # 按 mimetype 格式输出显示内容
    def rawinput(self):
        if len(self.__independent) > 0:
            return sys.stdin.readline()
        elif len(self.__independent) < 1:
            return self.get_raw_input()
        return self.get_raw_input()
    def sendresponse(self, contents,name='stdout',mimetype=None):
        if mimetype ==None:
            self.send_response(self.iopub_socket, 'stream', {
                                'name': name, 'text': contents})
        else:
            self.send_response(self.iopub_socket, 'display_data', {'data': {mimetype: contents}, 'metadata': {mimetype:{}}})
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        retinfo = self.mymagics.do_execute(
            code, silent,
            store_history=store_history,
            user_expressions=user_expressions,
            allow_stdin=allow_stdin)
        self.mymagics.do_shutdown()
        return retinfo
    def do_shutdown(self, restart):
        pass
