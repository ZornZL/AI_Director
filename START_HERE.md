# START_HERE

This file is the GitHub-friendly entry point for the AI_Director repository.

For the full Chinese operating guide, read:

- `从这里开始.md`
- `00-系统总控/总索引.md`
- `00-系统总控/当前能力地图.md`
- `00-系统总控/当前系统能力边界.md`

## First Rule

AI_Director is a Seedance 2.0-centered AI video directing system. All camera, lighting, performance, blocking, scene, actor, prop, and production language refers to simulated AI-generation instructions, not real-world film production.

## Main Workflow

```text
Creative request
-> G0 viral direction gate
-> candidate directions
-> user locks one direction
-> script draft
-> logic review
-> user confirms A/B/C/D/E
-> locked script
-> platform/aspect/duration confirmation
-> director storyboard
-> Seedance 2.0 shot task pack

Production request
-> user provides concrete script
-> logic review
-> user locks script
-> platform/aspect/duration confirmation
-> director storyboard
-> Seedance 2.0 shot task pack
```

## Codex Opening Prompt

```text
这是 AI_Director 项目的专职任务。
请先读取《START_HERE.md》、《从这里开始.md》、总索引和当前能力地图，
再按本次任务调用相关 Skill。只读取任务需要的资料。
```

## What Is Stored In Git

This repository stores project rules, templates, skills, lightweight project records, and training knowledge.

Large media assets, video frames, audio files, generated videos, executable tools, temporary analysis folders, and credentials should stay outside normal Git tracking.
