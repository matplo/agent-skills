# Environment setup and execution

These commands describe setup when needed; do not reinstall an already working environment merely to use the skill. Examples use `.venv` or `hepbundle`; honor the project's actual location/name.

## Linux venv with native wheels

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'hepyy[cppyy,hepbundle]>=0.2.31'
python -c 'import hepyy; hepyy.load("fastjet"); import fastjet; print(fastjet.fastjet_version_string())'
```

The inspected wheel matrix covers Linux x86_64 and macOS arm64/Intel with CPython 3.10+. For macOS, upstream recommends conda-forge cppyy. Windows and Linux arm64 are not covered by this matrix. A compatible C++ toolchain is still needed by cppyy's JIT; native HEP wheels avoid compiling the five HEP packages themselves.

In later agent calls, use `/absolute/project/.venv/bin/python` and `/absolute/project/.venv/bin/hepyy`, or activate and execute in the same call. Check that `python3` also resolves into the environment when running recipes that invoke it.

## Conda / mamba

```bash
conda create -n hepbundle -c conda-forge python=3.12 cppyy pip
conda activate hepbundle
python -m pip install 'hepyy[hepbundle]>=0.2.31'
```

For an existing compatible conda/ROOT runtime, omit `[cppyy]` to retain the matched runtime. For a path-based environment use `conda create --prefix /absolute/path ...` and `conda activate /absolute/path`.

For noninteractive execution without relying on previous activation:

```bash
conda run --no-capture-output -n hepbundle python analysis.py
conda run --no-capture-output -p /absolute/env/path hepyy config
```

If activation is required in bash, initialize the shell hook in that same invocation before activating. Do not modify global conda solver/channel settings for this pip-inside-conda workflow.

## The user's setup-hepbundle.sh pattern

The inspected [setup script](https://github.com/matplo/utils/blob/main/sh/setup-hepbundle.sh) creates a conda environment, activates it within the script, and ends with:

```bash
python -m pip install 'hepyy[hepbundle]'
hepyy install hepyy-utils --verbose
hepyy install hepyy-pipmisc --verbose
```

Its invocation modes are `setup-hepbundle.sh NAME` for `./NAME`, `--global NAME` for a named conda environment, and `--prefix PATH` (or `-p PATH`) for an explicit prefix. It refuses an existing target. Executing it as a child process does not activate the resulting environment in the parent shell; activate explicitly afterward or use `conda run`.

The last two commands are additional recipes, not pip extras or necessary prerequisites for every core demo:

- [hepyy-utils recipe](https://github.com/matplo/hepyy-recipes/blob/main/hepyy-utils/main.sh) installs `hepyy_utils` from GitHub into a recipe prefix and creates JEWEL helper wrappers. Use its generated environment/module setup when exposing that prefix's Python module and executables; do not assume ordinary site-packages installation.
- [hepyy-pipmisc recipe](https://github.com/matplo/hepyy-recipes/blob/main/hepyy-pipmisc/main.sh) installs a broader Python tool collection into the executing environment, including hepyy-workflows, notebook/plotting packages, and scipaperlib. Inspect the current recipe before assuming its contents.

To reproduce that setup, include both commands. For a narrower task, install only the required extras. Recipe payloads can change on main.

## Package stores and shell modules

Verify effective settings with `hepyy config`. The source-store defaults from [config.py](https://github.com/matplo/hepyy/blob/main/src/hepyy/config.py) are:

| Interpreter environment | Default source package store |
| --- | --- |
| venv | `sys.prefix/hepyy_packages` |
| conda without a nested venv | `sys.prefix/share/hepyy_packages` |
| neither | `./packages` |

Override precedence is `HEPYY_PACKAGES_DIR`, legacy `HEPYY_BUILD_DIR`, `.hepyy.toml` `packages_dir`, legacy TOML `build_dir`, then the defaults. The TOML file is read from the current working directory, not searched upward. Relative paths therefore depend on that directory. Pip-native wheels live in the Python environment and do not create source registry entries.

`HEPYY_SYSTEM_PACKAGES_DIR` supplies read-only shared source stores (colon-separated paths); `.hepyy.toml` `system_packages_dir` is the fallback. Keep personal installs in the writable local store. Shared binaries must match the platform/runtime.

For packages requiring shell-provided PATH/PYTHONPATH or library settings, use the supported module setup in the same shell as the command:

```bash
eval "$(hepyy shell-init)"
module load hepyy-utils
python -c 'import hepyy_utils; print(hepyy_utils.__file__)'
```

Inspect installed CLI help and generated module names if this differs on an older version. Explicit `hepyy.load(...)` remains appropriate in scripts using native proxies. `henv` is an optional wrapper; if the project uses it, inspect its help and existing project invocation rather than substituting a new environment or assuming an interactive subshell persists between tool calls.

## Jupyter

Register from the chosen environment:

```bash
python -m pip install ipykernel
hepyy kernel install --name hep-analysis --display-name 'HEP analysis'
```

Use a project-specific kernel name to avoid collisions. Select it in Jupyter and check `sys.executable` inside the notebook. Run the explicit native load cell after each restart. After changing packages or paths, refresh with `hepyy kernel update hep-analysis` and restart the kernel. For notebook execution, explicitly select this kernel; starting nbconvert from the right shell alone does not override another kernel named in notebook metadata.

Install optional Python dependencies according to the selected demo. A notebook front end may run elsewhere; the kernel process must use the intended physics environment.
