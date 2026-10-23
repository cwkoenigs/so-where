#!/usr/bin/env python3
"""Link this checkout's so-where skill into existing agent runtimes."""
import argparse
from pathlib import Path
import re


def install(home):
    source=Path(__file__).resolve().parents[1]/'so-where'
    if not re.search(r'^name: so-where$',(source/'SKILL.md').read_text(),re.M):
        raise ValueError('Skill name does not match so-where')
    plans=[]
    for runtime in ['.codex','.claude']:
        runtime_dir=home/runtime
        if not runtime_dir.is_dir():
            continue
        target=runtime_dir/'skills/so-where'
        if target.exists() and not target.is_symlink():
            raise ValueError('Refusing to overwrite a real directory: '+str(target))
        plans.append((runtime,target))
    if not plans:
        raise ValueError('No existing Codex or Claude Code runtime found')
    for runtime,target in plans:
        target.parent.mkdir(exist_ok=True)
        if target.is_symlink():
            target.unlink()
        target.symlink_to(source,target_is_directory=True)
        if target.resolve()!=source or not (target/'references/dashboard.html').is_file():
            raise ValueError('Installed link did not resolve: '+str(target))
        print(runtime+': so-where linked to '+str(source))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,default=Path.home(),help='Runtime home; override for isolated tests')
    args=parser.parse_args()
    try:
        install(args.home)
    except (ValueError,OSError) as e:
        parser.exit(1,str(e)+'\n')
