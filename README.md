# gui_fun
Instantly create a gui for any Python function in a Jupyter notebook.

The basic idea is that if we create a function, say

<pre>
  def add(a,b):
    return a+b
</pre>

We can create a gui to collect the input (values for "a" and "b") and
call the function to produce output by simply calling:
<pre>
  gui_fun(add)
</pre>

For details, see the tutorial notebook.
