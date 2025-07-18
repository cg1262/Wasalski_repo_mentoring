# Git - Podstawowe Komendy, Tips and Tricks + Zarządzanie Commitami

## Podstawowe komendy Git

### Inicjalizacja i konfiguracja

```bash
# Inicjalizacja repo
git init

# Konfiguracja użytkownika (globalnie)
git config --global user.name "Jan Kowalski"
git config --global user.email "jan@example.com"

# Konfiguracja dla konkretnego repo
git config user.name "Jan Kowalski"
git config user.email "jan.kowalski@work.com"

# Sprawdzenie konfiguracji
git config --list
git config user.name

# 💡 TIP: Różne tożsamości dla różnych projektów
git config --global includeIf."gitdir:~/work/".path ~/.gitconfig-work
```

### Status i podstawowe operacje

```bash
# Status repo
git status
git status --short           # skrócona wersja
git status --porcelain       # dla skryptów

# Dodawanie plików
git add file.txt             # jeden plik
git add .                    # wszystkie pliki w katalogu
git add *.py                 # wszystkie pliki .py
git add -A                   # wszystkie zmiany (dodane, usunięte, zmodyfikowane)
git add -u                   # tylko zmodyfikowane i usunięte (bez nowych)

# 💡 TIP: Interaktywne dodawanie
git add -i                   # interaktywny tryb
git add -p                   # patch mode - wybierz części pliku
```

### Commitowanie

```bash
# Podstawowe commity
git commit -m "Opis zmian"
git commit -am "Dodaj i commituj wszystkie zmodyfikowane pliki"

# Wielolinijkowy commit message
git commit -m "Tytuł commita" -m "Dłuższy opis zmian"

# Commity z edytorem
git commit                   # otwiera edytor
git commit --amend           # edytuj ostatni commit

# 💡 TIP: Szablon commit message
git config --global commit.template ~/.gitmessage
```

## Zarządzanie historią

### Przeglądanie historii

```bash
# Historia commitów
git log                      # pełna historia
git log --oneline           # jedna linia na commit
git log --graph             # graficzna reprezentacja
git log --all --graph --oneline  # wszystkie branch + graf

# Filtrowanie historii
git log --since="2023-01-01"     # od daty
git log --until="2023-12-31"     # do daty
git log --author="Jan"           # po autorze
git log --grep="fix"            # po message
git log -S "function_name"      # po zawartości

# 💡 TIP: Piękny format logów
git log --pretty=format:"%h - %an, %ar : %s"
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

### Różnice między commitami

```bash
# Sprawdzanie różnic
git diff                     # zmiany w working directory
git diff --staged           # zmiany w staging area
git diff HEAD               # wszystkie niezcommitowane zmiany
git diff commit1 commit2    # między commitami
git diff HEAD~1 HEAD        # ostatni commit vs poprzedni

# 💡 TIP: Różnice z ignorowaniem whitespace
git diff --ignore-all-space
git diff --ignore-space-change
```

## Cofanie zmian

### Różne sposoby cofania

```bash
# Cofanie zmian w working directory
git checkout -- file.txt    # cofnij zmiany w pliku
git checkout .              # cofnij wszystkie zmiany

# Cofanie z staging area
git reset HEAD file.txt     # usuń z staging (zostaw zmiany)
git reset HEAD              # usuń wszystko z staging

# Cofanie commitów
git reset --soft HEAD~1     # cofnij commit, zostaw zmiany w staging
git reset --mixed HEAD~1    # cofnij commit i staging, zostaw w working dir
git reset --hard HEAD~1     # cofnij wszystko (UWAGA: straci zmiany!)

# 💡 TIP: Bezpieczne cofanie z revert
git revert HEAD             # tworzy nowy commit cofający ostatni
git revert commit_hash      # cofnij konkretny commit
```

### Reflog - ratowanie "utraconych" commitów

```bash
# Historia wszystkich operacji
git reflog                  # pokazuje historię HEAD
git reflog show branch_name # historia konkretnego branch

# Odzyskiwanie commitów
git reset --hard HEAD@{5}   # wróć do stanu sprzed 5 operacji
git checkout HEAD@{5}       # sprawdź stan sprzed 5 operacji

# 💡 TIP: Reflog ma expiry, domyślnie 90 dni
git reflog expire --expire=never --all  # nigdy nie usuwaj
```

## Branche i merging

### Praca z branchami

```bash
# Tworzenie i przełączanie branch
git branch feature-branch        # stwórz branch
git checkout feature-branch      # przełącz na branch
git checkout -b feature-branch   # stwórz i przełącz

# Lista branch
git branch                  # lokalne branch
git branch -r              # remote branch
git branch -a              # wszystkie branch

# Usuwanie branch
git branch -d branch_name   # usuń (tylko jeśli merged)
git branch -D branch_name   # usuń na siłę

# 💡 TIP: Nowa składnia (Git 2.23+)
git switch feature-branch   # przełącz branch
git switch -c new-branch    # stwórz i przełącz
git restore file.txt        # przywróć plik
```

### Mergowanie

```bash
# Merge branch do current
git merge feature-branch    # fast-forward lub merge commit
git merge --no-ff feature-branch  # zawsze stwórz merge commit
git merge --squash feature-branch # squash wszystkie commity

# Rozwiązywanie konfliktów
git status                  # zobacz pliki z konfliktami
# Edytuj pliki, usuń markery konfliktów
git add resolved_file.txt
git commit                  # dokończ merge

# 💡 TIP: Abort merge jeśli coś poszło nie tak
git merge --abort
```

## Remote repositories

### Praca z remote

```bash
# Dodawanie remote
git remote add origin https://github.com/user/repo.git
git remote -v              # pokaż remote URLs

# Fetch vs Pull
git fetch origin           # pobierz zmiany (nie merguj)
git pull origin main       # pobierz i zmerguj
git pull --rebase origin main  # pobierz i rebase

# Push
git push origin main       # wyślij na remote
git push -u origin main    # ustaw upstream
git push --all             # wyślij wszystkie branch
git push --tags            # wyślij tagi

# 💡 TIP: Force push (OSTROŻNIE!)
git push --force-with-lease origin main  # bezpieczniejszy force push
```

## Zaawansowane zarządzanie commitami

### Rebase - przepisywanie historii

```bash
# Podstawowy rebase
git rebase main            # przenieś current branch na main
git rebase -i HEAD~3       # interaktywny rebase ostatnich 3 commitów

# Opcje w interaktywnym rebase:
# pick   - pozostaw commit
# reword - zmień message
# edit   - zatrzymaj się do edycji
# squash - połącz z poprzednim
# drop   - usuń commit

# 💡 TIP: Autosquash
git commit --fixup=commit_hash    # automatycznie oznacz do squash
git rebase -i --autosquash HEAD~5 # automatycznie arrange squash
```

### Cherry-pick

```bash
# Skopiuj konkretny commit
git cherry-pick commit_hash
git cherry-pick branch_name~2     # commit 2 od końca branch
git cherry-pick A..B              # zakres commitów

# Cherry-pick bez commita
git cherry-pick --no-commit commit_hash

# 💡 TIP: Cherry-pick merge commit
git cherry-pick -m 1 merge_commit_hash  # wybierz parent
```

### Stash - tymczasowe przechowywanie

```bash
# Podstawowe stash
git stash                   # schowaj zmiany
git stash push -m "WIP: feature X"  # z opisem
git stash list             # lista stash
git stash pop              # przywróć ostatni stash (usuń ze stash)
git stash apply            # przywróć (zostaw w stash)

# Zarządzanie stash
git stash show stash@{0}   # pokaż zmiany w stash
git stash drop stash@{0}   # usuń konkretny stash
git stash clear            # usuń wszystkie stash

# 💡 TIP: Partial stash
git stash push -p          # wybierz co stashować
git stash push -- file.txt  # stash tylko konkretny plik
```

## Dobre praktyki commitowania

### Konwencje commit messages

```bash
# Conventional Commits format:
# <type>[optional scope]: <description>
#
# [optional body]
#
# [optional footer(s)]

# Przykłady:
git commit -m "feat: add user authentication"
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update API documentation"
git commit -m "style: format code according to style guide"
git commit -m "refactor: extract user service class"
git commit -m "test: add unit tests for user service"
git commit -m "chore: update dependencies"

# 💡 TIP: Template commit message
cat > ~/.gitmessage << EOF
# <type>: (If applied, this commit will...) <subject> (Max 50 char)
# |<----  Using a Maximum Of 50 Characters  ---->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or other resources
# Example: Github issue #23

# --- COMMIT END ---
# Type can be 
#    feat     (new feature)
#    fix      (bug fix)
#    refactor (refactoring code)
#    style    (formatting, missing semi colons, etc; no code change)
#    docs     (changes to documentation)
#    test     (adding or refactoring tests; no production code change)
#    chore    (updating grunt tasks etc; no production code change)
# --------------------
EOF

git config --global commit.template ~/.gitmessage
```

### Strategie commitowania

```bash
# 1. Atomic commits - jeden logiczny change na commit
# DOBRE:
git add user_service.py
git commit -m "feat: add user authentication service"
git add login_view.py  
git commit -m "feat: implement login view"

# ZŁE:
git add user_service.py login_view.py
git commit -m "add authentication stuff"

# 2. WIP commits during development
git commit -m "WIP: working on authentication"
# Później squash przed push:
git rebase -i HEAD~3

# 💡 TIP: Użyj pre-commit hooks
# .git/hooks/prepare-commit-msg
#!/bin/sh
echo "# Please include ticket number in commit message" >> "$1"
```

## Aliasy i konfiguracja

### Przydatne aliasy

```bash
# Podstawowe aliasy
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status

# Zaawansowane aliasy
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'

# Piękny log
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

# Show files w commit
git config --global alias.ll 'log --stat --abbrev-commit'

# 💡 TIP: Alias do szybkiego commit
git config --global alias.ac '!git add -A && git commit -m'
# Użycie: git ac "commit message"
```

### Globalne ustawienia

```bash
# Edytor
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"          # Vim

# Merge tool
git config --global merge.tool vimdiff
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Automatyczne ustawienia
git config --global push.default simple      # tylko current branch
git config --global pull.rebase true        # rebase zamiast merge przy pull
git config --global rebase.autoStash true   # auto stash przed rebase

# 💡 TIP: Konfiguracja dla różnych systemów
git config --global core.autocrlf true      # Windows
git config --global core.autocrlf input     # Unix/Mac
```

## Workflow patterns

### GitFlow
```bash
# Main branches: main, develop
# Supporting: feature/*, release/*, hotfix/*

# Feature branch
git checkout develop
git checkout -b feature/new-login
# ... praca ...
git checkout develop
git merge --no-ff feature/new-login
git branch -d feature/new-login

# Release branch
git checkout develop
git checkout -b release/1.0.0
# ... bug fixes ...
git checkout main
git merge --no-ff release/1.0.0
git tag -a v1.0.0
git checkout develop
git merge --no-ff release/1.0.0
```

### GitHub Flow (prostszy)
```bash
# Tylko main branch + feature branches
git checkout main
git pull origin main
git checkout -b feature/fix-bug
# ... praca ...
git push origin feature/fix-bug
# Create Pull Request
# Po merge: usuń branch
```

## Tips and Tricks

### 1. **Szybkie shortcuts**
```bash
# Przejdź do poprzedniego branch
git checkout -

# Przejdź do main/master
git checkout $(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# 💡 TIP: Znajdź main branch automatycznie
git config --global alias.main '!git checkout $(git symbolic-ref refs/remotes/origin/HEAD | sed "s@^refs/remotes/origin/@@")'
```

### 2. **Wyszukiwanie w historii**
```bash
# Znajdź commit który wprowadził/usunął tekst
git log -S "function_name" --oneline

# Znajdź kiedy linia została dodana/zmieniona
git blame file.txt
git blame -L 10,20 file.txt  # tylko linie 10-20

# 💡 TIP: Git bisect dla znajdowania bugów
git bisect start
git bisect bad              # current commit is bad
git bisect good v1.0        # tag v1.0 was good
# Git będzie propose commits do testowania
git bisect good/bad         # depending on test result
git bisect reset           # when done
```

### 3. **Cleaning up**
```bash
# Usuń untracked files
git clean -n               # dry run - pokaż co zostanie usunięte
git clean -f               # usuń pliki
git clean -fd              # usuń pliki i foldery
git clean -fX              # usuń tylko ignored files

# Prune remote branches
git remote prune origin    # usuń ref do usuniętych remote branch
git fetch --prune          # automatycznie podczas fetch

# 💡 TIP: Automatyczne cleanup
git config --global fetch.prune true
```

### 4. **Ignorowanie plików**
```bash
# .gitignore patterns
*.log                      # wszystkie .log files
build/                     # folder build
!important.log            # except important.log
temp-*                     # temp- prefix

# Gitignore dla już tracked files
git rm --cached file.txt
echo "file.txt" >> .gitignore

# 💡 TIP: Global gitignore
git config --global core.excludesfile ~/.gitignore_global
```

### 5. **Debugging tricks**
```bash
# Zobacz co się zmieniło w każdej linii
git annotate file.txt

# Sprawdź configuration
git config --list --show-origin

# Debug git commands
GIT_TRACE=true git status
GIT_CURL_VERBOSE=true git push

# 💡 TIP: Git statistics
git shortlog -s -n         # commits per author
git log --since="1 month ago" --pretty=tformat: --numstat | gawk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }'
```

Git to potężne narzędzie - te komendy i triki pomogą w codziennej pracy! 🚀

---

# 🇬🇧 ENGLISH VERSION

# Git - Basic Commands, Tips and Tricks + Commit Management

## Basic Git commands

### Initialization and configuration

```bash
# Initialize repository
git init

# Global user configuration
git config --global user.name "John Smith"
git config --global user.email "john@example.com"

# Repository-specific configuration
git config user.name "John Smith"
git config user.email "john.smith@work.com"

# Check configuration
git config --list
git config user.name

# 💡 TIP: Different identities for different projects
git config --global includeIf."gitdir:~/work/".path ~/.gitconfig-work
```

### Status and basic operations

```bash
# Repository status
git status
git status --short           # short version
git status --porcelain       # for scripts

# Adding files
git add file.txt             # single file
git add .                    # all files in directory
git add *.py                 # all .py files
git add -A                   # all changes (added, deleted, modified)
git add -u                   # only modified and deleted (no new files)

# 💡 TIP: Interactive adding
git add -i                   # interactive mode
git add -p                   # patch mode - select parts of file
```

### Committing

```bash
# Basic commits
git commit -m "Description of changes"
git commit -am "Add and commit all modified files"

# Multi-line commit message
git commit -m "Commit title" -m "Longer description of changes"

# Commits with editor
git commit                   # opens editor
git commit --amend           # edit last commit

# 💡 TIP: Commit message template
git config --global commit.template ~/.gitmessage
```

## History management

### Viewing history

```bash
# Commit history
git log                      # full history
git log --oneline           # one line per commit
git log --graph             # graphical representation
git log --all --graph --oneline  # all branches + graph

# Filtering history
git log --since="2023-01-01"     # from date
git log --until="2023-12-31"     # to date
git log --author="John"          # by author
git log --grep="fix"            # by message
git log -S "function_name"      # by content

# 💡 TIP: Beautiful log format
git log --pretty=format:"%h - %an, %ar : %s"
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

### Differences between commits

```bash
# Checking differences
git diff                     # changes in working directory
git diff --staged           # changes in staging area
git diff HEAD               # all uncommitted changes
git diff commit1 commit2    # between commits
git diff HEAD~1 HEAD        # last commit vs previous

# 💡 TIP: Differences ignoring whitespace
git diff --ignore-all-space
git diff --ignore-space-change
```

## Undoing changes

### Different ways to undo

```bash
# Undoing changes in working directory
git checkout -- file.txt    # undo changes in file
git checkout .              # undo all changes

# Undoing from staging area
git reset HEAD file.txt     # remove from staging (keep changes)
git reset HEAD              # remove everything from staging

# Undoing commits
git reset --soft HEAD~1     # undo commit, keep changes in staging
git reset --mixed HEAD~1    # undo commit and staging, keep in working dir
git reset --hard HEAD~1     # undo everything (WARNING: loses changes!)

# 💡 TIP: Safe undoing with revert
git revert HEAD             # creates new commit undoing the last one
git revert commit_hash      # undo specific commit
```

### Reflog - recovering "lost" commits

```bash
# History of all operations
git reflog                  # shows HEAD history
git reflog show branch_name # history of specific branch

# Recovering commits
git reset --hard HEAD@{5}   # return to state 5 operations ago
git checkout HEAD@{5}       # check state 5 operations ago

# 💡 TIP: Reflog has expiry, default 90 days
git reflog expire --expire=never --all  # never delete
```

## Branches and merging

### Working with branches

```bash
# Creating and switching branches
git branch feature-branch        # create branch
git checkout feature-branch      # switch to branch
git checkout -b feature-branch   # create and switch

# List branches
git branch                  # local branches
git branch -r              # remote branches
git branch -a              # all branches

# Deleting branches
git branch -d branch_name   # delete (only if merged)
git branch -D branch_name   # force delete

# 💡 TIP: New syntax (Git 2.23+)
git switch feature-branch   # switch branch
git switch -c new-branch    # create and switch
git restore file.txt        # restore file
```

### Merging

```bash
# Merge branch to current
git merge feature-branch    # fast-forward or merge commit
git merge --no-ff feature-branch  # always create merge commit
git merge --squash feature-branch # squash all commits

# Resolving conflicts
git status                  # see files with conflicts
# Edit files, remove conflict markers
git add resolved_file.txt
git commit                  # complete merge

# 💡 TIP: Abort merge if something went wrong
git merge --abort
```

## Remote repositories

### Working with remote

```bash
# Adding remote
git remote add origin https://github.com/user/repo.git
git remote -v              # show remote URLs

# Fetch vs Pull
git fetch origin           # fetch changes (don't merge)
git pull origin main       # fetch and merge
git pull --rebase origin main  # fetch and rebase

# Push
git push origin main       # send to remote
git push -u origin main    # set upstream
git push --all             # send all branches
git push --tags            # send tags

# 💡 TIP: Force push (CAREFUL!)
git push --force-with-lease origin main  # safer force push
```

## Advanced commit management

### Rebase - rewriting history

```bash
# Basic rebase
git rebase main            # move current branch onto main
git rebase -i HEAD~3       # interactive rebase of last 3 commits

# Options in interactive rebase:
# pick   - keep commit
# reword - change message
# edit   - stop for editing
# squash - combine with previous
# drop   - remove commit

# 💡 TIP: Autosquash
git commit --fixup=commit_hash    # automatically mark for squash
git rebase -i --autosquash HEAD~5 # automatically arrange squash
```

### Cherry-pick

```bash
# Copy specific commit
git cherry-pick commit_hash
git cherry-pick branch_name~2     # commit 2 from end of branch
git cherry-pick A..B              # range of commits

# Cherry-pick without commit
git cherry-pick --no-commit commit_hash

# 💡 TIP: Cherry-pick merge commit
git cherry-pick -m 1 merge_commit_hash  # choose parent
```

### Stash - temporary storage

```bash
# Basic stash
git stash                   # stash changes
git stash push -m "WIP: feature X"  # with description
git stash list             # list stashes
git stash pop              # restore last stash (remove from stash)
git stash apply            # restore (keep in stash)

# Managing stashes
git stash show stash@{0}   # show changes in stash
git stash drop stash@{0}   # remove specific stash
git stash clear            # remove all stashes

# 💡 TIP: Partial stash
git stash push -p          # choose what to stash
git stash push -- file.txt  # stash only specific file
```

## Good committing practices

### Commit message conventions

```bash
# Conventional Commits format:
# <type>[optional scope]: <description>
#
# [optional body]
#
# [optional footer(s)]

# Examples:
git commit -m "feat: add user authentication"
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update API documentation"
git commit -m "style: format code according to style guide"
git commit -m "refactor: extract user service class"
git commit -m "test: add unit tests for user service"
git commit -m "chore: update dependencies"

# 💡 TIP: Template commit message
cat > ~/.gitmessage << EOF
# <type>: (If applied, this commit will...) <subject> (Max 50 char)
# |<----  Using a Maximum Of 50 Characters  ---->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or other resources
# Example: Github issue #23

# --- COMMIT END ---
# Type can be 
#    feat     (new feature)
#    fix      (bug fix)
#    refactor (refactoring code)
#    style    (formatting, missing semi colons, etc; no code change)
#    docs     (changes to documentation)
#    test     (adding or refactoring tests; no production code change)
#    chore    (updating grunt tasks etc; no production code change)
# --------------------
EOF

git config --global commit.template ~/.gitmessage
```

### Commit strategies

```bash
# 1. Atomic commits - one logical change per commit
# GOOD:
git add user_service.py
git commit -m "feat: add user authentication service"
git add login_view.py  
git commit -m "feat: implement login view"

# BAD:
git add user_service.py login_view.py
git commit -m "add authentication stuff"

# 2. WIP commits during development
git commit -m "WIP: working on authentication"
# Later squash before push:
git rebase -i HEAD~3

# 💡 TIP: Use pre-commit hooks
# .git/hooks/prepare-commit-msg
#!/bin/sh
echo "# Please include ticket number in commit message" >> "$1"
```

## Aliases and configuration

### Useful aliases

```bash
# Basic aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status

# Advanced aliases
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'

# Beautiful log
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

# Show files in commit
git config --global alias.ll 'log --stat --abbrev-commit'

# 💡 TIP: Alias for quick commit
git config --global alias.ac '!git add -A && git commit -m'
# Usage: git ac "commit message"
```

### Global settings

```bash
# Editor
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"          # Vim

# Merge tool
git config --global merge.tool vimdiff
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Automatic settings
git config --global push.default simple      # only current branch
git config --global pull.rebase true        # rebase instead of merge on pull
git config --global rebase.autoStash true   # auto stash before rebase

# 💡 TIP: Configuration for different systems
git config --global core.autocrlf true      # Windows
git config --global core.autocrlf input     # Unix/Mac
```

## Workflow patterns

### GitFlow
```bash
# Main branches: main, develop
# Supporting: feature/*, release/*, hotfix/*

# Feature branch
git checkout develop
git checkout -b feature/new-login
# ... work ...
git checkout develop
git merge --no-ff feature/new-login
git branch -d feature/new-login

# Release branch
git checkout develop
git checkout -b release/1.0.0
# ... bug fixes ...
git checkout main
git merge --no-ff release/1.0.0
git tag -a v1.0.0
git checkout develop
git merge --no-ff release/1.0.0
```

### GitHub Flow (simpler)
```bash
# Only main branch + feature branches
git checkout main
git pull origin main
git checkout -b feature/fix-bug
# ... work ...
git push origin feature/fix-bug
# Create Pull Request
# After merge: delete branch
```

## Tips and Tricks

### 1. **Quick shortcuts**
```bash
# Go to previous branch
git checkout -

# Go to main/master
git checkout $(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# 💡 TIP: Find main branch automatically
git config --global alias.main '!git checkout $(git symbolic-ref refs/remotes/origin/HEAD | sed "s@^refs/remotes/origin/@@")'
```

### 2. **Searching in history**
```bash
# Find commit that introduced/removed text
git log -S "function_name" --oneline

# Find when line was added/changed
git blame file.txt
git blame -L 10,20 file.txt  # only lines 10-20

# 💡 TIP: Git bisect for finding bugs
git bisect start
git bisect bad              # current commit is bad
git bisect good v1.0        # tag v1.0 was good
# Git will propose commits to test
git bisect good/bad         # depending on test result
git bisect reset           # when done
```

### 3. **Cleaning up**
```bash
# Remove untracked files
git clean -n               # dry run - show what will be removed
git clean -f               # remove files
git clean -fd              # remove files and folders
git clean -fX              # remove only ignored files

# Prune remote branches
git remote prune origin    # remove refs to deleted remote branches
git fetch --prune          # automatically during fetch

# 💡 TIP: Automatic cleanup
git config --global fetch.prune true
```

### 4. **Ignoring files**
```bash
# .gitignore patterns
*.log                      # all .log files
build/                     # build folder
!important.log            # except important.log
temp-*                     # temp- prefix

# Gitignore for already tracked files
git rm --cached file.txt
echo "file.txt" >> .gitignore

# 💡 TIP: Global gitignore
git config --global core.excludesfile ~/.gitignore_global
```

### 5. **Debugging tricks**
```bash
# See what changed in each line
git annotate file.txt

# Check configuration
git config --list --show-origin

# Debug git commands
GIT_TRACE=true git status
GIT_CURL_VERBOSE=true git push

# 💡 TIP: Git statistics
git shortlog -s -n         # commits per author
git log --since="1 month ago" --pretty=tformat: --numstat | gawk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }'
```

Git is a powerful tool - these commands and tricks will help in daily work! 🚀