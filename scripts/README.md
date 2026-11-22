# Register a project's physics environment

`setup-project.py` tells coding agents which **existing** environment to use and
adds a persistent reuse policy to the project. It uses the Python standard library
(Python 3.9+) and targets Linux/macOS shells and environment layouts. It does not
create an environment, install packages, install agent skills, or run physics code.

## Normal use: activate, then register

Install the hepyy skill for your agent once using the [repository instructions](../README.md).
Then register an environment once per project checkout. Run the script with the
environment's `python`, not a system Python or a launcher that selects a different interpreter.

### Existing conda environment

```bash
conda activate /path/to/hep-env
cd /path/to/analysis
python /path/to/agent-skills/scripts/setup-project.py --project . --dry-run
python /path/to/agent-skills/scripts/setup-project.py --project .
```

An environment name works with `conda activate` too. The script records its resolved
prefix so agents do not have to guess which environment name to use.

### Existing Python venv

```bash
source /path/to/.venv/bin/activate
cd /path/to/analysis
python /path/to/agent-skills/scripts/setup-project.py --project .
```

No `--venv` or `--conda-prefix` is needed in either case. Detection uses the running
interpreter's `sys.prefix` and `sys.base_prefix`, with conda metadata as an additional
signal. A venv takes precedence over inherited conda activation variables.

### Select an environment without activation

Explicit overrides are useful for registering an environment from another shell:

```bash
python3 /path/to/agent-skills/scripts/setup-project.py \
  --project /path/to/analysis --conda-prefix /path/to/hep-env

python3 /path/to/agent-skills/scripts/setup-project.py \
  --project /path/to/analysis --venv /path/to/.venv
```

The script probes that environment's `bin/python` and verifies its type. Only one
override may be supplied. Conda execution instructions assume `conda` is available
to the agent; otherwise initialize conda in its shell before running those commands.

System Python and detected conda base environments are rejected by default. If
deliberately required, use `--allow-system` or `--allow-base`, respectively. These
flags only permit registration; they do not install anything. Conda base detection
uses `condabin/` and active-base metadata; inspect the reported prefix on unusual
conda installations. Missing hepyy is reported but does not prevent registration.

## Create or choose an environment first, when needed

Keep these operations separate from project registration. Existing utilities:

- [setup-hepbundle.sh](https://github.com/matplo/utils/blob/main/sh/setup-hepbundle.sh)
  creates a **conda** environment, installs conda-forge cppyy, the pip hepbundle,
  and the `hepyy-utils` / `hepyy-pipmisc` recipes. It refuses an existing target.
- [conda-pick.py](https://github.com/matplo/utils/blob/main/python/conda-pick.py)
  provides an interactive terminal picker for environments listed in
  `~/.conda/environments.txt` and opens a shell with the selected environment
  activated. It selects existing conda environments; it does not create venvs.
  Run registration inside the selected shell. This curses interface is for a human
  terminal; agents should use a known prefix and noninteractive commands.

After obtaining the utilities, for example in an existing `matplo/utils` checkout:

```bash
bash /path/to/utils/sh/setup-hepbundle.sh --prefix /path/to/new-hep-env
conda activate /path/to/new-hep-env
python /path/to/agent-skills/scripts/setup-project.py --project /path/to/analysis
```

The creation script's activation occurs inside its own process, so activate the
new environment explicitly afterward. Other creation modes are `NAME` (creates
`./NAME`) and `--global NAME` (creates a named conda environment).

Alternatively choose an existing environment:

```bash
python3 /path/to/utils/python/conda-pick.py
# In the shell opened by the picker:
python /path/to/agent-skills/scripts/setup-project.py --project /path/to/analysis
```

For a fresh Python venv, use the normal `python3 -m venv` workflow and the
[hepyy environment guidance](../skills/hepyy/references/environments.md) for the
appropriate platform/runtime installation. This repository does not duplicate
the environment-creation tools.

## Files created or updated

| File in the target project | Purpose | Commit? |
| --- | --- | --- |
| `.physics-env.local.json` | Environment type, absolute prefix/interpreter, shell commands, and hepyy availability at registration time | No; machine-specific |
| `AGENTS.md` | Managed Physics environment section: read local config, reuse environment, preserve runtime, validate work | Yes |
| `CLAUDE.md` | Managed section referring to `AGENTS.md` with Claude's `@AGENTS.md` import syntax | Yes |
| `.gitignore` | Adds `/.physics-env.local.json` | Yes |

The shared instructions contain no machine-specific paths. Each collaborator
registers their own environment in their checkout. Git ignore rules do not untrack
an already tracked file: if local configuration was previously committed, review
and remove it from tracking separately.

Existing instruction text outside the marked sections is preserved. Repeating
registration updates the same sections and local configuration without duplicates.
Review any existing instructions that contradict the new policy. Keep custom
instructions outside the generated markers because their contents are regenerated.
The script refuses symlinked target files, malformed/duplicate markers, and local
configuration not owned by this tool. It validates all proposed contents before
writing; filesystem write failures can still leave partial updates, so review
reported errors and rerun after resolving them.

`--dry-run` probes the interpreter and prints proposed diffs without writing files.
It still starts the selected Python process (including its normal startup hooks).
No dependencies are installed or imported to test their native runtime: hepyy is
checked for discoverability only. No package lists, secrets, or environment-variable
dumps are saved.

## First prompt and subsequent use

The script prints this prompt after registration:

> Follow this project's agent instructions and use the hepyy skill. Reuse the
> registered physics environment. Work on [TASK], validate within that environment,
> and report the interpreter and checks used.

Replace `[TASK]` with the actual request. Subsequently, ordinary task prompts
should suffice when the agent loads the project's instructions. The generated
policy permits another environment only when requested, when a concrete
dependency/ABI conflict requires isolation, or when a fresh-install test is the
task. Agents must explain that reason before creating one.

Rerun registration after moving or switching environments. If the configured
interpreter disappears, instructions tell agents to resolve the environment choice
instead of silently creating a replacement.

## Help and validation

```bash
python3 scripts/setup-project.py --help
python3 scripts/setup-project.py
python3 -m unittest discover -s tests -v
```

Run these from the `agent-skills` checkout. No arguments prints help and examples
without modifying files. Tests use temporary projects and a small standard-library
venv; they do not install hepyy or conda or execute physics examples.
