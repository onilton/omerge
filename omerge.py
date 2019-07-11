#!/usr/bin/env python3
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout import Layout, BufferControl, FormattedTextControl, UIContent, Dimension, NumberedMargin, ScrollOffsets
from prompt_toolkit.layout.processors import AfterInput, Processor, Transformation
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText, to_formatted_text, fragment_list_len, fragment_list_to_text
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


def get_normalized_branch(raw_conflict_line):
    prefix = ">>>>>>> "
    branch = raw_conflict_line[len(prefix):]
    if 'HEAD' in branch:
        result = subprocess.run(['git', 'branch', '--no-color'], stdout=subprocess.PIPE)
        branches = result.stdout.decode("utf-8").splitlines()
        print(branches)
        head_branch = next(line for line in branches if line.startswith("* "))
        head_branch = head_branch[2:]
        branch = head_branch

    return branch


conflict_last_line = next(line for line in merged.splitlines() if line.startswith(">>>>>>>"))
remote_branch = get_normalized_branch(conflict_last_line)

conflict_first_line = next(line for line in merged.splitlines() if line.startswith("<<<<<<<"))
local_branch = get_normalized_branch(conflict_first_line)


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
    else:
        if line.startswith("+"):
            previous = '+'
            previous_adds.append(line)
        else:
            if not line.startswith("?"):
                if previous == '-':
                    for remove in previous_removes:
                        a.append("---------------------\n")
                        s = " ? \n"
                        c.append(s)
                if previous == '+':
                    for add in previous_adds:
                        a.append(add)
                        s = " ? \n"
                        c.append(s)
                    extra_removes = len(previous_removes) - len(previous_adds)
                    if extra_removes > 0:
                        for remove in range(extra_removes):
                            a.append("--------------------\n")
                            s = " ? \n"
                            c.append(s)
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

i = 0
no_previous_removal = True
output = ""
for line in comparison_conflicts:
    if not line.startswith("?"):
        print(line[:-1])
    if not (line.startswith("-") or line.startswith("?")):
        if line.startswith("+") and no_previous_removal:
            output = output + "--------------------\n"
            # Remove non-conflicts from picker
            c[i] = "   \n"
        else:
            if line.startswith("+"):

                output = output + "?" + line[1:]
            else:
                output = output + line
    no_previous_removal = line.startswith(" ") or line.startswith("+")
    i += 1


class AddStyleToDiff(Processor):
    """
    Insert style before the input. for -, +
    """
    def __init__(self, style: str = '') -> None:
        self.style = style

    def apply_transformation(self, ti):
        len_frag = fragment_list_len(ti.fragments)
        if len_frag >= 2:
            fragments_before = to_formatted_text(ti.fragments[0][1][:2], self.style)

            fragments = fragments_before
            fragments += [(ti.fragments[0][0], ti.fragments[0][1][2:])]
            fragments += ti.fragments[1:]
        else:
            fragments = ti.fragments

        source_to_display = lambda i: i
        display_to_source = lambda i: i

        return Transformation(fragments, source_to_display=source_to_display,
                              display_to_source=display_to_source)

    def __repr__(self) -> str:
        return 'AddStyleToDiff(%r, %r)' % (self.text, self.style)


local_file_buffer = Buffer(document=Document("".join(a), 0), read_only=True)  # Editable buffer.
local_file_buffer_control = BufferControl(buffer=local_file_buffer, input_processors=[AddStyleToDiff("bg:#222222")])  # Editable buffer.




remote_file_buffer = Buffer(document=Document("".join(b), 0), read_only=True)  # Editable buffer.

def sync_cursor(source_buffer, target_buffer):
    old_target_text = target_buffer.document.text
    source_row = source_buffer.document.cursor_position_row
    target_buffer.set_document(Document(old_target_text, 0), True)
    if source_row > 0:
        target_buffer.cursor_down(count=source_row)


def debug(line, a=None):
    #pass
    #new_text = str(line) + "\n" + horizbuffer.document.text
    new_text = debug_buffer.document.text
    new_text += "\n"
    new_text += str(len(debug_buffer.document.lines))
    new_text += "-"
    new_text += str(line)
    if a:
        new_text += str(a)
    debug_buffer.set_document(Document(new_text, len(new_text)), True)


def replace_line(line):
    output_buffer.delete(len(output_buffer.document.current_line)+1)
    output_buffer.insert_text(line + "\n", move_cursor=False, fire_event=False)
    #output_buffer.insert_text(line[2:] + "\n", move_cursor=False, fire_event=False)


#def change_on_cursor(source_buffer, target_buffer):
#    old_target_text = target_buffer.document.text
#    source_row = source_buffer.document.cursor_position_row
#    target_buffer.set_document(Document(old_target_text, 0), True)
#    if source_row > 0:
#        target_buffer.cursor_down(count=source_row)


def cursor_changed(x):
    #debug(x)
    sync_cursor(sbuffer, local_file_buffer)
    sync_cursor(sbuffer, remote_file_buffer)
    sync_cursor(sbuffer, output_buffer)
    sync_cursor(sbuffer, backup_buffer)
    update_output_titlebar()


style = Style.from_dict({
    "cursor-line": "bg:#999999 nounderline",
    "line-number": "bg:#222222",
    "current-line-number": "bg:#999999 fg:#DDDDDD bold",
    "file-viewer": "bg:#1c1c1c",
    "titlebar": "bg:#404040",
    "picker": "bg:#333333",
    "picker cursor-line": "reverse bold"
})


sbuffer = Buffer(
    document=Document("".join(c), 0),
    read_only=True,
    on_cursor_position_changed=cursor_changed)
spliter = BufferControl(buffer=sbuffer, key_bindings=splitkb)
wspliter = Window(
    content=spliter,
    width=3,
    style="class:picker",
    always_hide_cursor=True,
    cursorline=True,
    scroll_offsets=ScrollOffsets(top=10, bottom=10))


local_file_window = Window(
    content=local_file_buffer_control,
    style="class:file-viewer",
    ignore_content_height=True,
    cursorline=True,
    dont_extend_height=True,
    left_margins=[NumberedMargin()],
    scroll_offsets=ScrollOffsets(top=10, bottom=10))


remote_file_buffer_control = BufferControl(
    buffer=remote_file_buffer,
    input_processors=[AddStyleToDiff("bg:#222222")])
remote_file_window = Window(
    content=remote_file_buffer_control,
    style="class:file-viewer",
    ignore_content_height=True,
    cursorline=True,
    dont_extend_height=True,
    left_margins=[NumberedMargin()],
    scroll_offsets=ScrollOffsets(top=10, bottom=10))


output_buffer = Buffer(document=Document(output, 0))
output_buffer_control = BufferControl(
    buffer=output_buffer,
    input_processors=[AddStyleToDiff("bg:#222222")])
output_window = Window(
    content=output_buffer_control,
    style="class:file-viewer",
    ignore_content_height=True,
    cursorline=True,
    dont_extend_height=True,
    height=Dimension(weight=1),
    left_margins=[NumberedMargin()],
    scroll_offsets=ScrollOffsets(top=10, bottom=10))


hotkeys = {
    '<': 'pick left line',
    '>': 'pick right line',
    'C-down':  'go to output',
    'C-q': 'quit',
    'C-s': 'accept changes',
}


# The output titlebar: a vertical line in the middle.
output_titlebar = Window(
    content=FormattedTextControl(text=''),
    height=1,
    char=' ',
    style="class:titlebar")


def update_output_titlebar():
    global hotkeys

    new_hotkeys = {
        '<': 'pick left line',
        '>': 'pick right line'
    }
    new_hotkeys.update(hotkeys)
    hotkeys = new_hotkeys

    if sbuffer.document.current_line.startswith("   "):
        if '<' in hotkeys:
            del hotkeys['<']
            del hotkeys['>']
    elif sbuffer.document.current_line.startswith("<="):
        hotkeys['<'] = 'pick left block'
    elif sbuffer.document.current_line.endswith("=>"):
        hotkeys['>'] = 'pick right block'

    elif sbuffer.document.current_line.startswith("<|"):
        hotkeys['<'] = 'unpick left block'
    elif sbuffer.document.current_line.endswith("|>"):
        hotkeys['>'] = 'unpick right block'

    new_text = ' OUTPUT | Keys: '
    new_text += " | ".join([key + " (" + description + ")" for (key, description) in hotkeys.items()])
    output_titlebar.content.text = new_text


update_output_titlebar()


backup_buffer = Buffer(document=Document(output, 0))
backup_buffer_control = BufferControl(
    buffer=backup_buffer,
    input_processors=[AddStyleToDiff("bg:#222222")])
backup_buffer_window = Window(
    content=backup_buffer_control,
    ignore_content_height=True,
    cursorline=True,
    dont_extend_height=True,
    height=Dimension(weight=1),
    left_margins=[NumberedMargin()],
    scroll_offsets=ScrollOffsets(top=10, bottom=10))


debug_buffer = Buffer(document=Document("", 0))
debug_window = Window(
    content=BufferControl(buffer=debug_buffer),
    ignore_content_height=True,
    cursorline=True,
    dont_extend_height=True,
    height=Dimension(weight=1))


@kb.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()


@kb.add('c-s')
def save_and_exit_(event):
    """
    """
    for line in output_buffer.document.lines:
        if line.startswith("?"):
            return
    with open(args.merged, 'wt') as merged_file:
        for line in output_buffer.document.lines:
            if not line[1:].startswith("--"):
                merged_file.write(line[2:] + "\n")

    event.app.exit()


@splitkb.add('down')
def smart_down(event):
    """
    Smart down:
        inside block, go one line down,
        at the end of the block, go to next conflict
    """
    doc = sbuffer.document
    position = sbuffer.document.cursor_position
    offsets = [doc.find("?"), doc.find("<"), doc.find(">")]
    offsets = sorted([p for p in offsets if p is not None])
    offset = next(iter(offsets), None)

    if offset:
        sbuffer.set_document(
            Document(doc.text, position + offset),
            bypass_readonly=True)


@splitkb.add('up')
def smart_up(event):
    """
    Smart up:
        inside block, go one line up,
        at the end of the block, go to previous conflict
    """
    doc = sbuffer.document
    position = sbuffer.document.cursor_position
    offsets = [doc.find_backwards("?"), doc.find_backwards("<"),
               doc.find_backwards(">")]
    offsets = sorted([p for p in offsets if p is not None], reverse=True)
    offset = next(iter(offsets), None)

    if offset:
        sbuffer.set_document(
            Document(doc.text, position + offset),
            bypass_readonly=True)


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
            self.buffer.delete(len(self.buffer.document.current_line)+1)
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
        diff_block.of_buffer(output_buffer).replace_lines(
            replace_lines_start(diff_block.get_lines_from_doc(local_file_buffer.document), "A"))
        diff_block.of_buffer(sbuffer).replace_single("<| ")

        update_output_titlebar()
        return

    if sbuffer.document.current_line.startswith("<|"):
        diff_block.of_buffer(sbuffer).replace_single(" ? ")
        diff_block.of_buffer(output_buffer).replace_lines(
            diff_block.get_lines_from_doc(backup_buffer.document))

        update_output_titlebar()
        return

    if (sbuffer.document.current_line.startswith(" ?") or
            sbuffer.document.current_line.startswith("==") or
            sbuffer.document.current_line.endswith("|>")):
        replace_line(replace_line_start(local_file_buffer.document.current_line, "A"))

        diff_block.of_buffer(sbuffer).replace_current_line("<==")

        update_output_titlebar()


@splitkb.add('>')
@splitkb.add('right')
def right_(event):
    """
    """
    if sbuffer.document.current_line.startswith("   "):
        return

    diff_block = get_diffblock_from_currentline()

    if sbuffer.document.current_line.endswith("=>"):
        diff_block.of_buffer(output_buffer).replace_lines(
            replace_lines_start(diff_block.get_lines_from_doc(remote_file_buffer.document), "B"))
        diff_block.of_buffer(sbuffer).replace_single(" |>")

        update_output_titlebar()
        return

    if sbuffer.document.current_line.endswith(" |>"):
        diff_block.of_buffer(sbuffer).replace_single(" ? ")
        diff_block.of_buffer(output_buffer).replace_lines(
            diff_block.get_lines_from_doc(backup_buffer.document))

        update_output_titlebar()
        return

    if (sbuffer.document.current_line.startswith(" ?") or
            sbuffer.document.current_line.endswith("==") or
            sbuffer.document.current_line.startswith("<|")):
        replace_line(replace_line_start(remote_file_buffer.document.current_line, "B"))

        diff_block.of_buffer(sbuffer).replace_current_line("==>")
        update_output_titlebar()


@kb.add('c-up')
def w1_(event):
    """
    """
    event.app.layout.focus(wspliter)

@kb.add('c-left')
def w1_(event):
    """
    """
    event.app.layout.focus(local_file_window)

@kb.add('c-right')
def w2_(event):
    """
    """
    event.app.layout.focus(remote_file_window)

@kb.add('c-down')
def w3_(event):
    """
    """
    event.app.layout.focus(output_window)


root_container = HSplit([
    # One window that holds the BufferControl with the default buffer on
    # the left.

    VSplit([
        HSplit([
            Window(content=FormattedTextControl(text=' A - LOCAL - ' + local_branch), height=1, char=' ', style="class:titlebar"),
            local_file_window,
        ]),

        HSplit([
            Window(height=1, char=' ', style="bg:#333333"),
            wspliter,
        ]),


        HSplit([
            Window(content=FormattedTextControl(text=' B - REMOTE - ' + remote_branch), height=1, char=' ', style="class:titlebar"),
            remote_file_window,
        ]),
    ], height=Dimension(weight=1)),


    # The output titlebar: a vertical line in the middle.
    output_titlebar,
    #debug_window,

    # Display the text 'Hello world' on the right.
    # Window(content=FormattedTextControl(text='Hello world')),
    output_window
])

layout = Layout(root_container)

app = Application(layout=layout, full_screen=True, key_bindings=kb, style=style)

app.layout.focus(wspliter)

def main():
    """
    """
    smart_down(None)
    app.run()

if __name__ == "__main__":
    main()
