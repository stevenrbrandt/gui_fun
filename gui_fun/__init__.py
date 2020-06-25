import inspect
import pickle
import stat
import os
import re
from ipywidgets import *

class ResultStream:
    def __init__(self):
        self.results = []
    def has_result(self):
        return len(self.results) > 0
    def pop_result(self):
        val = self.results[0]
        self.results = self.results[1:]
        return val
    def add_result(self,result):
        print("added result:", result)
        self.results += [result]

display(HTML("""
<style>
.gui_label_style {
    background: black;
    color: white;
    font-weight: bold;
    padding: 5px;
}
.off_label_style_1 {
    background: #DDDDDD;
    padding: 5px;
    border: black solid 1px;
    font-weight: bold;
}
.off_label_style_0 {
    padding: 5px;
    border: black solid 1px;
    font-weight: bold;
}
</style>
"""))

gui_settings = {}

def settings(f, s):
    global gui_settings
    fn = f.__name__
    mo = str(f.__module__)
    if mo not in gui_settings:
        gui_settings[mo] = {}
    gui_settings[mo][fn] = s


def load_property(f, tag):
    if tag == "defaults":
        return {}
    fn = f.__name__
    mo = str(f.__module__)
    path = os.path.join(os.environ["HOME"],"tmp",mo,fn,tag,"data.txt")
    if os.path.exists(path):
        with open(path,"rb") as fd:
            return pickle.loads(fd.read())
    return {}

def store_property(f,r,tag):
    fn = f.__name__
    mo = str(f.__module__)
    dirp = os.path.join(os.environ["HOME"],"tmp",mo,fn,tag)
    os.makedirs(dirp, exist_ok=True)
    path = os.path.join(dirp, "data.txt")
    with open(path, "wb") as fd:
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        fd.write(pickle.dumps(r))
        
# A length function that returns 0 for None
def zlen(z):
    if z is None:
        return 0
    else:
        return len(z)

# Convert a string from the input. If the string
# begins with [ or {, it is a list or an array
# and eval should be called.
def unstr(s):
    if type(s) != str:
        return s

    # substitute values from the environment
    # if we see things that look like ${NAME}
    while True:
        g = re.search(r'\$\{(\w+)\}', s)
        if g:
            s = s[0:g.start()]+os.environ.get(g.group(1),"")+s[g.end():]
        else:
            break

    if s == "None":
        return None
    elif re.match(r'[\[{"]',s):
        return eval(s)
    else:
        return s

def BLabel(value,style):
    label = Label(value=value)
    label.add_class(style)
    return label

def gui_fun(f, tag="", defaults=None, settings = None):
    global gui_settings
    fn = f.__name__
    mo = str(f.__module__)
    if settings is None:
        if mo in gui_settings:
            settings = gui_settings[mo].get(fn, None)
    if settings is None:
        settings = {}

    fargs = inspect.getfullargspec(f)
    # widgets to collect data
    disp = []
    # labels for the widgets, using the description
    # field in the widget seems not to work right.
    # If the description it gets too long and no
    # setting of Layout fixes it.
    desc = []
    disp += [BLabel(value=f.__name__,style='gui_label_style')]
    desc += [Label()]
    index = 1
    for i in range(len(fargs.args)):
        arg = fargs.args[i]
        if arg == "self" and i == 0:
            index = 0
            continue
        a = fargs.annotations.get(arg, None)
        if type(settings.get(arg,"")) == list:
            options = settings.get(arg)
            if type(options[0]) == tuple:
                value = options[0][1]
            else:
                value = options[0]
            t = Dropdown(options=options, value=value)
        elif a == list:
            options = a
            if type(options[0]) == tuple:
                value = options[0][0]
            else:
                value = options[0]
            t = Dropdown(options=options, value=value)
        elif a == int:
            t = IntText()
        elif a == float:
            t = FloatText()
        elif settings.get(arg,"") == "password" or a == "password":
            t = Password()
        elif settings.get(arg,"") == "textarea" or a == "textarea":
            t = Textarea()
        else:
            t = Text()
        if i % 2 == 0:
            d = BLabel(value=arg,style='off_label_style_1')
        else:
            d = BLabel(value=arg,style='off_label_style_0')
        desc += [d]
        disp += [t]

    # Create an array of blank strings to use
    # for default display values
    empty = object()
    r = [empty for i in range(len(fargs.args))]

    # Load the default values from the
    # function definitions.
    off = zlen(fargs.args) - zlen(fargs.defaults)
    for i in range(zlen(fargs.defaults)):
        r[i+off] = fargs.defaults[i]

    # Load the values stored from the
    # last time this function was invoked.
    if defaults is not None:
        pairs = load_property(f, defaults)
        for i in range(len(fargs.args)):
            r[i] = pairs.get(fargs.args[i], r[i])
    pairs = load_property(f, tag)
    for i in range(len(fargs.args)):
        r[i] = pairs.get(fargs.args[i], r[i])
    for i in range(len(fargs.args)):
        # Don't prompt for the self field of
        # member functions. That is already
        # filled in if gui() is called properly.
        if r[i] == empty:
            pass
        elif fargs.args[i] == "self":
            pass 
        elif type(disp[i+index]) in [Password, Text, Textarea]:
            disp[i+index].value = str(r[i])
        elif type(disp[i+index]) == IntText:
            if r[i] == "":
                disp[i+index].value = 0
            else:
                disp[i+index].value = int(r[i])
        elif type(disp[i+index]) == FloatText:
            if r[i] == "":
                disp[i+index].value = 0
            else:
                disp[i+index].value = float(r[i])
        elif type(disp[i+index]) == Dropdown:
            disp[i+index].value = r[i]
    run = Button(description="Run")
    retval = ResultStream()
    def gui_run(_):
        vals = []
        pairs = {}
        for i in range(len(fargs.args)):
            if i == 0 and fargs.args[0] == "self":
                pass
            else:
                # load the values...
                d = disp[i+index]
                # load the argument names...
                l = desc[i+index]
                vals += [unstr(d.value)]
                # store them.
                pairs[l.value] = d.value
        retval.add_result( f(*vals) )
        # Because we store name value pairs,
        # stored values will still load properly
        # if we change the arguments around.
        store_property(f, pairs, tag)
    run.on_click(gui_run)
    disp += [run]
    desc += [Label()]
    display(HBox([VBox(desc),VBox(disp)]))
    return retval
