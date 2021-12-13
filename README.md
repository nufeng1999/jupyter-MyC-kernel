# C kernel for Jupyter

This project was forked from [https://github.com/brendan-rius/jupyter-c-kernel](brendan-rius/jupyter-c-kernel) as that project seems to have been abandoned. (PR is pending)


## Manual installation

Works only on Linux and OS X. Windows is not supported yet. If you want to use this project on Windows, please use Docker.

* Make sure you have the following requirements installed:
  * gcc
  * jupyter
  * python 3
  * pip

### Step-by-step

```bash
git clone https://github.com/nufeng1999/jupyter-MyC-kernel.git
cd jupyter-MyC-kernel
pip install -e .  # for system install: sudo install .
cd jupyter_MyC_kernel && install_MyC_kernel --user # for sys install: sudo install_c_kernel
# now you can start the notebook
jupyter notebook
```
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


| label         | value | annotation                                               |
| :-------------- | :-----: | :--------------------------------------------------------- |
| noruncode     |      | Do not run code content                                  |
| overwritefile |      | Overwrite existing files                                 |
| file:         |      | The code can be saved to multiple files                  |
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


## License

[MIT](LICENSE.txt)
