Omerge

A simple, intuitive and fast conflict resolution tool


Configuring as git mergetool
git config --global merge.tool omerge
git config --global mergetool.omerge.cmd '/my/path/to/omerge.py "$BASE" "$LOCAL" "$REMOTE" "$MERGED"'


Optional to avoid prompting
git config --global difftool.prompt false
