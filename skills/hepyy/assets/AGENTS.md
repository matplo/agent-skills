# HENP software environment

Use hepyy for the project's high-energy and nuclear physics packages. It supports the native hepbundle and additional recipe-installed generators, libraries, executables, and Python utilities.

## Environment

Use the environment identified by this project's setup instructions. Before running or installing software, verify its `sys.executable`, `python -m pip --version`, and `hepyy config`. Use that interpreter for scripts, tests, and notebook kernels. Activate and run within the same shell call, use absolute venv executables, or use `conda run -p /absolute/env/path ...`; activation in a previous tool call is insufficient.

Preserve conda/ROOT's compatible cppyy runtime. For such environments, install `hepyy[hepbundle]` without `[cppyy]`. For a fresh supported Linux venv without cppyy, use `hepyy[cppyy,hepbundle]`. Reuse the established environment before creating or rebuilding one.

## Package selection

Use `hepyy avail` and `hepyy recipe list-sources` to discover packages, and inspect the relevant recipe before `hepyy install PACKAGE --verbose`. The recipe collection includes HENP tools beyond FastJet/Pythia, such as Herwig, Sherpa, POWHEG, JEWEL, DPMJET, STARlight, ROOT, and RooUnfold; verify current availability and platform prerequisites. A recipe name does not imply a Python import name.

`hepyy list` describes source registry installs; check pip metadata and runtime loading for native wheels. Avoid duplicate source installs over a working wheel bundle. For source Pythia with optional interfaces, install FastJet, HepMC3, and LHAPDF before Pythia. Keep configured package stores and shared-store settings intact.

## Python and notebooks

Initialize in every Python process/kernel before importing native proxy modules:

```python
import hepyy
hepyy.load(["fastjet", "pythia8"])
import cppyy
import fastjet
import pythia8
```

Use `hepyy.load("hepbundle")` when all bundle packages are needed. ROOT is separate; initialize ROOT first for PyROOT workflows. For ROOT-format output alone, the upstream uproot demo avoids requiring PyROOT.

Use `cppyy.gbl.std.vector[fastjet.PseudoJet]` for FastJet inputs. Retain the ClusterSequence while accessing constituents/history and retain fjcontrib axes/measure objects while calculators use them. Check Pythia initialization and failed events; preserve physics selections and use small seeded smoke runs before production.

Use the matching notebook kernel, verify its interpreter, and rerun initialization after restart. Refresh kernel settings with `hepyy kernel update` after package changes, specifying the kernel name when custom.

## Examples and validation

Follow [upstream demos](https://github.com/matplo/hepyy/tree/main/demos) for FastJet, Pythia, fjcontrib, and ROOT examples. `heyy demos` downloads them separately from pip; inspect local edits before `--overwrite`. Plotting and ROOT-output demos may need additional Python dependencies and write files in the current directory.

Validate the required API or executable in the selected environment. Diagnose missing proxies through load order and interpreter selection before reinstalling. For native failures inspect runtime compatibility, selected source packages, and build logs. Report what actually ran and any remaining limitations.
