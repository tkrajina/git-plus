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

import sys as mod_sys
import argparse as mod_argparse
import time as mod_time

from . import git

from typing import *

git.assert_in_git_repository()

parser = mod_argparse.ArgumentParser(
    description='Show list of branches sorted by last commit time')

parser.add_argument('-r', '--remote', action='store_true',
                    default=False, help='Get remote branches')
parser.add_argument('-b', '--brief', action='store_true',
                    default=False, help='brief output')
parser.add_argument('-a', '--all', action='store_true',
                    default=False, help='Get all (local and remote) branches')
parser.add_argument('-n', '--no-merged', action='store_true',
                    default=False, help='Only *not* merged branches')
parser.add_argument('-m', '--merged', action='store_true',
                    default=False, help='Only merged branches')
parser.add_argument('entries', metavar='entries', type=int, default=1000, nargs='?',
                    help='Number of entries (negative number if you want the last N entries)')
parser.add_argument('-x', '--execute-command', help='Execute command with branch name')
parser.add_argument('-ch', '--checkout', action='store_true',
                    default=False, help='Checkout to branch')
parser.add_argument('-chn', '--checkoutnth',
                    default=False, help='Checkout to n-th branch')
parser.add_argument('-me', '--merge', action='store_true',
                    default=False, help='Merge recent branch')
parser.add_argument('-men', '--mergenth', action='store_true',
                    default=False, help='Merge nth recent branch')

args = parser.parse_args()

now = mod_time.time()

times_and_branches = []

brief: bool = args.brief
merged: bool = args.merged
remote: bool = args.remote
get_all: bool = args.all
no_merged: bool = args.no_merged
execute_command = args.execute_command
merge = args.merge
merge_nth = args.mergenth

if args.checkout:
    execute_command = "checkout"

nth_branch = execute_command or merge or merge_nth

branches = git.get_branches(remote, merged=merged, no_merged=no_merged, all=get_all)
for branch in branches:
    cmd = 'log ' + branch + ' -1 --format=%at --'
    success, result = git.execute_git(cmd, output=False)
    if not success:
        mod_sys.stderr.write(cmd)
        mod_sys.stderr.write(result)
        mod_sys.exit(1)

    time_diff_seconds = int(now) - int(result)
    if (not success) or (len(result.strip()) == 0):
        print('Cannot find the age of %s' % branch)
    elif brief:
        times_and_branches.append((time_diff_seconds, branch))
    else:
        time_diff_days = int((float(time_diff_seconds) / (60*60*24)) * 100) / 100.
        times_and_branches.append((time_diff_seconds, '%10s days: %s' % (time_diff_days, branch), ))

times_and_branches.sort()

try:
    entries = int(args.entries)
except:
    entries = 1000

if entries > 0:
    times_and_branches = times_and_branches[:entries]
if entries < 0:
    times_and_branches = times_and_branches[entries:]

n = 0
for _, branch in times_and_branches:
    n += 1
    if nth_branch:
        print(f"  [{n}] {branch}")
    else:
        print(branch)

if nth_branch:
    nth = None
    try:
        if merge_nth:
            nth = int(merge_nth)
        if execute_command:
            nth = int(input(f"Execute {execute_command} with branch (1-{n})? "))
        if merge:
            nth = int(input(f"Merge (1-{n})? "))
    except:
        mod_sys.exit(1)

    if not nth:
        mod_sys.exit(1)

    branch = times_and_branches[nth-1][1].split(":")[1].strip()

    if execute_command:
        git.execute_git([execute_command, branch])
    if merge or merge_nth:
        git.execute_git(["merge", branch])