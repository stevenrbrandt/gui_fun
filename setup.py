from setuptools import setup, find_packages

setup(
  name='gui_fun',
  version='1.0.2',
  description='Create a basic gui for a function',
  long_description='''
  Create a basic gui for a function.
  Calling gui_fun(func) will generate a sequence of input boxes
  for each argument in func, plus a run button to execute the function.
  The output of gui_fun() is an asyncio.Future that can be queried for
  the result.
  ''',
  url='http://cct.lsu.edu/~sbrandt/',
  author='Steven R. Brandt',
  author_email='steven@stevenrbrandt.com',
  license='LGPL',
  packages=['gui_fun']
)
