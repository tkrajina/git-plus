#!/usr/bin/python
# -*- coding: utf-8 -*-

import pdb

import os as mod_os
import os.path as mod_path
import sys as mod_sys

def assert_in_git_repository():
    success, lines = execute_git('status', output=False)
    if not success:
        print 'Not a git repository!!!'
        mod_sys.exit(1)

def execute_command(command, output=True, prefix='', grep=None):
    result = ''
    p = mod_os.popen(command)
    for line in p:
        output_line = prefix + ('%s' % line).rstrip() + '\n'
        if not grep or grep in output_line:
            if output and output_line:
                print output_line.rstrip()
                mod_sys.stdout.flush()
            result += output_line

    return (not p.close(), result)

def execute_git(command, output=True, prefix='', grep=None):
    return execute_command('git %s' % command, output, prefix, grep)

def get_branches(remote=False, all=False):
    git_command = 'branch'
    if remote:
        git_command += ' -r'
    if all:
        git_command += ' -a'
    success, result = execute_git(git_command, output=False)
    assert success
    assert result

    def _filter_branch(branch):
        if '*' in branch:
            # Current branch:
            return branch.replace('*', '').strip()
        elif '->' in branch:
            # Branch is an alias
            return branch.split('->')[0].strip()
        return branch.strip()

    lines = result.strip().split('\n')
    return map(_filter_branch, lines)

def delete_branch(branch, force=False):
    # TODO: Delete remote branches?
    execute_git('branch %s %s' % ('-D' if force else '-d', branch))

def get_config_properties():
    executed, output = execute_git('config -l', output=False)

    if not executed:
        print 'Error retrieving git config properties'
        mod_sys.exit(1)

    result = {}
	
    lines = output.split('\n')
    for line in lines:
        if '=' in line:
            pos = line.find('=')
            key = line[0 : pos].strip().lower()
            value = line[pos + 1 :].strip()
            result[key] = value
	
    return result

def is_changed():
    """ Checks if current project has any noncommited changes. """
    executed, changed_lines = execute_git('status --porcelain', output=False)
    merge_not_finished = mod_path.exists('.git/MERGE_HEAD')
    return changed_lines or merge_not_finished

