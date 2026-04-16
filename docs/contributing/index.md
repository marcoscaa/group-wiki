# Contributing to the Wiki

This page explains how to add or edit tutorials so that the wiki stays up to date.

---

## How the wiki works

The wiki is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).
You write plain **Markdown** files inside the `docs/` folder, and MkDocs converts them into the website.
The source lives on GitHub (`marcoscaa/group-wiki`) and the live site is served via GitHub Pages.

```
group-wiki/
├── mkdocs.yml        ← site config: theme, navigation, extensions
└── docs/
    ├── index.md      ← home page
    ├── installation/
    ├── lammps/
    ├── qe/
    ├── vasp/
    ├── python/
    ├── hpc/
    └── contributing/ ← you are here
```

---

## Setup (first time only)

```bash
# 1. Clone the repository
git clone git@github.com:marcoscaa/group-wiki.git
cd group-wiki

# 2. Install MkDocs Material
pip install mkdocs-material

# 3. Preview the site locally
python3 -m mkdocs serve
# Open http://127.0.0.1:8000 in your browser
```

The local preview auto-reloads every time you save a file — no need to restart.

---

## Adding or editing a page

### Edit an existing page

Open any `.md` file under `docs/` in your text editor and make your changes.
The file path mirrors the URL: `docs/lammps/input_file.md` → `.../lammps/input_file/`.

### Add a new page

1. Create a new `.md` file in the appropriate subfolder:
   ```
   docs/lammps/thermostats.md
   ```

2. Register it in `mkdocs.yml` under the `nav:` section:
   ```yaml
   nav:
     - LAMMPS:
       - Overview: lammps/index.md
       - Input File Structure: lammps/input_file.md
       - Thermostats: lammps/thermostats.md   # ← add this line
   ```

### Add a new section

1. Create a new subfolder and an `index.md` inside it:
   ```
   docs/new_topic/index.md
   ```

2. Add the section to `mkdocs.yml`:
   ```yaml
   nav:
     - New Topic:
       - Overview: new_topic/index.md
   ```

---

## Markdown reference

All pages are written in standard Markdown with a few useful extensions enabled.

### Headings

```markdown
# Page title (H1 — one per page)
## Major section (H2)
### Subsection (H3)
```

### Code blocks

Specify the language for syntax highlighting:

````markdown
```bash
module load python/3.10.8
source venv/bin/activate
```

```python
import numpy as np
a = np.array([1, 2, 3])
```

```fortran
&SYSTEM
  nat = 2
  ecutwfc = 60.0
/
```

```lammps
units    metal
pair_style mace no_domain_decomposition
run      10000
```
````

### Admonitions (callout boxes)

```markdown
!!! tip "Optional title"
    Use this for helpful hints.

!!! note
    Use this for extra context or reminders.

!!! warning
    Use this for common pitfalls or important caveats.
```

Renders as:

!!! tip "Optional title"
    Use this for helpful hints.

!!! warning
    Use this for common pitfalls or important caveats.

### Tabbed content

Useful for showing the same steps on different machines or systems:

```markdown
=== "Tuolumne (LLNL)"
    ```bash
    module load rocm/6.2.4hangfix
    ```

=== "Another cluster"
    ```bash
    module load cuda/12.0
    ```
```

### Tables

```markdown
| Column A | Column B | Column C |
|---|---|---|
| value 1  | value 2  | value 3  |
```

### Links

```markdown
[link text](other_page.md)          # internal link
[link text](../lammps/index.md)     # link to another section
[LAMMPS website](https://lammps.org) # external link
```

---

## Publishing your changes

Once you are happy with the edits:

```bash
# 1. Stage and commit the source files
git add docs/ mkdocs.yml
git commit -m "Brief description of what you added or changed"
git push

# 2. Deploy the live site to GitHub Pages
python3 -m mkdocs gh-deploy
```

The live site updates within about a minute after `gh-deploy`.

!!! warning "Never commit the `site/` folder manually"
    The `site/` folder is generated automatically by `gh-deploy`.
    Do not `git add site/` — it is managed separately on the `gh-pages` branch.

---

## Workflow summary

```
edit docs/*.md
      ↓
python3 -m mkdocs serve   (preview at localhost:8000)
      ↓
git add + git commit + git push   (save source to GitHub)
      ↓
python3 -m mkdocs gh-deploy       (publish to live site)
```
