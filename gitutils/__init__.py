# -*- coding: utf-8 -*-

import os.path as mod_path
import sys as mod_sys
import subprocess

from typing import *

def assert_in_git_repository() -> None:
    success, lines = execute_git('status', output=False)
    if not success:
        print('Not a git repository!!!')
        mod_sys.exit(1)


def execute_command(cmd: Union[str, List[str]], output: bool=True, prefix: str='', grep: Optional[str]=None) -> Tuple[bool, str]:
    result = ''

    command = cmd if type(cmd) is list else cmd.split(' ') # type: ignore

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=-1)
    (cmdout, cmderr) = p.communicate()
    if cmdout is None:
        return (0, "")

    for line in cmdout.decode('utf-8').split('\n'):
        output_line = prefix + ('%s' % line).rstrip() + '\n'
        if not grep or grep in output_line:
            if output and output_line:
                print(output_line.rstrip())
                mod_sys.stdout.flush()
            result += output_line

    return (not p.returncode, result)


def execute_git(command: str, output: bool=True, prefix: str='', grep: str="") -> Tuple[bool, str]:
    return execute_command('git %s' % command, output, prefix, grep)


def get_branches(remote: bool=False, all: bool=False, merged: bool=False, no_merged: bool=False) -> List[str]:
    git_command = 'branch'

    if remote:
        git_command += ' -r'
    if all:
        git_command += ' -a'
    if merged is True:
        git_command += ' --merged'
    if no_merged is True:
        git_command += ' --no-merged'

    success, result = execute_git(git_command, output=False)

    assert success
    assert result

    def _filter_branch(branch: str) -> str:
        if '*' in branch:
            # Current branch:
            return branch.replace('*', '').strip()
        elif '->' in branch:
            # Branch is an alias
            return branch.split('->')[0].strip()
        return branch.strip()

    lines = result.strip().split('\n')
    lines = list(map(_filter_branch, lines))
    lines = [line for line in lines if line]
    return lines


def delete_branch(branch: str, force: bool=False) -> None:
    if branch.startswith('remotes/'):
        if branch.startswith('remotes/'):
            branch = branch.replace('remotes/', '')
        parts = branch.split('/')
        if len(parts) >= 2:
            origin_name, branch_name = parts[0], "/".join(parts[1:])
            execute_git('push %s :%s' % (origin_name, branch_name))
        else:
            print('Don\'t know how to delete %s' % branch)
    else:
        execute_git('branch %s %s' % ('-D' if force else '-d', branch))


def get_config_properties() -> Dict[str, str]:
    executed, output = execute_git('config -l', output=False)

    if not executed:
        print('Error retrieving git config properties')
        mod_sys.exit(1)

    result = {}

    lines = output.split('\n')
    for line in lines:
        if '=' in line:
            pos = line.find('=')
            key = line[0: pos].strip().lower()
            value = line[pos + 1:].strip()
            result[key] = value

    return result


def is_changed() -> bool:
    """ Checks if current project has any noncommited changes. """
    executed, changed_lines = execute_git('status --porcelain', output=False)
    merge_not_finished = mod_path.exists('.git/MERGE_HEAD')
    return cast(bool, changed_lines.strip() or merge_not_finished)
