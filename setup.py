from setuptools import setup, find_packages

setup(
  name='gui_fun',
  version='1.0.0',
  description='Create a basic gui for a function'
  long_description="""
  Create a basic gui for a function. Calling gui_fun(func) will generate
  a sequence of input fields for each argument in func. Attention will be
  paid to type annotations of int or float.
  """,
  url='http://cct.lsu.edu/~sbrandt/',
  author='Steven R. Brandt',
  author_email='steven@stevenrbrandt.com',
  license='LGPL',
  packages=['gui_func']
)
