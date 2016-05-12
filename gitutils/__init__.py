#!/usr/bin/python
# -*- coding: utf-8 -*-

import os as mod_os
import os.path as mod_path
import sys as mod_sys
import subprocess
import xml.etree.ElementTree as mod_et


def assert_in_git_repository():
    success, lines = execute_git(['status'], output=False)
    if not success:
        print 'Not a git repository!!!'
        mod_sys.exit(1)


def execute_command(command, output=True, prefix='', grep=None):
    result = ''

    if type(command) is not list:
        raise Exception('string passed to execute_command', command)

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=-1)
    (cmdout, cmderr) = p.communicate()
    if cmdout is None or not cmdout.strip():
        return (p.returncode, cmdout.strip())

    for line in cmdout.strip().split('\n'):
        output_line = prefix + ('%s' % line).rstrip() + '\n'
        if not grep or grep in output_line:
            if output and output_line:
                print output_line.rstrip()
                mod_sys.stdout.flush()
            result += output_line

    return (not p.returncode, result)


def execute_git(command, output=True, prefix='', grep=None):
    return execute_command(['git']+command, output, prefix, grep)


def get_branches(remote=False, all=False, merged=None, no_merged=None):
    git_command = ['branch']

    if remote:
        git_command.append('-r')
    if all:
        git_command.append('-a')
    if merged is True:
        git_command.append('--merged')
    if no_merged is True:
        git_command.append('--no-merged')

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
    result = map(_filter_branch, lines)
    result = filter(lambda x: x, result)
    return result


def delete_branch(branch, force=False):
    if '/' in branch:
        if branch.startswith('remotes/'):
            branch = branch.replace('remotes/', '')
        parts = branch.split('/')
        if len(parts) == 2:
            origin_name, branch_name = parts
            execute_git(['push', origin_name, ':%s' % (branch_name)])
        else:
            print 'Don\'t know how to delete %s' % branch
    else:
        execute_git(['branch', '-D' if force else '-d', branch])


def get_config_properties():
    executed, output = execute_git(['config', '-l'], output=False)

    if not executed:
        print 'Error retrieving git config properties'
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


def is_changed():
    """ Checks if current project has any noncommited changes. """
    executed, changed_lines = execute_git(['status', '--porcelain'], output=False)
    merge_not_finished = mod_path.exists('.git/MERGE_HEAD')
    return changed_lines or merge_not_finished


def get_project_list_from_search(ignore_list=None):
    projects = []
    for file_name in mod_os.listdir('.'):
        if mod_path.isdir(file_name):
            if ignore_list and file_name in ignore_list:
                continue

            if mod_path.exists('%s/.git' % file_name):
                projects.append (file_name)
    return projects


def get_project_list_from_manifest(manifest, ignore_list):
    projects = []
    tree = mod_et.parse(manifest)
    root = tree.getroot()

    for prj in root.iter('project'):
        path = prj.attrib.get('path', None)
        if not path:
            continue

        if mod_path.isdir(path):
            if ignore_list and path in ignore_list:
                continue

            if mod_path.exists('%s/.git' % path):
                projects.append(path)
    return projects


def get_project_list(ignore_list=None):
    manifest = '.repo/manifest.xml'
    if mod_path.exists(manifest):
        print '## Using project list from repo manifest.'
        return get_project_list_from_manifest(manifest, ignore_list)
    else:
        print '## Using project list from directory search.'
        return get_project_list_from_search(ignore_list)
