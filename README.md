# MyC kernel for Jupyter
[Example](https://github.com/nufeng1999/jupyter-MyC-kernel/blob/master/example/jupyter_MyC_readme.ipynb "Example")
* Make sure you have the following requirements installed:
  * C
  * jupyter
  * python 3
  * pip
### Step-by-step
```bash
git clone https://github.com/nufeng1999/jupyter-MyC-kernel.git
cd jupyter-MyC-kernel
pip install -e . 
cd jupyter_MyC_kernel && python3 install_MyC_kernel --user
# now you can start the notebook
jupyter notebook
```
My minification kelnel of jupyter
|                   |                 |
| :--------------------------------------------------------------------- | :--------------------------------------------------------------------- |
|[MyBash](https://github.com/nufeng1999/jupyter-MyBash-kernel)           |[MyC](https://github.com/nufeng1999/jupyter-MyC-kernel)                 |
|[MyDart](https://github.com/nufeng1999/jupyter-MyDart-kernel)           |[MyGjs](https://github.com/nufeng1999/jupyter-MyGjs-kernel)             |
|[MyGo](https://github.com/nufeng1999/jupyter-MyGo-kernel)               |[MyGroovy](https://github.com/nufeng1999/jupyter-MyGroovy-kernel)       |
|[MyJava](https://github.com/nufeng1999/jupyter-MyJava-kernel)           |[MyKotlin](https://github.com/nufeng1999/jupyter-MyKotlin-kernel)       |
|[MyNodejs](https://github.com/nufeng1999/jupyter-MyNodejs-kernel)       |[MyPython](https://github.com/nufeng1999/jupyter-MyPython-kernel)       |
|[MyVala](https://github.com/nufeng1999/jupyter-MyVala-kernel)           |[MyVBScript](https://github.com/nufeng1999/jupyter-MyVBScript-kernel)   |
|[MyWolframScript](https://github.com/nufeng1999/jupyter-MyWLS-kernel)   |[MyVBScript](https://github.com/nufeng1999/jupyter-MyHtml-kernel)       |  
|[MyTypeScript](https://github.com/nufeng1999/jupyter-MyTypeScript-kernel)|[MyPowerShell](https://github.com/nufeng1999/jupyter-MyPS-kernel)|
|[MyBatch](https://github.com/nufeng1999/jupyter-MyBatch-kernel)| |
  
----  
### Support label  
#### Label  
Label prefix is `##%` or `//%`  
Example1:   
`##%overwritefile`  
`##%file:../src/do_execute.c`  
`##%noruncode`  
Example2:   
`##%runprg:ls`  
`##%runprgargs:-al`  
Example3:   
`##//%outputtype:text/html`  
`##%runprg:bash`   
`##%runprgargs:test.sh`  
`##%overwritefile`  
`##%file:test.sh`  
`echo "shell cmd test"`   
`ls`   
  
----
#### Compile and run code
| label       |   value   | annotation                                                                                                       |
| :------------ | :----------: | :----------------------------------------------------------------------------------------------------------------- |
| cflags:     |            | Specifies the compilation parameters for C language compilation                                                  |
| ldflags:    |            | Specify the link parameters for C language connection                                                            |
| args:       |            | Specifies the parameters for the code file runtime                                                               |
| coptions:   |            | Code compilation time parameters of JVM platform                                                                 |
| joptions:   |            | Code runtime parameters for the JVM platform                                                                     |
| runprg:     |            | The code content will be run by the execution file specified by runprg                                           |
| runprgargs: |            | runprg Parameters of the specified executable ,You can put the name specified by file into the parameter string. |
| outputtype: | text/plain | mime-type                                                                                                        |
---
#### Interactive running code
| label         | value | annotation                                                                                  |
| :-------------- | :------: | :-------------------------------------------------------------------------------------------- |
| runmode:      |  repl  | The code will run in interactive mode.                                                      |
| replcmdmode   |        | (repl interactive mode) to send stdin information to the specified process (repl child PID) |
| replsetip:    | "\r\n" | Set (repl interactive mode) the prompt string when waiting for input                        |
| replchildpid: |        | (repl interactive mode) specifies the running process number                                |
| repllistpid   |        | Lists the interactive process PIDs that are running                                         |
---
#### Interactive running GDB
| label  | value | annotation                                               |
| :------- | :-----: | :--------------------------------------------------------- |
| rungdb |      | Run GDB and send commands to GDB (repl interactive mode) |
---
#### Save code and include file
| label         | value | annotation                                              |
| :------------ | :---: | :-------------------------------------------------- |
| noruncode     |      | Do not run code content                                  |
| overwritefile |      | Overwrite existing files                                 |
| file:         |      | The code can be saved to multiple files                  |
| fndict:       |      | Dictionary for file names                                |
| filefordict:  |      | Replace $key of fndict with a string from the fndict when save file |
| fnlist:       |      | List for file names                                      |
| fileforlist:  |      | Replace $fnlist with a string from the list  when save file |
| include:      |      | Places the specified file contents in the label location |
---
#### Templates and testing
| label                                                                                                                                          |
| :----------------------------------------------------------------------------------------------------------------------------------------------- |
| Define a macro                                                                                                                                 |
| define:Define a macro，The content is jinja2 template. example:\#\#%define:M1 this is {{name}}                                                 |
| &emsp; `##$Macroname` or `//$Macroname` Replace with macro                                                                                    |
| &emsp; `##$M1` name='jinja2 content' This line will be replaced by this is jinja2 content                                                      |
| templatefile:                                                                                                                                  |
| Define template code area                                                                                                                      |
| \#\#jj2_begin or  //jj2_begin                                                                                                                  |
| \#\#jj2_end   or  //jj2_end                                                                                                                    |
| Put template code between jj2_begin and jj2__end ，jj2_begin Followed by parameters example: name='jinja2 content'.example: jj2_begin:name=www |
| Define test code area                                                                                                                          |
| ##test_begin  /  //test_begin                                                                                                                  |
| ##test_end    /  //test_end                                                                                                                    |
| test_ Begin and test_ End is the test code，Will not be saved to the file                                                                      |
---
#### Commands and environment variables
| label       |           value           | annotation                                                                         |
| :------------ | :-------------------------: | :----------------------------------------------------------------------------------- |
| command:    |                          | shell command or executable                                                        |
| pycmd:      |                          | python parameter command                                                           |
| dartcmd:    |                          | dart parameter command                                                             |
| fluttercmd: | flutter parameter command |                                                                                    |
| kcmd:       |                          | jupyter kernel command                                                             |
| env:        |                          | Setting environment variables for code file runtime.example: name=xxx name2='dddd' |
---
#### Behavior control
| label       | value | annotation                 |
| :------------ | :-----: | :--------------------------- |
| noruncode   |      | Do not run code content    |
| onlycsfile  |      | Generate code files only   |
| onlyruncmd  |      | Run the label command only |
| onlycompile |      | Compile code content only  |
### License
[MIT](LICENSE.txt)
