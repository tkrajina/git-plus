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

from __future__ import print_function

import argparse
import time
import sys

from . import git

git.assert_in_git_repository()

parser = argparse.ArgumentParser(
    description='Detects (and possibly deletes) old unused branches')

parser.add_argument('--no-merged', action='store_true',
                    default=False, help='Only *not* merged branches')
parser.add_argument('--merged', action='store_true',
                    default=False, help='Only merged branches')
parser.add_argument('-r', '--remote', action='store_true',
                    default=False, help='Get remote branches')
parser.add_argument('-a', '--all', action='store_true',
                    default=False, help='Get all (local and remote) branches')
parser.add_argument('-d', '--days', default=180, type=int,
                    help='How many days old must a branch be')
parser.add_argument('--delete', action='store_true', default=False,
                    help='Remove branches older than ... days (you\'ll be asked to confirm the deletion)')

args = parser.parse_args()

now = time.time()

remote: bool = args.remote
all_branches: bool = args.all
merged: bool = args.merged
no_merged: bool = args.no_merged

branches = git.get_branches(remote, all_branches, merged=merged, no_merged=no_merged)
delete_all = False
for branch in branches:
    if remote and not branch.startswith("remotes/"):
        branch = f"remotes/{branch}"
    command = 'log ' + branch + ' -1 --format=%at --'
    success, result = git.execute_git(command, output=False)
    if not success:
        sys.stderr.write(command)
        sys.stderr.write(result)
        sys.exit(1)

    if len(result.strip()) == 0:
        print('Cannot find the age of %s' % branch)
    else:
        time_diff_seconds = int(now) - int(result)
        time_diff_days = int((float(time_diff_seconds) / (60*60*24)) * 100) / 100.

        #print 'Last commit in %s was %s days ago' % (branch, time_diff_days)

        if time_diff_days > args.days:
            print('Branch %s is older than %s days (%s)!' % (branch, args.days, time_diff_days))
            if args.delete:
                if delete_all:
                    answer = 'y'
                else:
                    answer = input('Remove [y/N/all] ?')

                if answer.lower() == 'all' and input(f"Really delete all filtered branches [y/N]?") == 'y':
                    delete_all = True
                    answer = 'y'

                if answer.lower() == 'y':
                    git.delete_branch(branch, force=True)
                else:
                    print('Not deleted')
