from setuptools import setup

setup(name='jupyter_MyC_kernel',
      version='0.0.1',
      description='Minimalistic C kernel for Jupyter',
      author='nufeng',
      author_email='18478162@qq.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
      ],
      url='https://github.com/nufeng1999/jupyter-MyC-kernel/',
      download_url='https://github.com/nufeng1999/jupyter-MyC-kernel/tarball/0.0.1',
      packages=['jupyter_MyC_kernel'],
      scripts=['jupyter_MyC_kernel/install_MyC_kernel'],
      keywords=['jupyter', 'notebook', 'kernel', 'c'],
      include_package_data=True
      )
