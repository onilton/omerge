#!/usr/bin/env python3
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout import Layout, BufferControl, FormattedTextControl, UIContent, Dimension, NumberedMargin, ScrollOffsets
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

prefix = ">>>>>>> "
remote = next(line for line in merged.splitlines() if line.startswith(">>>>>>>"))
remote = remote[len(prefix):]
local = next(line for line in merged.splitlines() if line.startswith("<<<<<<<"))
local = local[len(prefix):]
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
comparisonA = list(d.compare(data3.splitlines(keepends=True), data1.splitlines(keepends=True)))
comparisonB = list(d.compare(data3.splitlines(keepends=True), data2.splitlines(keepends=True)))
print(comparison)
#dataA = comparison

a = []
b = []
c = []
previous = ''
previous_removes = []
previous_adds = []
for line in comparisonA:
    # s = ("", " ")
    s = "   \n"
    if line.startswith("-"):
        previous = '-'
        previous_removes.append(line)
        s = " ? \n"
        c.append(s)
    else:
        if line.startswith("+"):
            previous = '+'
            previous_adds.append(line)
            s = " ? \n"
            c.append(s)
        else:
            if not line.startswith("?"):
                if previous == '-':
                    for remove in previous_removes:
                        a.append("---------------------\n")
                if previous == '+':
                    for add in previous_adds:
                        a.append(add)
                    extra_removes = len(previous_removes) - len(previous_adds)
                    if extra_removes > 0:
                        for remove in range(extra_removes):
                            a.append("--------------------\n")
                previous = ''
                previous_removes = []
                previous_adds = []
                a.append(line)
                c.append(s)

i = 0
previous = ''
previous_removes = []
previous_adds = []
for line in comparisonB:
    s = "   \n"
    if line.startswith("-"):
        previous = '-'
        previous_removes.append(line)
        s = " ? \n"
        # b.append(line)
        c[i] = s
    else:
        if line.startswith("+"):
            previous = '+'
            previous_adds.append(line)
            s = " ? \n"
            # b.append(line)
            c[i] = s
        else:
            if not line.startswith("?"):
                if previous == '-':
                    for remove in previous_removes:
                        b.append("---------------------\n")
                if previous == '+':
                    for add in previous_adds:
                        b.append(add)
                    extra_removes = len(previous_removes) - len(previous_adds)
                    if extra_removes > 0:
                        for remove in range(extra_removes):
                            b.append("--------------------\n")
                previous = ''
                previous_removes = []
                previous_adds = []
                b.append(line)
                # c.append(s)
    i += 1

conflict_file = []
add_prefix = False
for line in merged.splitlines(keepends=True):
    if line.startswith("<<<<<<<"):
        add_prefix = True
        conflict_file.append(line)
    elif line.startswith(">>>>>>>"):
        add_prefix = False
        conflict_file.append(line)
    elif line.startswith("======="):
        conflict_file.append(line)
    else:
        if add_prefix:
            conflict_file.append("?<<<<<<?" + line)
        else:
            conflict_file.append(line)
    #print(conflict_file[-1:][0])

comparison_conflicts = list(d.compare(conflict_file, base.splitlines(keepends=True)))

no_previous_removal = True
output = ""
for line in comparison_conflicts:
    if not line.startswith("?"):
        print(line[:-1])
    if not (line.startswith("-") or line.startswith("?")):
        if line.startswith("+") and no_previous_removal:
            output = output + "--------------------\n"
        else:
            if line.startswith("+"):
                output = output + "?" + line[1:]
            else:
                output = output + line
    no_previous_removal = line.startswith(" ") or line.startswith("+")


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


def debug(line, a=None):
    #pass
    #new_text = str(line) + "\n" + horizbuffer.document.text
    new_text = horizbuffer.document.text
    new_text += "\n"
    new_text += str(len(horizbuffer.document.lines))
    new_text += "-"
    new_text += str(line)
    if a:
        new_text += str(a)
    horizbuffer.set_document(Document(new_text, len(new_text)), True)


def replace_line(line):
    buffer3.delete(len(buffer3.document.current_line)+1)
    buffer3.insert_text(line + "\n", move_cursor=False, fire_event=False)
    #buffer3.insert_text(line[2:] + "\n", move_cursor=False, fire_event=False)


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

buffer3 = Buffer(document=Document(output, 0))  # Editable buffer.

horizbuffer = Buffer(document=Document("", 0))


wspliter = Window(content=spliter, width=3, style="bg:#333333 ", cursorline=True, scroll_offsets=ScrollOffsets(top=10, bottom=10))

style = Style.from_dict({"cursor-line": "bg:#999999", "current-line-number": "bg:#999999 fg:#DDDDDD"})
w1 = Window(content=buffercontrol1, ignore_content_height=True, cursorline=True, dont_extend_height=True, left_margins=[NumberedMargin()], scroll_offsets=ScrollOffsets(top=10, bottom=10))
w2 = Window(content=BufferControl(buffer=buffer2), ignore_content_height=True, cursorline=True, dont_extend_height=True, left_margins=[NumberedMargin()], scroll_offsets=ScrollOffsets(top=10, bottom=10))
w3 = Window(content=BufferControl(buffer=buffer3), ignore_content_height=True, cursorline=True, dont_extend_height=True,
            height=Dimension(weight=1), left_margins=[NumberedMargin()], scroll_offsets=ScrollOffsets(top=10, bottom=10))


horizwindow = Window(content=BufferControl(buffer=horizbuffer), ignore_content_height=True, cursorline=True, dont_extend_height=True,
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


#@splitkb.add('down')
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


def get_diffblock_from_currentline():
    first_previous_from_same_block = sbuffer.document.find_previous_matching_line(
        lambda l: not l.startswith("   "))


    debug("first_previous_from_same_block", first_previous_from_same_block)
    start_line = sbuffer.document.cursor_position_row
    if first_previous_from_same_block == -1:
        first_previous_space = sbuffer.document.find_previous_matching_line(lambda l: l.startswith("   "))

        debug("first_previous_space", first_previous_space)
        start_line += first_previous_space + 1

    debug("start_line", start_line)

    first_next_from_same_block = sbuffer.document.find_next_matching_line(
        lambda l: not l.startswith("   "))

    end_line = sbuffer.document.cursor_position_row + 1
    if first_next_from_same_block == 1:
        first_next_space = sbuffer.document.find_next_matching_line(lambda l: l.startswith("   "))
        end_line += first_next_space - 1

    return DiffBlock(start_line, end_line)

class DiffBlock():
    def __init__(self, start_line, end_line):
        self.start_line = start_line
        self.end_line = end_line
        self.num_lines = end_line - start_line

    def get_lines_from_doc(self, document):
        return document.lines[self.start_line:self.end_line]

    def of_buffer(self, buffer_):
        return BufferBlock(buffer_, self)


class BufferBlock():
    def __init__(self, buffer_, diffblock):
        self.block = diffblock
        self.buffer = buffer_

    def replace_lines(self, lines):
        current_position_row = self.buffer.document.cursor_position_row

        ups = current_position_row - self.block.start_line
        #debug("cur" + str(current_position_row))
        #debug("start" + str(self.block.start_line))
        #debug("end" + str(self.block.end_line))
        #debug("ups" + str(ups))

        for _ in range(ups):
            self.buffer.cursor_up()

        for _ in lines:
            self.buffer.delete(len(buffer3.document.current_line)+1)
        self.buffer.insert_text("\n".join(lines) + "\n", move_cursor=False, fire_event=False)

        for _ in range(ups):
            self.buffer.cursor_down()

    def replace_single(self, line):
        current_position_row = self.buffer.document.cursor_position_row

        debug("========")
        debug("cur" + str(current_position_row))

        debug("num_lines " + str(self.block.num_lines))
        debug("start" + str(self.block.start_line))
        debug("end" + str(self.block.end_line))
        debug("========")

        start_index = self.buffer.document.translate_row_col_to_index(self.block.start_line, 0)
        end_index = self.buffer.document.translate_row_col_to_index(self.block.end_line, 0)

        new_text = self.buffer.document.text[0:(start_index)]
        #debug(")))" + new_text[-10:] + "((((")


        debug("REMOVED" + self.buffer.document.text[start_index:end_index] + "REMOVEDEND")
        cursor_position = self.buffer.document.cursor_position

        for _ in range(self.block.num_lines):
            debug(line + "\\n")
            new_text += line + "\n"
        new_text += self.buffer.document.text[end_index:]
        #debug(")))" + self.buffer.document.text[end_index: end_index+20] + "(((")

        self.buffer.set_document(Document(new_text, cursor_position), bypass_readonly=True)

        debug("END REPLACE LINES")

    def replace_current_line(self, line):
        start_index = self.buffer.document.cursor_position + self.buffer.document.get_start_of_line_position()
        end_index = self.buffer.document.cursor_position + self.buffer.document.get_end_of_line_position() + 1

        new_text = self.buffer.document.text[0:start_index]
        new_text += line + "\n"
        new_text += self.buffer.document.text[end_index:]

        cursor_position = self.buffer.document.cursor_position
        self.buffer.set_document(Document(new_text, cursor_position), bypass_readonly=True)


def replace_lines_start(lines, replacement):
    return [replace_line_start(line, replacement) for line in lines]


def replace_line_start(line, replacement):
    return replacement + line[len(replacement):]


@splitkb.add('<')
@splitkb.add('left')
def left_(event):
    """
    """
    if sbuffer.document.current_line.startswith("   "):
        return

    diff_block = get_diffblock_from_currentline()

    if sbuffer.document.current_line.startswith("<="):
        diff_block.of_buffer(buffer3).replace_lines(
            replace_lines_start(diff_block.get_lines_from_doc(buffer1.document), "A"))
        diff_block.of_buffer(sbuffer).replace_single("<| ")
        return

    if sbuffer.document.current_line.startswith("<|"):
        diff_block.of_buffer(sbuffer).replace_single(" ? ")
        replace_line(replace_line_start(buffer1.document.current_line, "A"))
        return

    if (sbuffer.document.current_line.startswith(" ?") or
            sbuffer.document.current_line.startswith("==") or
            sbuffer.document.current_line.endswith("|>")):
        replace_line(replace_line_start(buffer1.document.current_line, "A"))

        diff_block.of_buffer(sbuffer).replace_current_line("<==")


@splitkb.add('>')
@splitkb.add('right')
def right_(event):
    """
    """
    if sbuffer.document.current_line.startswith("   "):
        return

    diff_block = get_diffblock_from_currentline()

    if sbuffer.document.current_line.endswith("=>"):
        diff_block.of_buffer(buffer3).replace_lines(
            replace_lines_start(diff_block.get_lines_from_doc(buffer2.document), "B"))
        diff_block.of_buffer(sbuffer).replace_single(" |>")
        return

    if sbuffer.document.current_line.endswith(" |>"):
        diff_block.of_buffer(sbuffer).replace_single(" ? ")
        replace_line(replace_line_start(buffer2.document.current_line, "B"))
        return

    if (sbuffer.document.current_line.startswith(" ?") or
            sbuffer.document.current_line.endswith("==") or
            sbuffer.document.current_line.startswith("<|")):
        replace_line(replace_line_start(buffer2.document.current_line, "B"))

        diff_block.of_buffer(sbuffer).replace_current_line("==>")


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
         Window(content=FormattedTextControl(text='REMOTE - ' + remote), height=1, char=' ', style="bg:#555555"),
         w2,
        ]),
    ], height=Dimension(weight=1)),

    # A vertical line in the middle. We explicitly specify the width, to
    # make sure that the layout engine will not try to divide the whole
    # width by three for all these windows. The window will simply fill its
    # content by repeating this character.
    Window(height=1, char='-'),
    horizwindow,

    # Display the text 'Hello world' on the right.
    # Window(content=FormattedTextControl(text='Hello world')),
    w3
])

layout = Layout(root_container)

app = Application(layout=layout, full_screen=True, key_bindings=kb, style=style)

app.layout.focus(wspliter)
app.run()
