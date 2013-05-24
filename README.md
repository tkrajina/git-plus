# Git plus

Git plus is a set of git utilities:

 * **git multi** execute a single git command on multiple git repositories
 * **git relation** show a relation between two branches/commits/tags
 * **git old-branches** find old/unused branches

## Git multi

If you have repositories ~/projects/repository1, ~/projects/repository2, ~/projects/repository3, ~/projects/repository4, ... First go to:

    cd ~/projects

Check the status of all repositories:

    git multi status

...which is the same as:

    git multi

Execute "git gui" only on repositories which contain some changes:

    git multi -c gui

Switch to "master" for all repositories:

    git multi checkout master

Create a "test" branch on all repositories and checkout it immediately:

    git multi checkout -b test

...and so on. The basic usage is simple "git multi normal_git_commands_here". In addition to this, "git multi -c git_commands" will execute "git_commands" only on changed repositories and "git multi -b" will show the current branch for all repositories.

If you want your "git multi" commands to always execute all except some repositories add them to the file ".multigit_ignore" in the same directory.

With:

    git multi -a

A .tar archive named git-repositories-yyyy-mm-dd-hh-mm.tar with all repositories in this directory (i.e. their .git directories) will be created.

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

## Git old-branches

# Installation

Add a this directory to your $PATH:

    export PATH=$PATH:/path/to/git-plus

License
-------

Git plus is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
