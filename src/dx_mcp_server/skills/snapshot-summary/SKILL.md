---
name: snapshot-summary
description: Summarize the results of the latest completed DX snapshot. Use when the user asks for snapshot results, a snapshot summary, how the org scored, what changed since the last snapshot, or what developers are saying in snapshot comments.
---

# Snapshot summary

Write a short summary of the latest completed snapshot for a leader. Lead with what matters. Do not just list the lowest scores against the benchmark.

## 1. Find the snapshots

Call `listSnapshots(ordering="completed_at")`. Ignore any snapshot with `deleted_at` set. The first remaining item is the latest snapshot. The second remaining item is the comparison snapshot. If the user names a different snapshot to compare against, use that one.

If there is only one snapshot, skip all comparisons and say so.

## 2. Collect data

- Headline: `getSnapshotScores(snapshot_id, "dxi")` for both snapshots.
- Drivers: `getSnapshotScores(snapshot_id, "driver")` for both snapshots.
- Workflows: `getSnapshotScores(snapshot_id, "workflow")` for both snapshots.
- Comments: `getSnapshotComments(snapshot_id)` for the latest snapshot. Follow `next_cursor` for at most 3 pages. Group comments by `driver_name`.

## 3. Handle thin data

A result with `hidden: true` is below the response threshold. Never treat it as zero. Leave it out of rankings. Also treat rows with very few responses as inconclusive and do not draw conclusions from them. Mention hidden or thin results only when they limit something you are reporting.

## 4. Work out the movers

**Drivers.** The driver results include drivers from every survey branch, and some names repeat with different ids. Match drivers between the two snapshots by id, and compare only drivers present in both with a benchmark and a meaningful number of responses. Ignore the small branch drivers. Subtract, then keep the 3 biggest gains and the 3 biggest drops. Ignore drivers hidden in either snapshot.

**Workflows.** Each workflow has its own `unit`, so never add, average or rank workflows against each other or against drivers. For each workflow, compare `score` with `workflow.benchmark.p_50`, using `workflow.lower_is_better` to decide which side is worse. Report the workflows furthest on the wrong side of p50, and show the change from the comparison snapshot in the workflow's own unit. Also flag a workflow whose `distribution` is mostly in the worst options, even if its score looks fine. Ignore workflows with no benchmark and only a few respondents. Note workflows that were not asked in both snapshots.

**Why.** To explain a big driver drop, do these in order:

1. Read the comments for that driver.
2. Look for a workflow that measures the same friction. For example Deep work with interruption frequency, or Code review with review wait time. Use it as supporting numbers, or to rule a cause out.
3. If something obviously needs a deeper look, such as a big drop that may sit in one team, use `getSnapshotScoresBreakdown` with `snapshotTeam` or another dimension. Teams below the response threshold come back hidden. Note that only if it limits the answer.

If none of these explains it, say the data does not explain it.

## 5. Write the summary

Use these headings in this order. Keep it short and plain.

1. **Context**: snapshot date, number of responses, number of responses in the comparison snapshot, and the comparison snapshot date. State the counts only. Add a line of comment only when participation changed a lot.
2. **Summary**: two or three sentences on how the org did against the benchmark. Give the DXI score and its change from the comparison snapshot. Give the numbers.
3. **What moved**: split into **Gains** and **Drops**, with the change in points for each. For each big drop, say why. Then the workflows furthest from p50, with their units.
4. **What people are saying**: the few themes that matter most, most common first. See the rules below.

Do not add a separate cautions section. Mention a limit only where it changes how to read a result, for example a team or branch that is below the response threshold, or comments that disagree with the scores.

## Comment themes

The comments should add something the scores do not already show. Do not repeat the driver list as a list of comment topics.

- Include a theme only if it comes up in many comments. As a guide, it should be about 10% of the comments or more, and never just one or two comments. Scale this to the size of the snapshot. In a snapshot with hundreds of comments, a handful of comments is not a theme.
- Prefer themes that explain a score, show a cause, cross several drivers, or raise a concern the scores hide. Skip a theme that only says a driver is fine or repeats its score.
- Keep it to 3 to 5 themes, with a line or two each. Say which driver or drivers each theme relates to.
- Quote at most a few short lines. Never name or guess who wrote a comment, and leave out any names of people that appear in comments.
- If nothing reaches the bar, say the comments had no strong themes. Do not pad.

## Rules

- Say which two snapshots you compared at the top.
- Report only what the data shows. Use comments to explain scores, not to override them.
- If comments are unavailable, say so and write a scores-only summary.
- Do not give recommendations unless the user asks.
