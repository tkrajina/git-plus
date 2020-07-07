from typing import *

def get_arg(args: List[str], short_name: str, long_name: str) -> Optional[str]:
    for i in range(len(args)):
        arg = args[i]
        if arg[0] != '-':
            return None
        if arg.startswith('--%s=' % long_name):
            args.remove(arg)
            return arg.replace('--%s=' % long_name, '')
        elif arg == '-%s' % short_name:
            result = args[i + 1]
            args.remove('-%s' % short_name)
            args.remove(result)
            return result
    return None


def has_arg(args: List[str], short_name: str, long_name: str) -> bool:
    for arg in args:
        if arg[0] != '-':
            return False
        if arg == '--%s' % long_name or arg == '-%s' % short_name:
            args.remove(arg)
            return True
    return False

