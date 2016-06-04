# Git plus

Git plus is a set of git utilities:

 * **git multi** execute a single git command on multiple git repositories
 * **git relation** show a relation between two branches/commits/tags
 * **git old-branches** find old/unused branches
 * **git recent** list branches ordered by last commit time

## Installation

Add this directory to your $PATH:

    export PATH=$PATH:/path/to/git-plus

On OSX using brew:

    brew install git-plus

Or using pip:

    pip install git-plus

## Git multi

If you have repositories ~/projects/repository1, ~/projects/repository2, ~/projects/repository3, ~/projects/repository4, ... First go to:

    cd ~/projects

Check the status of all repositories:

    git multi status

...which is the same as:

    git multi

Execute "git gui" only on repositories which contain some changes:

    git multi -c gui

Make the output quiet - do not show any output for repositories with no changes:

    git multi -q status

Switch to "master" for all repositories:

    git multi checkout master

Show all repositories that are not on the specified branch

    git multi -B <branch name>

Create a "test" branch on all repositories and checkout it immediately:

    git multi checkout -b test

...and so on. The basic usage is simple "git multi normal_git_commands_here". In addition to this, "git multi -c git_commands" will execute "git_commands" only on changed repositories and "git multi -b" will show the current branch for all repositories.

If you want your "git multi" commands to always execute all except some repositories add them to the file ".multigit_ignore" in the same directory.

With:

    git multi -a

A .tar archive named git-repositories-yyyy-mm-dd-hh-mm.tar.xz with all
repositories in this directory (i.e. their .git directories) will be created.

### Group by output

If you have many projects with same git commant output, for example:

    git multi status
    
    aaa:
    	# On branch master
    	nothing to commit (working directory clean)
    bbb:
    	# On branch TRUNK
    	nothing to commit (working directory clean)
    ccc:
    	# On branch master
    	nothing to commit (working directory clean)
    ddd:
    	# On branch master
    	nothing to commit (working directory clean)
    eee:
    	# On branch TRUNK
    	nothing to commit (working directory clean)

You can configure multi git to group projects with same output together:

    aaa, ccc, ddd:
    	# On branch master
    	nothing to commit (working directory clean)
    bbb, eee:
    	# On branch TRUNK
    	nothing to commit (working directory clean)

This can be done by setting:

    git config --global 'multi.groupbyoutput' 1

Or reset to default with:

    git config --global --unset 'multi.groupbyoutput'

## Git relation

Git relation gives you the relation between two commits/branches/tags. For example:

    get relation master test-branch

...will tell you if two branches are equals, or if master is AHEAD of test-branch or if master is BEHIND test-branch or if they diverged in some commit in history.

For example:

    $ git relation master test-branch
    master is AHEAD of test-branch

    Commits from test-branch to master:
      2176e45 Tomo Krajina git-multi in README, 18 hours ago
      50b2f79 Tomo Krajina + README, 18 hours ago

Another example:

    $ git relation branch-1 branch-2
    branch-1 and branch-2 DIVERGED, common point is 7e0bb439dd2aef4ff0262afec0a98461489becae

    Commits from 7e0bb439dd2aef4ff0262afec0a98461489becae to branch-1:
      3d0246b Tomo Krajina js namespace, 3 weeks ago
      60215aa Tomo Krajina Merge branch 'new-path-editor' into new-path-editor--js-namespace, 3 weeks ago
      1e76deb Tomo Krajina js namespace, 5 weeks ago

    Commits from 7e0bb439dd2aef4ff0262afec0a98461489becae to branch-2:
      359eff6 Tomo Krajina form event functions, 5 hours ago
      a99b5f8 Tomo Krajina ..., 3 weeks ago
      1d3b97c Tomo Krajina Preparations for marker handler, 3 weeks ago
      9546769 Tomo Krajina Removed all subscription stuff, 3 months ago

## Git old-branches

Old-branches can detect old/unused branches.

Find local branches older than 10 days:

    $ git old-branches -d 10

Find remote branches older than 60 days:

    $ git old-branches -r -d 60

Find local and remote branches older than 120 days:

    $ git old-branches -a -d 120

Find and remove branches older than 10 days:

    $ git old-branches -d 10 --delete
    Branch old-branch is older than 10 days (13.89)!
    Remove [yes/N] ?

Note that branches will not be removed unconditionally, you'll be asked once to confirm the deletion.

# Git recent

Find list of branches ordered by last commit time:

    git recent

Show only remote branches:

    git recent -r

Show all branches (local and remote)

    git recent -a

Show only **last** 10 branches:

    git recent -10

Show only **first** 15 branches:

    git recent 15

# License

Git plus is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
