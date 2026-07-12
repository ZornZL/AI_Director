# AiBianDao Project Guidance

## Purpose

Build a beginner-friendly AI directing system that turns a user theme or competition brief into reviewed creative directions, a locked script, and independently executable Seedance 2.0 shot tasks.

## Stable Product Boundary

- All video shots are generated with Seedance 2.0; camera, lighting, performance, blocking, sound, and production language are AI-generation controls, not live-action instructions.
- The stable chain is: theme/rules -> 3 creative directions -> user locks one -> complete script -> logic review and A/B/C/D/E lock -> platform/aspect/duration confirmation -> director shots -> assets/keyframes -> independent 4-15 second Seedance tasks.
- Each Seedance task must state references, duration, time context, one primary shot intention, numeric action timeline, dialogue/audio whitelist, continuity, acceptance criteria, and fallback.
- Do not promise one-pass success, automatic browser generation, automatic editing, publishing, or data learning.
- The only validated full production case is `06-视频制作项目/ABD-PROD-2026-002-houlai-mama/`.

## Working Rules

- Read `从这里开始.md` and `00-系统总控/总索引.md` before broad project work.
- Creative request: use `create-video-concept`, provide three genuinely different directions, recommend one, and wait for the user's choice before writing the complete script.
- Concrete user script: use `refine-video-script-logic`; do not enter production until the user chooses A/B/C/D.
- Locked script: use `compile-seedance2-shots`.
- Keep confirmed source facts, compiler assumptions, and optional rewrites separate.
- Do not default platform, aspect ratio, duration, or current Seedance interface parameters when the user has not confirmed them.
- Storyboard preview is optional, not a proven mandatory gate. Recommend it for long, multi-scene, continuity-heavy work; it never replaces production assets or keyframes.
- Test character identity, the hardest action, and product/text fidelity before bulk generation.
- Record failed generations and retry one variable at a time.
- Promote new positive training knowledge only after explicit user approval and real production evidence.
- Preserve portrait, music, font, product, platform, competition, and copyright compliance boundaries.

## Human Gates

Require explicit approval for: creative direction, locked script, platform/aspect/duration, core appearance/assets, high-risk test/task pack, rough cut, and pre-publication compliance. At every gate, state what the user must confirm and what happens next.

## Versioning

- Production project: `ABD-PROD-YYYY-NNN-short-name`.
- File: `name_v01_status.ext`.
- Never use `final2`, `latest-final`, `newest`, or `副本`.
