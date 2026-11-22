# Agent skills for physics work

Reusable instructions for coding agents working on high-energy and nuclear physics (HENP), scientific software, and analysis environments. Skills use Markdown with standard `name` and `description` metadata and keep supporting references alongside the entry point.

## Available skills

| Skill | Purpose |
| --- | --- |
| [hepyy](skills/hepyy/SKILL.md) | Use hepyy in venv/conda environments, discover HENP package recipes, initialize cppyy libraries, and work with analysis demos and Jupyter kernels. |

The hepyy skill includes [environment guidance](skills/hepyy/references/environments.md) and a [project AGENTS.md example](skills/hepyy/assets/AGENTS.md). There is no separate top-level templates directory.

## Register your project's existing environment

After installing the skill below, activate the conda environment or venv you want
agents to reuse, then run:

```bash
python /path/to/agent-skills/scripts/setup-project.py --project /path/to/analysis
```

The script detects the running interpreter, saves machine-local environment
configuration, and adds shared instructions to `AGENTS.md` and `CLAUDE.md`.
It creates no environments and installs no dependencies. Add `--dry-run` to preview
changes, or use `--help` for syntax.

See **[scripts/README.md](scripts/README.md)** for copy-paste conda/venv examples,
the existing environment creation and picker tools, generated files, and the first
agent prompt.

## Use with Codex or Claude Code

Clone this repository to a stable location:

```bash
git clone https://github.com/matplo/agent-skills.git
cd agent-skills
```

Copy the complete skill folder into your agent's skill directory. The following commands assume the destination skill does not already exist; inspect an existing installation before replacing it.

For Codex:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/hepyy "${CODEX_HOME:-$HOME/.codex}/skills/hepyy"
```

For Claude Code:

```bash
mkdir -p "$HOME/.claude/skills"
cp -R skills/hepyy "$HOME/.claude/skills/hepyy"
```

For project-local Claude Code use, place the folder under `.claude/skills/hepyy/` instead. Reload or start a new agent session if discovery has not refreshed. Invoke as `$hepyy` in Codex or `/hepyy` in Claude Code, or ask a relevant hepyy question for automatic selection where supported.

Keep the full folder structure: the skill uses relative links into `references/` and `assets/`. A copy is a snapshot; updating this repository does not update installed copies. For local development, a directory symlink to the checkout can keep a single source of truth where the agent supports it. Do not overwrite an existing skill installation without checking its changes.

## Use with chat applications

For Claude's custom skill uploader, package the complete `skills/hepyy/` folder according to the uploader's current requirements. For a ChatGPT Project, upload `SKILL.md` and `references/environments.md` and instruct the project to consult those files for hepyy/HENP tasks. Explicitly name the uploaded reference file because a chat upload may not preserve relative paths.

These files provide guidance. Running the examples requires a compatible execution environment with access to the relevant software and data; uploading a skill does not grant access to your local conda environment.

## Maintain skills

- Edit the repository copy, then update installations from it. Keep provider-specific configuration outside the shared instructions unless needed.
- Put project-specific environment names, commands, and data locations in that project's agent instructions. Adapt the bundled AGENTS.md example rather than using machine-specific paths in the shared skill.
- Keep references concise, cite upstream sources, and record when version-sensitive guidance was inspected.
- Before committing, validate skill metadata, check relative links and example syntax, and run `git diff --check`. State separately whether any native runtime examples were executed.
- Pin a commit or release tag when using the skill in a reproducible course or analysis. A skill's documentation date is not a software dependency lock.

The initial hepyy skill was checked with Codex's skill-creator validator. Its physics runtime examples have not been executed as part of this repository's initial publication.

## License

[MIT](LICENSE). Linked upstream software and documentation retain their own licenses.
