# Omerge

A simple, intuitive and fast conflict resolution tool


#### Configuring as the git mergetool

```
git config --global merge.tool omerge
git config --global mergetool.omerge.cmd '/my/path/to/omerge.py "$BASE" "$LOCAL" "$REMOTE" "$MERGED"'
```


#### Optional to avoid prompting when calling git mergetool

```
git config --global difftool.prompt false
```
