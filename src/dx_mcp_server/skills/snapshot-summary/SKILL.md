---
name: snapshot-summary
description: Summarize the results of the latest completed DX snapshot. Use when the user asks for snapshot results, a snapshot summary, how the org scored, what changed since the last snapshot, or what developers are saying in snapshot comments.
---

# Snapshot summary

Write a short summary of the latest completed snapshot for a leader. Lead with what matters. Do not just list the lowest scores against the benchmark.

## 1. Find the snapshots

Call `listSnapshots(ordering="completed_at")`. The first item is the latest snapshot. The second item is the comparison snapshot. If the user names a different snapshot to compare against, use that one.

If there is only one snapshot, skip all comparisons and say so.

## 2. Collect data

- Headline: `getSnapshotScores(snapshot_id, "dxi")` for the latest snapshot.
- Drivers: `getSnapshotScores(snapshot_id, "driver")` for both snapshots.
- Workflows: `getSnapshotScores(snapshot_id, "workflow")` for both snapshots.
- Branches: `listSnapshotBranches()`, then `getSnapshotScores(snapshot_id, "dxi", branch_ids=...)` once per branch. Always include the main branch in `branch_ids`.
- Comments: `getSnapshotComments(snapshot_id)`. Follow `next_cursor` for at most 3 pages. Group comments by `driver_name`.

## 3. Handle thin data

A result with `hidden: true` is below the response threshold. Never treat it as zero. Leave it out of rankings and say it is hidden. Also treat rows with very few responses as inconclusive, and say so. Do not draw conclusions from them.

## 4. Work out the movers

**Drivers.** Match drivers between the two snapshots by id and subtract. Keep the 3 biggest gains and the 3 biggest drops. Ignore drivers hidden in either snapshot.

**Workflows.** Each workflow has its own `unit`, so never add, average or rank workflows against each other or against drivers. For each workflow, compare `score` with `workflow.benchmark.p_50`, using `workflow.lower_is_better` to decide which side is worse. Report the workflows furthest on the wrong side of p50, and show the change from the comparison snapshot in the workflow's own unit. Also flag a workflow whose `distribution` is mostly in the worst options, even if its score looks fine.

**Why.** To explain a big driver drop, do these in order:
1. Read the comments for that driver.
2. Look for a workflow that measures the same friction. For example Deep work with interruption frequency, or Code review with review wait time. Use it as supporting numbers.
3. If the drop is concentrated in one team or branch, say so, using `getSnapshotScoresBreakdown`.

If none of these explains it, say the data does not explain it.

## 5. Write the summary

Use these headings in this order. Keep it short and plain.

1. **Context**: snapshot date, number of responses, number of responses in the comparison snapshot, and the comparison snapshot date. Note a large change in participation.
2. **Summary**: two or three sentences on how the org did against the benchmark. Give the numbers.
3. **What moved**: the top driver gains and drops with the change in points. For each big drop, say why. Then the workflows furthest from p50, with their units.
4. **What people are saying**: the main themes in the comments, most common first. Say which driver each theme belongs to. Quote at most a few short lines. Never name or guess who wrote a comment.
5. **Branches**: one line per branch with its score and response count. Mark hidden branches as below the response threshold.
6. **Cautions**: only if needed. Hidden or low-response items, missing data, or comments that disagree with the scores.

## Rules

- Say which two snapshots you compared at the top.
- Report only what the data shows. Use comments to explain scores, not to override them.
- If comments are unavailable, say so and write a scores-only summary.
- Do not give recommendations unless the user asks.
