# AiBianDao Project Guidance

## Purpose

Build and continuously improve a Seedance 2.0-centered AI video directing and shot-compilation system.

## Current Product Boundary

- All video outputs in this system are generated with Seedance 2.0. This is an AI video generation workflow, not a live-action filming workflow.
- Do not plan real-world filming, camera crews, physical locations, actors, props, or on-set production unless the user explicitly changes the project scope in the future.
- Terms such as camera, lighting, performance, blocking, and production refer to instructions simulated by Seedance 2.0 and supporting AI asset generation, not instructions for a physical film crew.
- The currently supported production capability is: simple user script -> logic review and explicit lock -> complete director script -> independent Seedance 2.0 shot tasks.
- Every production shot must be independently copyable into Seedance 2.0 and include references, keyframe requirements, action timeline, audio, continuity, acceptance criteria, and fallback.
- Asset generation, browser operation, editing, publishing, and automatic data learning are future extensions, not current guarantees.

## Working Rules

- Read `从这里开始.md` and `00-系统总控/总索引.md` before broad project work.
- Keep each task scoped. Do not load all full case analyses by default.
- Keep a video's working files only in `06-视频制作项目/<项目编号-名称>/`.
- Global libraries contain reusable knowledge and templates, not duplicate working copies.
- Do not approve training knowledge until the user explicitly confirms satisfaction.
- Separate positive examples, unverified ideas, and failure lessons.
- Preserve portrait, music, font, product, and platform compliance boundaries.
- Distinguish creative requests from production requests before drafting. If the user asks for a topic, concept, product story, campaign story, reference adaptation, "write a video script", or otherwise wants the system to create the core idea, treat it as a script creative task and provide distinct candidate directions first. Only skip multi-direction ideation when the user has already supplied a concrete script/storyline and is asking for logic review, polishing, storyboard, or Seedance production.
- For script creative tasks, add a G0 viral-direction gate before any full script: each candidate must state the first 3-8 second hook, why users keep watching, the emotional ladder, the relationship cost, the ending callback, concise thought-provoking dialogue potential, and Seedance production risk. Do not draft the full script until the user locks one direction.
- Before a full script for Douyin-style emotional, prompt, reference-hit, answer/list, product story, family/friendship/regret, or life-philosophy shorts, test at least three first-8-second openings when useful: cognitive mismatch, light-question-heavy-answer, and abnormal-action/relationship-suspense. Pick or recommend the strongest opening before continuing.
- Important character dialogue must be concise, relationship-bound, and thought-provoking. Each key line should imply a life philosophy through who says it, who it is really said to, what remains unsaid, and what visible cost it carries. Do not let characters directly explain the philosophy in abstract slogans.
- For every script creative task, follow the standard creative-to-shot chain before Seedance compilation: clarify platform/rules/reference inputs, extract learnable structure and must-not-copy elements, generate distinct candidate directions, wait for the user to lock one direction, run logic review with A/B/C/D/E confirmation, deepen weak segments through visual objects/actions instead of abstract explanation, then compile the locked script into storyboard and Seedance 2.0 shot tasks.
- For emotional shorts, prompt-based shorts, reference-hit adaptations, list/group-answer formats, and family/friendship/regret themes, enforce the "retention-progression-story-callback" narrative gate before storyboard: first 3-8 seconds must create retention, the middle must escalate rather than list, each segment must have a visible story unit, and the ending must callback a concrete opening action/object/line/relationship. If this gate fails, return to script development instead of compiling shots.
- For interview, group-answer, list-answer, or prompt-answer scripts, require a speaking-relationship table before drafting the final script: character identity -> speaking target -> absent relationship -> cost of the unsaid -> visual anchor -> implied life philosophy. Do not let characters speak only to the audience as portable maxims.
- When the user provides a simple script and requests production-ready Seedance 2.0 shots, use `compile-seedance2-shots` as the primary workflow.
- If that script has not been logic-reviewed and explicitly locked, run `refine-video-script-logic` first and wait for the user's A/B/C/D/E decision.
- Keep confirmed source facts, compiler assumptions, and optional rewrites visibly separate.
- When creating or modifying storyboard/video shot scripts, always include clear time context and logic guidance inside each copyable video prompt code block, including the suggested total generation duration and a numeric second-by-second action timeline; do not place timing only in surrounding notes. Synchronize every affected project file, numbering reference, task count, fallback reference, asset/record/status entry, or explicitly state why a related file was not changed.
- Test character identity, the hardest action, and product/text fidelity before bulk generation.
- Record failed generations and single-variable retries; do not learn only from successful reference videos.
- Treat every reference-video submission as beginner mode by default: proactively identify what is worth learning, what needs caution, what is not worth learning, and what must not be copied, even when the user provides no technical preferences.
- Automate analysis, comparison, recommendation, and candidate refinement, but require explicit user approval before promoting any positive conclusion into the formal training library.
- Detect repeated or increasingly standardized work during normal tasks. When a workflow has appeared at least twice, or already has stable inputs, outputs, steps, and acceptance criteria, tell the user whether it should remain a rule/template, extend an existing Skill, or become a new Skill; require user approval before creating a new Skill.
- Prefer updating an existing Skill or adding a rule/template over creating a narrowly scoped Skill. Do not create a Skill whose main purpose is only to decide whether another Skill should exist.

## Human Gates

Require explicit approval for G0 viral direction selection, story/director assumptions, storyboard and key appearance, high-risk Seedance tests and task pack, rough cut, and pre-publication compliance.
- At every human gate or phase transition, explicitly tell the user what the next operation should be, what confirmation is needed, and what will happen after confirmation. Do this even when the current deliverable is already complete, so the user is never left guessing whether to confirm, test, revise, or proceed.

## Versioning

- New production project ID: `ABD-PROD-YYYY-NNN-short-name`.
- New reference-analysis ID: `ABD-REF-YYYY-NNN-short-name`.
- Training cards keep their typed IDs, such as `ABD-CASE`, `ABD-STRUCT`, `ABD-HOOK`, and `ABD-RISK`.
- Existing `ABD-2026-NNN-*-reference` folders are legacy-compatible and do not need renaming.
- File: `name_v01_status.ext`.
- Never use names such as `final2`, `latest-final`, or `newest`.
