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
    kernelinfo="[MyPython]"
    main_head = "\n" \
            "\n" \
            "int main(List<String> arguments){\n"
    main_foot = "\nreturn 0;\n}"
    def __init__(self, *args, **kwargs):
        super(MyKernel, self).__init__(*args, **kwargs)
        self.runfiletype='script'
        self.mymagics=MyMagics(jkobj=self,runfiletype=self.runfiletype)
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=True):
        # mymagics=MyMagics(jkobj=self,runfiletype=self.runfiletype)
        # self.mymagics=mymagics
        retinfo = self.mymagics.do_execute(
            code, silent, 
            store_history=store_history,
            user_expressions=user_expressions, 
            allow_stdin=allow_stdin)
        self.mymagics.do_shutdown()
        return retinfo
    def do_shutdown(self, restart):
        pass
