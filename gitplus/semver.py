import sys

from . import git

from typing import *

MAX_SUBVERSION = 1000000

class Version:
    def __init__(self, tag: str, prefix: str, major: int, minor: int, patch: int, suffix: str):
        self.tag = tag
        self.prefix = prefix
        self.major = major
        self.minor = minor
        self.patch = patch
        self.suffix = suffix
        if major >= MAX_SUBVERSION:
            raise Exception(f"Invalid major: {major}")
        if minor >= MAX_SUBVERSION:
            raise Exception(f"Invalid minor: {minor}")
        if patch >= MAX_SUBVERSION:
            raise Exception(f"Invalid patch: {patch}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}{'-' + self.suffix if self.suffix else ''}"

    def __lt__(self, other: "Version") -> bool:
        return self.to_n() < other.to_n()

    def to_n(self) -> int:
        return self.major * MAX_SUBVERSION**2 + self.minor * MAX_SUBVERSION + self.patch

def parse_tag_as_semver(tag: str) -> Optional[Version]:
    if not tag:
        return None
    prefix = ""
    if tag[0] == "v" or tag[0] == "V":
        prefix = tag[0]
        parts = tag[1:].split(".")
    else:
        parts = tag.split(".")
    if len(parts) != 3:
        return None
    try:
        patch = parts[2]
        suffix = ""
        if "-" in patch:
            patch, sufix = patch.split("-", 1)
        return Version(tag, prefix, int(parts[0]), int(parts[1]), int(patch), suffix)
    except:
        return None

def get_all_versions_ordered(output_non_versions: bool=False) -> List[Version]:
    success, tags = git.execute_git("tag", output=False)
    if not success:
        print('Error getting tags')
        sys.exit(1)
    versions = []
    for line in tags.split("\n"):
        line = line.strip()
        if not line:
            continue
        version = parse_tag_as_semver(line)
        if not version:
            if output_non_versions:
                print(f"{line} not a tag")
        else:
            versions.append(version)
    versions.sort()
    return versions
