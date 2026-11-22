#!/usr/bin/env python3
"""Register an existing physics environment; never create or install one."""

import argparse
import difflib
import json
from pathlib import Path
import shlex
import subprocess
import sys

CONFIG = '.physics-env.local.json'
START = '<!-- agent-skills:physics-environment:start -->'
END = '<!-- agent-skills:physics-environment:end -->'
PROBE = '''import importlib.util, json, os, sys
from pathlib import Path
p = Path(sys.prefix)
is_conda = (p / "conda-meta").is_dir() or os.environ.get("CONDA_PREFIX") == str(p)
kind = "venv" if sys.prefix != sys.base_prefix else "conda" if is_conda else "system"
base = kind == "conda" and ((p / "condabin").is_dir() or
    os.environ.get("CONDA_DEFAULT_ENV") == "base" and os.environ.get("CONDA_PREFIX") == str(p))
print(json.dumps(dict(kind=kind, prefix=str(p), python=sys.executable,
    is_conda_base=base, hepyy_available=importlib.util.find_spec("hepyy") is not None)))
'''

POLICY = '''## Physics environment

Read `.physics-env.local.json` in this project before running commands. It records
the existing environment's type, prefix, Python executable, and execution command.
If it is absent or its interpreter no longer exists, consult the project setup
instructions or ask for the intended environment; do not silently create one.

Use the hepyy skill for HENP package management and analyses. If unavailable,
consult https://github.com/matplo/agent-skills/tree/main/skills/hepyy.
Run Python, installs, tests, scripts, and notebook kernels in the registered
environment. Verify `sys.executable`, `python -m pip --version`, and, when installed,
`hepyy config` before dependency changes. Run from the project working directory.
Use the recorded command prefix, or activate and execute in the same shell call;
activation does not persist between independent agent tool calls. For recipes
that invoke `python3` or other tools, activate the venv in that same call or use
conda run so those tools also resolve inside the selected environment.

Reuse this environment by default. Missing imports or commands are reasons to
check interpreter/kernel selection, activation, `hepyy.load()`, and installed
packages first. Add task dependencies here when compatible with the existing
stack. Preserve project pins and the compatible cppyy/ROOT runtime.

Create another environment only when explicitly requested, when concrete
dependency/ABI conflicts require isolation, or when testing a fresh installation
is part of the task. Explain the reason before creation. Registration itself
does not authorize replacing, upgrading, or recreating the environment.

Report the interpreter and validation commands used. Installing packages is not
physics validation. Update the local registration if the environment moves.
'''


def managed_block(original, body):
    """Replace only our block, refusing ambiguous or damaged markers."""
    block = START + '\n' + body.rstrip() + '\n' + END
    if START not in original and END not in original:
        return original + ('\n\n' if original and not original.endswith('\n') else
                           '\n' if original else '') + block + '\n'
    if original.count(START) != 1 or original.count(END) != 1:
        raise ValueError('duplicate or incomplete managed markers')
    start, end = original.index(START), original.index(END)
    if end < start:
        raise ValueError('managed markers are out of order')
    return original[:start] + block + original[end + len(END):]


def inspect_environment(python):
    result = subprocess.run([str(python), '-c', PROBE], capture_output=True,
                            text=True, timeout=30, check=True)
    # Some site startup hooks print diagnostics before the probe result.
    return json.loads(result.stdout.strip().splitlines()[-1])


def parser():
    p = argparse.ArgumentParser(description=__doc__, epilog='Examples:\n'
        '  python scripts/setup-project.py --project . --dry-run\n'
        '  python scripts/setup-project.py --project /path/to/analysis\n'
        '  python scripts/setup-project.py --project . --venv /path/to/.venv\n'
        '  python scripts/setup-project.py --project . --conda-prefix /path/to/env',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--project', required=True, type=Path, help='existing project directory')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--venv', type=Path, help='use this existing venv instead of current Python')
    group.add_argument('--conda-prefix', type=Path, help='use this existing conda prefix')
    p.add_argument('--allow-system', action='store_true', help='explicitly register system Python')
    p.add_argument('--allow-base', action='store_true', help='explicitly register conda base')
    p.add_argument('--dry-run', action='store_true', help='show changes without writing files')
    return p


def main(argv=None):
    p = parser()
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        p.print_help()
        return 0
    args = p.parse_args(argv)
    try:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            raise ValueError('project must be an existing directory')
        prefix = args.venv or args.conda_prefix
        python = prefix.expanduser().absolute() / 'bin/python' if prefix else Path(sys.executable)
        env = inspect_environment(python)
        expected = 'venv' if args.venv else 'conda' if args.conda_prefix else None
        if expected and env['kind'] != expected:
            raise ValueError(f"requested {expected}, but interpreter reports {env['kind']}")
        if env['kind'] == 'system' and not args.allow_system:
            raise ValueError('system Python detected; activate a venv/conda environment or use --allow-system')
        if env['is_conda_base'] and not args.allow_base:
            raise ValueError('conda base detected; select a project environment or use --allow-base')
        command = (['conda', 'run', '--no-capture-output', '-p', env['prefix'], 'python']
                   if env['kind'] == 'conda' else [env['python']])
        config = {'managed_by': 'agent-skills/setup-project', 'schema_version': 1,
                  **env, 'python_command': command,
                  'python_command_shell': shlex.join(command)}
        if env['kind'] == 'venv':
            config['activation_shell'] = 'source ' + shlex.quote(str(Path(env['prefix']) / 'bin/activate'))
        bodies = {
            'AGENTS.md': POLICY,
            'CLAUDE.md': '## Physics environment\n\nFollow the Physics environment section in @AGENTS.md.\n'
                         'Read `.physics-env.local.json` before executing project commands.\n',
            '.gitignore': None,
            CONFIG: None,
        }
        changes = []
        # Prepare and validate every file before writing any of them.
        for name, body in bodies.items():
            path = project / name
            if path.is_symlink():
                raise ValueError(f'refusing to modify symlink: {path}')
            old = path.read_text() if path.exists() else ''
            if name == CONFIG:
                if old and json.loads(old).get('managed_by') != config['managed_by']:
                    raise ValueError(f'{CONFIG} is not managed by this script')
                new = json.dumps(config, indent=2) + '\n'
            elif name == '.gitignore':
                rule = '/' + CONFIG
                new = old if rule in old.splitlines() else old + ('\n' if old and not old.endswith('\n') else '') + rule + '\n'
            else:
                new = managed_block(old, body)
            if old != new:
                changes.append((path, old, new))
        print(f"Environment: {env['kind']} at {env['prefix']}")
        print(f"Python: {env['python']}")
        print('hepyy: ' + ('available (not runtime-tested)' if env['hepyy_available'] else
                          'not installed; registration does not install it'))
        for path, old, new in changes:
            if args.dry_run:
                print(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                      fromfile=str(path), tofile=str(path))), end='')
            else:
                path.write_text(new)
                print(f'Updated {path.name}')
        if not changes:
            print('Already up to date.')
        if args.dry_run:
            print('Dry run: no files changed.')
        print('\nSuggested agent prompt:\nFollow this project\'s agent instructions and use the '
              'hepyy skill. Reuse the registered physics environment. Work on [TASK], validate '
              'within that environment, and report the interpreter and checks used.')
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, IndexError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
