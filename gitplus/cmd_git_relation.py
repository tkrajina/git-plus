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
import argparse

from . import git
from . import semver

git.assert_in_git_repository()

parser = argparse.ArgumentParser(
    description='Show a relation between two git commits/tags/branches')

parser.add_argument('branch_1', metavar='branch_1', type=str, default='HEAD', nargs='?',
                   help='the one commit/tag/branch')
parser.add_argument('branch_2', metavar='branch_2', type=str, nargs='?', default='HEAD',
                   help='the other commit/tag/branch (default HEAD)')
parser.add_argument('-b', '--brief', action='store_true',
                    default=False, help='brief output')
parser.add_argument('-u', '--upstream', action='store_true',
                    default=False, help='relation with upstream branch')
parser.add_argument('-a', '--all', action='store_true',
                    default=False, help='show all commits')
parser.add_argument('-sv', '--semver', action='store_true',
                    default=False, help='relation with latest semver tag')
parser.add_argument('-svn', '--semvern', type=int,
                    default=0, help='relation with semver tag before n semantic versions')

args = parser.parse_args()

branch_1: str = args.branch_1
branch_2: str = args.branch_2
branch_2_latest_semver: bool = args.semver
branch_2_n_old_semver: int = args.semvern

if branch_2_latest_semver:
    branch_2_n_old_semver = 1
if branch_2_n_old_semver:
    versions = semver.get_all_versions_ordered()
    if not versions:
        print('no semver tags found')
        sys.exit(1)
    try:
        branch_2 = versions[-branch_2_n_old_semver].tag
    except:
        print(f'too few semver tags for {branch_2_n_old_semver}')
        sys.exit(1)

if args.upstream:
    if branch_2:
        print('cannot use --upstream and specify the second branch')
        sys.exit(1)
    success, optput = git.execute_git(f'rev-parse --abbrev-ref {branch_1}@{{u}}', output=False)
    if not success:
        print('error getting upstream branch')
        sys.exit(1)
    first_line = optput.split("\n")[0]
    branch_2 = first_line


def print_log(commit_1: str, commit_2: str, all_commits: bool=False) -> None:
    success, log = git.execute_git(
        'log %s..%s --format=%%x20%%x20%%x20%%h%%x20%%Cgreen%%an%%Creset%%x20\"%%Cred%%s%%Creset\",%%x20%%ar' % (commit_1, commit_2),
        output=False)
    if not success:
        print('Error retrieving log %s..%s' % (commit_1, commit_2))
        sys.exit(1)
    result = log.rstrip()

    lines = result.split('\n')

    print()
    print('%s commits from \033[1;34m%s\033[0m to \033[1;34m%s\033[0m:' % (len(lines), commit_1, commit_2))

    if all_commits or len(lines) < 30:
        print(result)
        return

    first = lines[:10]
    last = lines[-10:]

    lines = first + ['   ...%s more commits...' % (len(lines) - len(first) - len(last))] + last

    print('\n'.join(lines))

branch_1_sha1 = git.get_git_sha1(branch_1)
branch_2_sha1 = git.get_git_sha1(branch_2)

success, merge_base = git.execute_git('merge-base %s %s' % (branch_1, branch_2),
                                               output=False)
merge_base = merge_base.strip()
if not success:
    print('Can\'t find merge base for %s and %s' % (branch_1, branch_2))
    sys.exit(1)

elif merge_base == branch_1_sha1 and merge_base == branch_2_sha1:
    print('\033[1;34m%s\033[0m \033[1;31mEQUALS\033[0m \033[1;34m%s\033[0m' % (branch_1, branch_2))
elif merge_base == branch_1_sha1:
    print('\033[1;34m%s\033[0m is \033[1;31mBEHIND\033[0m \033[1;34m%s\033[0m by %d commits' % (branch_1, branch_2, git.distance_to_commit(branch_1, branch_2)))
    if not args.brief:
        print_log(branch_1, branch_2, args.all)
elif merge_base == branch_2_sha1:
    print('\033[1;34m%s\033[0m is \033[1;31mAHEAD\033[0m of \033[1;34m%s\033[0m by %d commits' % (branch_1, branch_2, git.distance_to_commit(branch_2, branch_1)))
    if not args.brief:
        print_log(branch_2, branch_1, args.all)
else:
    print('\033[1;34m%s\033[0m and \033[1;34m%s\033[0m \033[1;31mDIVERGED\033[0m by respectively %d and %d commits' % (branch_1, branch_2, git.distance_to_commit(merge_base, branch_1), git.distance_to_commit(merge_base, branch_2)))
    if not args.brief:
        print('common point is \033[1;34m%s\033[0m'%(merge_base))
        print_log(merge_base, branch_1, args.all)
        print_log(merge_base, branch_2, args.all)
