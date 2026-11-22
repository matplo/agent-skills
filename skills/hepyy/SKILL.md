---
name: hepyy
description: Set up, use, and troubleshoot hepyy-managed HENP physics software in venv or conda environments, including native bundles, additional package recipes, cppyy analyses, and Jupyter demos.
---

# hepyy for HENP work

Use hepyy as an extensible package manager for high-energy and nuclear physics (HENP). The FastJet/Pythia hepbundle is one convenient starting point; recipes also install generators, analysis libraries, executables, and Python utilities. Do not assume every installed package exposes a cppyy module.

## Select the execution environment first

- Reuse the environment specified by the user or project. Inspect project setup instructions, `.hepyy.toml`, interpreter paths, and existing activation scripts before creating another environment.
- Verify `sys.executable`, `sys.prefix`, `python -m pip --version`, and `hepyy config` in that environment. `hepyy`, `heyy`, and `her` are equivalent CLI entry points.
- Shell activation does not persist between separate agent tool calls. Activate and run in the same shell invocation, use the venv's absolute executable paths, or use `conda run --no-capture-output -p /absolute/env/path ...` (or `-n NAME`). Preserve required environment variables and the project working directory.
- Use `python -m pip` from the chosen interpreter. Keep a working conda/ROOT cppyy runtime intact: omit the `[cppyy]` extra when that runtime already provides cppyy.
- For setup, package locations, the user's setup-script pattern, and kernels, read [references/environments.md](references/environments.md).

## Discover and install the packages the task actually needs

Inspect `hepyy config`, `hepyy list`, `hepyy avail`, and `hepyy recipe list-sources`. The installed CLI's `--help` is authoritative for version-specific options. `list` describes source registry installations; an empty listing does not establish that pip-native wheels are absent. Check pip metadata and an actual load as well.

`hepyy init` initializes the store and registers the standard [recipe collection](https://github.com/matplo/hepyy-recipes). It may also repair cppyy library references; it is a setup action, not a read-only diagnostic. Refresh recipes with `hepyy recipe update` when the task requires newer or missing recipes.

The inspected collection includes `herwig`, `sherpa`, `powheg`, `jewel`, `dpmjet`, `starlight`, `root`, `roounfold`, `boost`, `gsl`, `hepyy-utils`, and `hepyy-pipmisc`, in addition to the core bundle. Discover current names and versions rather than treating this list as exhaustive or guaranteeing support on every platform.

Before installing an additional package, inspect its recipe and upstream usage instructions for dependencies, compiler requirements (including Fortran where relevant), download/data requirements, supported platforms, and whether it supplies libraries, executables, or Python modules. Then use `hepyy install PACKAGE --verbose` in the selected environment and validate the interface the task needs. Do not invent `import PACKAGE` from a recipe name.

For additional recipe sources or local recipes:

```bash
hepyy recipe add https://github.com/OWNER/RECIPE-REPOSITORY
hepyy install PACKAGE --recipe /absolute/path/to/recipe.yaml
```

These are templates: replace the repository, package, and path with inspected values. For an existing external build, use `hepyy register PACKAGE --prefix /absolute/install/prefix` rather than rebuilding by default.

For a source-built core stack with Pythia's optional interfaces, install in this order:

```bash
hepyy install fastjet hepmc3 lhapdf pythia8 fjcontrib --verbose
```

The optional Pythia interfaces depend on what is present at configure time. Installing a dependency afterward does not retrofit an existing Pythia build. The native pip bundle already includes these interfaces. Avoid adding duplicate source builds to a working wheel stack: selected source/shell packages take precedence and may conflict with wheel dependencies. Rebuild only when the requested configuration needs it.

## Initialize native libraries in each Python process

```python
import hepyy
hepyy.load(["fastjet", "pythia8"])
import cppyy
import fastjet
import pythia8
```

Use `hepyy.load("hepbundle")` for the complete installed bundle, or load only the required packages. Installing native wheels supplies libraries and headers; loading creates the Python proxies. Repeat the load cell after a kernel restart. Explicit load calls are safe when shell hooks already initialized the packages. The bundle's upstream `lhapdf` module is directly importable; PDF sets remain separate data, e.g. `lhapdf install CT14lo`, with `LHAPDF_DATA_PATH` for custom locations.

When using PyROOT, initialize ROOT before FastJet/Pythia/cppyy work. Use importable ROOT from the chosen environment; if ROOT is managed only by hepyy, expose it with `hepyy.load("root")` first. ROOT is not part of the pip hepbundle. Follow the ROOT demo's initialization sequence and keep all libraries on the same compatible runtime.

## Follow the demos' binding conventions

- Use `cppyy.gbl.std.vector[fastjet.PseudoJet]` and `push_back` for clustering inputs. This is the C++ API exposed through cppyy; do not substitute unrelated Python FastJet/Awkward APIs.
- Keep the `ClusterSequence` alive while using its jets' constituents, clustering history, or substructure. Extract persistent Python values before discarding an event's C++ owners.
- Keep Nsubjettiness axes and measure objects in named variables that outlive the calculators; avoid temporary constructor arguments for those borrowed references.
- For Pythia, check initialization success, skip failed `next()` calls, and distinguish attempted from generated events. Choose final-state, visible, charged, and acceptance selections deliberately for the physics task. Preserve the requested process and cuts when adapting a demo.
- Use a fixed seed and a small event count for reproducible smoke checks before long runs. Check denominator and empty-collection cases in observables.

## Pick the relevant upstream example

The [demos directory](https://github.com/matplo/hepyy/tree/main/demos) and [demo prerequisites](https://github.com/matplo/hepyy/blob/main/demos/README.md) are the starting points:

| Example | Use |
| --- | --- |
| `demo_fastjet.py` | C++ vector inputs, clustering, constituents |
| `demo_pythia_fastjet.py` / `.ipynb` | Event generation and jet finding |
| `demo_fjcontrib.py` / `.ipynb` | SoftDrop, Nsubjettiness, energy correlators; needs numpy/matplotlib |
| `demo_softdrop_splitting.ipynb` | Groomed splitting observables |
| `demo_pythia_fastjet_root.py` | ROOT-format output with uproot/numpy; no PyROOT required |
| `demo_pythia_fastjet_root_cppyy.py` | PyROOT TTree output and ROOT-first initialization |
| `demo_pythia_fastjet_root.ipynb` | Notebook with additional ROOT requirement |

`heyy demos` downloads to `./hepyy_demos/` from GitHub main. It preserves existing files; pip upgrades do not refresh downloaded demos. Inspect local modifications before choosing `heyy demos --overwrite`. For reproducibility, record the upstream commit or retain the exact scripts used. Run demos from a writable output directory; some create images or ROOT files.

## Validate and diagnose

First test imports and a tiny actual operation in a fresh process using the intended interpreter. For FastJet, create two PseudoJets, cluster them, and inspect constituents while retaining the sequence. For another recipe, test its documented executable or API. Report the interpreter, relevant versions, command, and outcome; do not call installation success physics validation.

- Missing `fastjet`/`pythia8`: check load-before-import and interpreter/kernel selection before installing anything else.
- Missing recipe package: inspect sources and availability; distinguish a missing recipe from an unsupported build.
- Native symbol, header, or library errors: inspect the selected runtime, source registry, shell-selected packages, and pip distributions before changing library paths. `hepyy fix-cppyy --check` is the inspection command.
- Source build failure: inspect the package store's `logs/`, recipe, dependencies, and compiler. Avoid reflexive `--force`, upgrades, or another cppyy installation.
- Notebook-only failure: inspect `sys.executable` in the notebook, refresh the appropriate kernel spec, restart, and rerun initialization.

Guidance inspected against upstream main on 2026-11-21. Recheck current metadata for versions and platform support. Primary references: [hepyy README](https://github.com/matplo/hepyy/blob/main/README.md), [native wheels](https://github.com/matplo/hepyy/blob/main/NATIVE_WHEELS.md), [recipes](https://github.com/matplo/hepyy-recipes), and [workflow examples](https://github.com/matplo/hepyy/blob/main/WORKFLOW-EXAMPLE.md).

For a repository-local alternative, adapt [assets/AGENTS.md](assets/AGENTS.md) into the project's existing agent instructions and supply its actual environment path.
