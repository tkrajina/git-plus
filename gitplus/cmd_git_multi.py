#!/usr/bin/env python3
# Copyright 2013 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import os.path as path
import datetime

from . import git
from . import utils

from typing import *

class term_colors:
    BLUE = '\033[34m'
    RESET = '\033[0m'

# Prefix for git command output:
PREFIX = '\t'

args = sys.argv[1:]
# If true, projects with same git command output will be groupped together:
group_by_output = True

# -c switch in command line, if true execute only if project not changed (i.e.
# the `git --porcelain` output is empty:
only_if_changed = False


def is_ignored(project: str) -> bool:
    return project in ignore_projects


def process_dir(dirname: str, depth: int) -> None:
    abs_dir_name = os.path.abspath(dirname)
    for file_name in os.listdir(dirname):
        if not single_project or single_project == file_name:
            os.chdir(abs_dir_name)

            if path.isdir(file_name):
                if path.exists('%s/.git' % file_name):
                    process_project(abs_dir_name, file_name)

                    if show_progress and group_by_output:
                        print('*', end=' ')
                        sys.stdout.flush()
                elif depth > 1:
                    process_dir(os.path.join(abs_dir_name, file_name), depth - 1)


def process_project(current_path: str, file_name: str) -> None:
    if is_ignored(file_name):
        return

    dir_path = '%s/%s' % (current_path, file_name)
    os.chdir(dir_path)

    output = ''

    if group_by_output:
        do_output = False
    else:
        do_output = True

    if not group_by_output:
        print(term_colors.BLUE+'%s:' % file_name+term_colors.RESET)

    execute = True
    if only_if_changed:
        execute = git.is_changed()
        if not execute:
            output = PREFIX + 'Not changed'
            if do_output:
                print(output)

    if execute:
        executed, result = git.execute_command(git_command, output=do_output, prefix=PREFIX, grep=grep)
        result = result.rstrip()

        if not executed:
            output = '\tError executing:%s:%s' % (git_command, result)
        elif result:
            output = result
        else:
            output = '\tOK'

    if group_by_output:
        if output in outputs:
            outputs[output].append(file_name)
        else:
            outputs[output] = [file_name]

show_progress = True

# If true, projects with same git command output will be groupped together:
group_by_output = False

# Check if to group results by output:
# Set by:
# 	git config --global 'multi.groupbyoutput' 1
# Unset by:
# 	git config --global --unset 'multi.groupbyoutput'
config_properties = git.get_config_properties()
group_by_output_config_key = 'multi.groupbyoutput'
if group_by_output_config_key in config_properties:
    group_by_output_config_value = config_properties[group_by_output_config_key]

    if group_by_output_config_value:
        if group_by_output_config_value.lower() in ('true', '1'):
            group_by_output = True

# Check if to do backup of projects:
backup = utils.has_arg(args, 'a', 'archive')

# Check if needed to be executed on only one project:
single_project = utils.get_arg(args, 'p', 'project')
if single_project and single_project[-1] == '/':
    single_project = single_project[: -1]

# Check projects which we don't need to be part of git multi commands execution:
ignore_projects: List[str] = []
except_projects = utils.get_arg(args, 'e', 'except')
if except_projects:
    ignore_projects = [x.strip() for x in except_projects.split(",")]

# Check if to execute only on projects which contain some changes:
only_if_changed = utils.has_arg(args, 'c', 'changed')

# Output only the current branch for all projects:
branch = utils.has_arg(args, 'b', 'branch')
branch_verbose = utils.has_arg(args, 'bv', 'branch-verbose')

# Specify depth for recursive search
depth = int(utils.get_arg(args, 'd', 'depth') or "1")

# Compute projects to be executed:
if path.exists('.multigit_ignore'):
    f = open('.multigit_ignore')
    for line in f:
        project = line.strip()
        ignore_projects.append(project)
    print('Ignoring:', ', '.join(ignore_projects))
    f.close()

# Execute backup?
if backup:
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    tar_name = 'git-repositories-%s.tar' % (now)

    executed, output = git.execute_command('tar cvf %s */.git */.gitignore' % tar_name, output=True)

    print('Saved git repositories to %s' % tar_name)

    sys.exit(0)

grep = None

# If no specific command is entered (i.e. only 'git multi'):
git_command = ['status', '-s']
if args:
    git_command = args

if branch_verbose:
    git_command = ['branch', '-v']
    group_by_output = True
    grep = '* '
elif branch:
    git_command = ['branch']
    grep = '* '

if git_command[0] == 'gitk':
    git_command = git_command
else:
    git_command.insert(0, 'git')

print('--------------------------------------------------------------------------------')
if grep:
    print('Executing: %s | grep %s' % (' '.join(git_command), grep))
else:
    print('Executing %s' % ' '.join(git_command))
print('--------------------------------------------------------------------------------')

# Used when group_by_output == True, keys are output, values are a list of projects
outputs: Dict[str, List[str]] = {}

if show_progress and group_by_output:
    print('Progress:', end=' ')
    sys.stdout.flush()

# Execute command on all subdirectories:
process_dir(os.getcwd(), depth)

if show_progress and group_by_output:
    print()
    print('--------------------------------------------------------------------------------')

# If group_by_output, then output them now:
if group_by_output:
    result_outputs = []
    output_keys = list(outputs.keys())
    output_keys.sort()
    for output in output_keys:
        projects = outputs[output]
        projects.sort()

        result_outputs.append([', '.join(projects) + ':', output])
        print()

    result_outputs.sort()
    for key, value in result_outputs:
        print(term_colors.BLUE+key+term_colors.RESET)
        print(value)
        print()
