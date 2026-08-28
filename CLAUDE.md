# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope

This repo produces **Manim animations for a master's thesis presentation** on graph theory
(Shannon capacity / confusability graphs / Lovász theta). Animation work happens only in the
top-level `Presentatie_animaties*.py` files. Treat everything else as out of scope unless asked:

- `Niet_presentatie/` — "not presentation": scratch research notebooks and solver scripts for the
  thesis itself (exhaustive search, Lovász theta, lattice packings). Unrelated to the animations.
- `Figuur_*.png` / `Figure_*.png` — static matplotlib figures for the written thesis, not animation output.
- `main.py` — untouched `uv init` stub.

## Environment & commands

Dependencies are managed with **uv** (Python 3.13, `manim>=0.21`). Everything runs through `uv run`.

```bash
uv sync                                             # install into .venv
uv run manim render Presentatie_animaties.py BipartiteToUndirected -pql   # render one scene, 480p15, auto-play
uv run manim render Presentatie_animaties.py -a -qh                       # render all scenes in the file, 1080p60
uv run manim checkhealth                            # verify the manim install (ffmpeg, LaTeX, etc.)
```

Quality flags: `-ql` 480p15 (fast iteration, the default used here), `-qm` 720p30, `-qh` 1080p60.
Rendering **LaTeX (`MathTex`) requires a working LaTeX toolchain** on the machine.

Output goes to `media/videos/<source-file-stem>/<quality>/<SceneName>.mp4`, with per-animation
segments cached under `partial_movie_files/`. `media/` is git-ignored — it is regenerated
output, not the source of truth. Regenerate from the `.py` files.

## Conventions for animation code

- **Every scene assumes a white background**: `config.background_color = WHITE` is set at module
  top level, so all mobjects must pass an explicit dark `color=` (the code uses `BLACK` / `GREY_B`)
  or they render invisible. New scenes in a new file must re-set this config line.
- Scene classes are the unit of work. `BipartiteToUndirected` and `ExtendHatchedSquare` subclass
  `Scene`; `C5ToUmbrella` subclasses `ThreeDScene` and drives the camera with
  `set_camera_orientation` / `move_camera` / `begin_ambient_camera_rotation`.
- Geometry is built from first principles: vertex positions are computed as `np.array` offsets or
  from polar angles (`graph_angles` in degrees → `DEGREES`), edges are `Line`/`Arrow` between those
  positions with a `buff` matching the vertex radius. Keep this style — no `manim.Graph` helper.
- Reveal sequencing uses `LaggedStart(*[Create(x) for x in group])`; shape-to-shape morphs use
  `Transform` / `ReplacementTransform` / `TransformFromCopy` between a source and a
  pre-positioned target mobject.
- `Presentatie_animaties_2.py` currently holds a duplicate of `BipartiteToUndirected`. If you edit
  that scene, confirm with the user which file is canonical rather than syncing both silently.
