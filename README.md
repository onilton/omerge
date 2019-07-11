# Omerge

A simple, intuitive and fast conflict resolution tool

## Why

Because what we had was not enough. :P (I need to improve this.)

## Install

The easiest way is to get the single binary:


#### Configuring as the git mergetool

```
git config --global merge.tool omerge
git config --global mergetool.omerge.cmd '/my/path/to/omerge.py "$BASE" "$LOCAL" "$REMOTE" "$MERGED"'
```


#### Optional to avoid prompting when calling git mergetool

```
git config --global difftool.prompt false
```
