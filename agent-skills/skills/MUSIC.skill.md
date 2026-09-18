# Skill: MUSIC

## Metadata

- name: MUSIC
- version: 1.0.0
- description: Generate music via Sonic Forge pipeline — style selection, generation, DNA tagging, output delivery.
- triggers: "make a beat", "produce a track", "make music", "write a song", "create an instrumental", /music, /build
- required_personas: Developer (creative)
- max_duration: 10m
- confidence_threshold: 80

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Interpret intent | Developer | User request, context | Style, prompt, duration parameters | Parse user request into Sonic Forge parameters. Infer style if not explicit. Check pipeline state for continuation. | Style is valid; prompt is non-empty |
| 2 | Check pipeline | Developer | Parameters | Pipeline health, engine registry status | Verify Sonic Forge pipeline is online (Blueprint through Export). Check engine registration health. | Pipeline healthy; all engines registered |
| 3 | Generate | Developer | Parameters | Job ID, generation status | Submit to Sonic Forge via Empire-1 API. Poll until complete or timeout. | Job completed; output files exist |
| 4 | Tag | Developer | Output files | DNA tags (SHA-256) | Compute DNA hashes for all output files. Tag with provenance metadata. | Every file has a DNA tag |
| 5 | Verify | Developer | Output files, DNA tags | Verification result | Check output quality (file size > 0, WAV header valid, duration matches). | All verification checks pass |
| 6 | Deliver | Developer | Output paths, DNA tags, style metadata | Summary to user, pipeline state update | Print output paths, DNA tags, style info. Update pipeline state with last run details. | User has all info needed |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Style valid | 1 | Style is registered in Sonic Forge pipeline | Fall back to default style; notify user |
| Pipeline healthy | 2 | All 15 engines registered | Report missing engines; try anyway |
| Generation complete | 3 | Job status is "completed" or "done" | Surface error; allow retry with different params |
| DNA integrity | 4 | All output files tagged; no collisions | Re-tag; if collision, flag manually |
| Output valid | 5 | Files non-empty; WAV headers valid; duration within 10% | Report invalid files; retry generation |
| Delivery | 6 | Summary displayed; state saved | Retry state write |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Parsed parameters | 1 | JSON (style, prompt, duration) | Project lifetime |
| Pipeline health | 2 | JSON (engine statuses) | Session |
| Generation result | 3 | JSON (job_id, status, output_paths) | Permanent |
| DNA tags | 4 | JSON (file->hash mapping) | Permanent |
| Verification | 5 | JSON (checks passed/failed) | Session |
| Delivery receipt | 6 | Markdown (user-facing summary) | Project lifetime |

## Confidence Scoring

- Intent match: 0-25 (style, prompt, mood match user request)
- Pipeline health: 0-15 (all engines green)
- Generation quality: 0-30 (file validity, duration accuracy, no artifacts)
- DNA coverage: 0-15 (all files tagged)
- User satisfaction: 0-15 (no errors surfaced)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 3 | Cancel job; mark as failed in pipeline state | Job stuck or user cancels |
| 6 | Revert pipeline state to before this run | State corruption |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | music.intent_parsed | style, prompt, duration |
| 2 | music.pipeline_checked | engine_count, healthy_count |
| 3 | music.generated | job_id, duration_ms |
| 4 | music.tagged | file_count, tag_count |
| 5 | music.verified | checks_passed, checks_failed |
| 6 | music.delivered | user_summary_length |
