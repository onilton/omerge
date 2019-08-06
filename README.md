# Omerge

A simple, intuitive and fast conflict resolution tool

## Why

Because what we had was not enough. :P (I need to improve this.)

## Install

The easiest way is to get the single binary (available in releases page). 

#### Install with a single command:

```
sudo wget 'https://github.com/onilton/omerge/releases/download/v0.0.1/omerge' -O /usr/local/bin/omerge ; sudo chmod +x  /usr/local/bin/omerge
```

#### Configuring as the git mergetool

```
git config --global merge.tool omerge
git config --global mergetool.omerge.cmd 'omerge "$BASE" "$LOCAL" "$REMOTE" "$MERGED"'
```


#### Avoid prompting when calling git mergetool (optional)

```
git config --global difftool.prompt false
```

## TO-DO

* This was made as proof of concept, so the code needs a lot of love to become prettier
* More color at the UI would be nice: highlight conflicts with color, colors in titlebars...
* Add syntax coloring for files
* Pick code from both sides (at the same time): `<=>`
* Resolve conflict without git mergetool just by calling omerge
* Walk around code not only conflicts
* Do not display `--------` for missing lines, instead dynamicaly move the cursor
* Display error when saving and not all conflicts were resolved
* Add vim mode to output editor
* Reduce single binary size
* Add contributing.MD

### Special Thanks
 
* [@jonathanslenders](https://github.com/jonathanslenders) for the amazing work on [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit/)
* [@dbrevesf](https://github.com/dbrevesf) for the help and inspiration
