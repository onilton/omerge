#!/usr/bin/env python3
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout import Layout, BufferControl, FormattedTextControl, UIContent, Dimension
from prompt_toolkit.layout.processors import AfterInput
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style
from difflib import Differ
import argparse
import subprocess

kb = KeyBindings()
splitkb = KeyBindings()

parser = argparse.ArgumentParser(prog='omerge', description='Cool merge tool')
parser.add_argument('base', metavar='BASE')
parser.add_argument('local', metavar='LOCAL')
parser.add_argument('remote', metavar='REMOTE')
parser.add_argument('merged', metavar='MERGED')
args = parser.parse_args()

with open(args.local, 'r') as file1:
    data1 = file1.read()

with open(args.remote, 'r') as file2:
    data2 = file2.read()

with open(args.merged, 'r') as file3:
    merged = file3.read()

with open(args.base, 'r') as base:
    base = base.read()
    data3 = base

remote = next(line for line in merged.splitlines() if line.startswith(">>>>>>>"))
local = next(line for line in merged.splitlines() if line.startswith("<<<<<<<"))
if 'HEAD' in local:
    result = subprocess.run(['git', 'branch', '--no-color'], stdout=subprocess.PIPE)
    branches = result.stdout.decode("utf-8").splitlines()
    print(branches)
    head_branch = next(line for line in branches if line.startswith("* "))
    head_branch = head_branch[2:]
    local = head_branch

#class Custom

d = Differ()

#comparison = list(d.compare(data1, data2))
comparison = list(d.compare(data1.splitlines(keepends=True), data2.splitlines(keepends=True)))
print(comparison)
#dataA = comparison

a = []
b = []
c = []
for line in comparison:
    #s = ("", " ")
    s = " \n"
    if line.startswith("-"):
        #s = ("fg:#ffffff", "<")
        s = "?\n"
        # a.append(("bg:#ff0000 class:color-column:#ff0000", line))
        a.append(line)

        c.append(s)
    else:
        if line.startswith("+"):
            s = "?\n"

            # s = ("fg:#ffffff", ">")

            b.append(line)
            c.append(s)
        else:
            if not line.startswith("?"):

                # a.append(("", line))
                a.append(line)
                b.append(line)
                c.append(s)


buffer1 = Buffer(document=Document("".join(a), 0), read_only=True)  # Editable buffer.
buffercontrol1 = BufferControl(buffer=buffer1)  # Editable buffer.




#buffercontrol1 = FormattedTextControl(text=a)
buffer2 = Buffer(document=Document("".join(b), 0), read_only=True)  # Editable buffer.
#buffer1 = Buffer(document=Document(data1, 0))  # Editable buffer.
#buffer2 = Buffer(document=Document(data2, 0))  # Editable buffer.

def sync_cursor(source_buffer, target_buffer):
    old_target_text = target_buffer.document.text
    source_row = source_buffer.document.cursor_position_row
    target_buffer.set_document(Document(old_target_text, 0), True)
    if source_row > 0:
        target_buffer.cursor_down(count=source_row)


def debug(line):
    new_text = str(line) + "\n" + buffer3.document.text
    buffer3.set_document(Document(new_text, 0), True)


def replace_line(line):
    buffer3.delete(len(buffer3.document.current_line)+1)
    buffer3.insert_text(line[2:] + "\n", move_cursor=False, fire_event=False)
    #new_text = str(line) + "\n" + buffer3.document.text
    #buffer3.set_document(Document(new_text, 0), True)


#def change_on_cursor(source_buffer, target_buffer):
#    old_target_text = target_buffer.document.text
#    source_row = source_buffer.document.cursor_position_row
#    target_buffer.set_document(Document(old_target_text, 0), True)
#    if source_row > 0:
#        target_buffer.cursor_down(count=source_row)


def cursor_changed(x):
    #debug(x)
    sync_cursor(sbuffer, buffer1)
    sync_cursor(sbuffer, buffer2)
    sync_cursor(sbuffer, buffer3)


#spliter = FormattedTextControl(text=c)
#sbuffer = Buffer(document=Document("".join(c), 0), readon_cursor_position_changed=cursor_changed)  # Editable buffer.
sbuffer = Buffer(document=Document("".join(c), 0), read_only=True, on_cursor_position_changed=cursor_changed)  # Editable buffer.
spliter = BufferControl(buffer=sbuffer, key_bindings=splitkb)  # Editable buffer.

buffer3 = Buffer(document=Document(data3, 0))  # Editable buffer.


wspliter = Window(content=spliter, width=1, style="bg:#333333 ", cursorline=True)

style = Style.from_dict({"cursor-line": "bg:#AAAAAA"})
w1 = Window(content=buffercontrol1, ignore_content_height=True, cursorline=True, cursorcolumn=True, dont_extend_height=True)
w2 = Window(content=BufferControl(buffer=buffer2), ignore_content_height=True, cursorline=True, dont_extend_height=True)
w3 = Window(content=BufferControl(buffer=buffer3), ignore_content_height=True, cursorline=True, dont_extend_height=True,
            height=Dimension(weight=1))
#w2 = Window(content=FormattedTextControl(text='Helloo world'))

@kb.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()


def change_char(s, p, r):
    return s[:p]+r+s[p+1:]


@splitkb.add('down')
def down_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    text = sbuffer.document.text
    position = sbuffer.document.cursor_position
    indexA = text.find("?",  position + 1, len(text))
    indexB = text.find("<",  position + 1, len(text))
    indexC = text.find(">",  position + 1, len(text))

    index = indexA
    if index < 0 or (indexB < index and indexB >= 0):
        index = indexB

    if index < 0 or (indexC < index and indexC >= 0):
        index = indexC

    if index >= 0:
        sbuffer.set_document(Document(text, index), bypass_readonly=True)

    sbuffer.set_document(Document(text, sbuffer.document.cursor_position), bypass_readonly=True)


@splitkb.add('<')
@splitkb.add('left')
def left_(event):
    """
    """
    if sbuffer.document.text[sbuffer.document.cursor_position] == " ":
        return

    replace_line(buffer1.document.current_line)
    new_text = change_char(sbuffer.document.text, sbuffer.document.cursor_position, "<")
    sbuffer.set_document(Document(new_text, sbuffer.document.cursor_position), bypass_readonly=True)

@splitkb.add('>')
@splitkb.add('right')
def right_(event):
    """
    """

    if sbuffer.document.text[sbuffer.document.cursor_position] == " ":
        return

    replace_line(buffer2.document.current_line)

    new_text = change_char(sbuffer.document.text, sbuffer.document.cursor_position, ">")
    sbuffer.set_document(Document(new_text, sbuffer.document.cursor_position), bypass_readonly=True)

@kb.add('c-up')
def w1_(event):
    """
    """
    event.app.layout.focus(wspliter)

@kb.add('c-left')
def w1_(event):
    """
    """
    event.app.layout.focus(w1)

@kb.add('c-right')
def w2_(event):
    """
    """
    event.app.layout.focus(w2)

@kb.add('c-down')
def w3_(event):
    """
    """
    event.app.layout.focus(w3)



root_container = HSplit([
    # One window that holds the BufferControl with the default buffer on
    # the left.

    VSplit([
        HSplit([
             Window(content=FormattedTextControl(text='LOCAL - ' + local), height=1, char=' ', style="bg:#555555"),
             w1,
        ]),

        HSplit([
            Window(height=1, char=' ', style="bg:#555555"),
            wspliter,
        ]),


        HSplit([
         Window(content=FormattedTextControl(text='REMOTE' + remote), height=1, char=' ', style="bg:#555555"),
         w2,
        ]),
    ], height=Dimension(weight=1)),

    # A vertical line in the middle. We explicitly specify the width, to
    # make sure that the layout engine will not try to divide the whole
    # width by three for all these windows. The window will simply fill its
    # content by repeating this character.
    Window(height=1, char='-'),

    # Display the text 'Hello world' on the right.
    # Window(content=FormattedTextControl(text='Hello world')),
    w3
])

layout = Layout(root_container)

app = Application(layout=layout, full_screen=True, key_bindings=kb, style=style)

app.layout.focus(wspliter)
app.run()
