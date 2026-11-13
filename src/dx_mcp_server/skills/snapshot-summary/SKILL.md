---
name: snapshot-summary
description: Summarize the results of the latest completed DX snapshot for a leader or manager, org-wide or for one team. Use when the user asks for snapshot results, a snapshot summary, how the org or their team scored, what changed since the last snapshot, or what developers are saying in snapshot comments. Do not use for a one-off question about a single score or driver; call the snapshot tools directly instead.
metadata:
  author: DX
  version: 1.1.0
  mcp-server: dx-mcp-server
---

# Snapshot summary

Write a short summary of the latest completed snapshot for a leader. Lead with what matters. Do not just list the lowest scores against the benchmark.

## 1. Find the snapshots

Call `listSnapshots(ordering="completed_at")`. Ignore any snapshot with `deleted_at` set. The first remaining item is the latest snapshot. The second remaining item is the comparison snapshot. If the user names a different snapshot to compare against, use that one.

If there is only one snapshot, skip all comparisons and say so.

## 2. Collect data

Use `compareSnapshotScores(snapshot_id, comparison_snapshot_id, score_type)` for the changes. It matches items by id, computes `change`, `direction` and `vs_p_50`, and lists hidden and unmatched items separately. Do not recompute these by hand.

- Headline: `compareSnapshotScores(..., "dxi")`.
- Drivers: `compareSnapshotScores(..., "driver")`.
- Workflows: `compareSnapshotScores(..., "workflow")`, plus `getSnapshotScores(snapshot_id, "workflow")` for the latest snapshot to see each workflow's `distribution`.
- Comments: `getSnapshotComments(snapshot_id)` for the latest snapshot. Follow `next_cursor` for at most 3 pages. Group comments by `driver_name`.

If there is no comparison snapshot, use `getSnapshotScores` for the latest snapshot instead of `compareSnapshotScores`.

### Scoping to a team

If the user asks about one team, or the request names a team, for example a manager asking about their own team, scope the scores to it. Find the team with `listTeams`, then pass its id as the `team_ids` filter to every `compareSnapshotScores` and `getSnapshotScores` call. Team ids are stable across snapshots, so use them rather than snapshot team ids. Compare the team with the comparison snapshot, the org and the benchmarks, but keep the story about what that team can discuss and influence.

`getSnapshotComments` cannot be filtered by team. Say that the comment themes are org-wide, or leave them out if they would mislead.

## 3. Handle thin data

A result with `hidden: true` is below the response threshold. Never treat it as zero. Leave it out of rankings. Also treat rows with very few `respondents` as inconclusive and do not draw conclusions from them. Mention hidden or thin results only when they limit something you are reporting.

## 4. Work out the movers

**Drivers.** The driver results include drivers from every survey branch, and some names repeat with different ids. From the `compareSnapshotScores` results, keep only drivers with a `benchmark_p_50` and a meaningful number of `respondents`. Ignore the small branch drivers. The results are sorted by `change`, so take the 3 biggest gains from the top and the 3 biggest drops from the bottom. Drivers in `hidden`, `only_in_current` or `only_in_comparison` are already excluded. Note them only if they matter.

**Workflows.** Each workflow has its own `unit`, so never add, average or rank workflows against each other or against drivers. Use `direction` and `vs_p_50` from `compareSnapshotScores`, which already account for `lower_is_better`. Report the workflows furthest on the wrong side of p50, and show the `change` in the workflow's own unit. Also flag a workflow whose `distribution` in the latest snapshot is mostly in the worst options, even if its score looks fine. Ignore workflows with no benchmark and only a few respondents. Note workflows in `only_in_current` or `only_in_comparison` as not asked in both snapshots.

**Why.** To explain a big driver drop, do these in order:

1. Read the comments for that driver.
2. Look for a workflow that measures the same friction. For example Deep work with interruption frequency, or Code review with review wait time. Use it as supporting numbers, or to rule a cause out.
3. If something obviously needs a deeper look, such as a big drop that may sit in one team, use `getSnapshotScoresBreakdown` with `snapshotTeam` or another dimension. Teams below the response threshold come back hidden. Note that only if it limits the answer.

If none of these explains it, say the data does not explain it. Do not state a root cause the data does not support. Say what the team could ask about instead. When you dig into a result, say whether it looks org-wide or specific to one team.

## 5. Write the summary

Use these headings in this order. Keep it short and plain.

1. **Context**: snapshot date, number of responses, number of responses in the comparison snapshot, and the comparison snapshot date. State the counts only. Add a line of comment only when participation changed a lot.
2. **Summary**: two or three sentences on how the org did against the benchmark. Give the DXI score and its change from the comparison snapshot. Give the numbers. Lead with the 2 to 4 strongest signals: the biggest strengths to keep, the biggest risks to look into, and meaningful changes since the last snapshot.
3. **What moved**: split into **Gains** and **Drops**, with the change in points for each. For each big drop, say why. Then the workflows furthest from p50, with their units.
4. **What people are saying**: the few themes that matter most, largest first. See the rules below.

Do not add a separate cautions section. Mention a limit only where it changes how to read a result, for example a team or branch that is below the response threshold, or comments that disagree with the scores.

## Comment themes

The comments should add something the scores do not already show. Do not repeat the driver list as a list of comment topics.

- Include a theme only if it comes up in many comments. As a guide, it should be about 10% of the comments or more, and never just one or two comments. Scale this to the size of the snapshot. In a snapshot with hundreds of comments, a handful of comments is not a theme.
- Prefer themes that explain a score, show a cause, cross several drivers, or raise a concern the scores hide. Skip a theme that only says a driver is fine or repeats its score.
- Keep it to 3 to 5 themes, with a line or two each. Say which driver or drivers each theme relates to.
- Order themes by the number of comments, largest first. Show the approximate count next to each theme, for example "(about 10 comments)". Do not reorder by importance.
- Quote at most a few short lines. Never name or guess who wrote a comment, and leave out any names of people that appear in comments.
- If nothing reaches the bar, say the comments had no strong themes. Do not pad.

## Rules

- Say which two snapshots you compared at the top.
- Report only what the data shows. Use comments to explain scores, not to override them.
- If comments are unavailable, say so and write a scores-only summary.
- Protect anonymity. Do not over-interpret comments or scores from small groups, and treat low-response rows as inconclusive.
- Do not give recommendations unless the user asks. If they ask for next steps, give up to three. Tie each to a driver or workflow, and give a next step and the metric to check in the next snapshot. Separate what the team can do itself from what needs help from outside the team.

## Examples

**"How did the last snapshot go?"** Org-wide summary. Compare the latest snapshot with the one before it. Follow steps 1 to 5 as written.

**"How did my team score? I manage the Platform team."** Team-scoped summary. Find Platform with `listTeams`, pass its id as `team_ids` to every score call, and compare the team with the previous snapshot, the org and the benchmarks. Say the comment themes are org-wide.

**"Summarize our snapshot" when there is only one completed snapshot.** No comparison. Use `getSnapshotScores` for the latest snapshot, report scores against the benchmark only, and say at the top that there is nothing to compare with yet.

## Common issues

- **No team matches the name.** Say so and list the closest names from `listTeams`. Do not guess, and do not fall back to an org-wide summary without saying that is what you did.
- **Several teams match the name.** Ask which one, or if the request makes it obvious, say which you chose at the top.
- **Every result for the team is hidden.** The team is below the response threshold. Say that, and do not report the team's scores. Offer the org-wide summary instead.
- **A tool returns an `error` field.** Report the error text and continue with the data you have. If `compareSnapshotScores` fails, fall back to `getSnapshotScores` for each snapshot and compare by id.
- **A snapshot has far fewer responses than the other.** Say so in Context, and treat changes as weaker signals.
