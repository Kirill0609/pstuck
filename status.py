import os

outs = ["left","right"]

files = { outs[0]: "~/.xmonad/left"
        , outs[1]: "~/.xmonad/right"
        }

for key in files.keys():
    files[key] = os.path.expanduser(files[key])

buff = {n:"" for n in outs}


def color_text(text, r,g,b):
    cstr = "{:02x}{:02x}{:02x}".format(r, g, b)
    return "<fc=#{}>{text}</fc> ".format(cstr, text=text)

def append_text(text, loc, color = None):
    if not loc in outs:
        print("No such output {}".format(loc))
        raise ValueError
    if color != None:
        text = color_text(text, *color)
    buff[loc] += text

def render_buff(buffn):
    with open(files[buffn], 'w') as f:
        f.write(buff[buffn])
    buff[buffn] = ""

def render(buffs = []):
    if len(buffs) == 0:
        for buffn in outs:
            render_buff(buffn)
    else:
        for buffn in buffs:
            render_buff(buffn)

   
