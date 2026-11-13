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

Use `compareSnapshotScores(snapshot_id, score_type, comparison_snapshot_id)` for scores. It matches items by id, computes `change`, `direction` and `vs_p_75`, includes each item's `distribution`, and lists hidden and unmatched items separately. Prefer it over working these out by hand. If there is no comparison snapshot, call it without `comparison_snapshot_id`.

- Headline: `compareSnapshotScores(..., "dxi")`. This returns one row per scale (`dxi_five_point`, `dxi_three_point`). Report the scale that has a score in both snapshots.
- Drivers: `compareSnapshotScores(..., "driver")`.
- Workflows: `compareSnapshotScores(..., "workflow")`.
- Impact: `compareSnapshotScores(..., "impact")`. Outcome measures such as Speed, Quality, Ease of delivery and Weekly time loss. Weekly time loss has `lower_is_better` set.
- Tools: `compareSnapshotScores(..., "csat")`. Satisfaction with internal tools and processes. No benchmark.
- Allocation: `compareSnapshotScores(..., "allocation")`. One row per allocation item, with the percentage of time as the score. No benchmark, and `direction` is null because a shift is not better or worse on its own.
- Comments: `getSnapshotComments(snapshot_id)` for the latest snapshot. Follow `next_cursor` for more pages. Group comments by `driver_name`.

### Scoping to a team

If the user asks about one team, or the request names a team, for example a manager asking about their own team, scope the scores to it. Find the team with `listTeams`, then pass its id as the `team_ids` filter to every `compareSnapshotScores` call. Team ids are stable across snapshots, so use them rather than snapshot team ids. Compare the team with the comparison snapshot, the org and the benchmarks, but keep the story about what that team can discuss and influence.

`getSnapshotComments` cannot be filtered by team. Say that the comment themes are org-wide, or leave them out if they would mislead.

## 3. Handle thin data

Items in the `hidden` list are below the response threshold or had no rated answers. Never treat them as zero. Leave it out of rankings. Also treat rows with very few `respondents` as inconclusive and do not draw conclusions from them. Mention hidden results when they limit something you are reporting.

## 4. Work out the movers

**Drivers.** The driver results include drivers from every survey branch, and some names repeat with different ids. From the `compareSnapshotScores` results, keep only drivers with a meaningful number of `respondents`. The results are sorted by `change`, so take the 3 biggest gains from the top and the 3 biggest drops from the bottom. Drivers in `hidden`, `only_in_current` or `only_in_comparison` are already excluded.

**Workflows.** Each workflow has its own `unit`, so never add, average or rank workflows against each other or against drivers. Use `direction` and `vs_p_75`, which already account for `lower_is_better`. Report the workflows furthest on the wrong side of p75, and show the `change` in the workflow's own unit. Also flag a workflow whose `distribution` is mostly in the worst options, even if its score looks fine. Note workflows in `only_in_current` or `only_in_comparison` as not asked in both snapshots.

**Impact.** These are outcomes, not causes. Report each against p75 and its change, using `direction` since Weekly time loss is lower-is-better. Flag an impact whose `distribution` has notable weight in the worst options.

**Tools.** CSAT has no benchmark. Report the lowest-scoring tools and the biggest changes. Tools only some people use have few `respondents`, so check that before reporting one. Use a tool score to explain a driver where they overlap, for example an observability tool with Production debugging.

**Allocation.** Report the split, for example new features against KTLO, and how it shifted in percentage points. Do not call a shift better or worse unless the drivers or comments support it.

**Why.** To explain a big driver drop, do these in order:

1. Read the comments for that driver.
2. Look for a workflow or tool that measures the same friction. For example Deep work with interruption frequency, or Code review with review wait time. Use it as supporting numbers, or to rule a cause out.
3. If something needs a deeper look, such as a big drop that may sit in one team, use `getSnapshotScoresBreakdown` with `snapshotTeam` or another dimension.

If none of these explains it, say the data does not explain it. Do not state a root cause the data does not support. Say what the team could ask about instead. When you dig into a result, say whether it looks org-wide or specific to one team.

## 5. Write the summary

Use these headings in this order. Keep it short and plain.

1. **Context**: snapshot date, number of responses, number of responses in the comparison snapshot, and the comparison snapshot date.
2. **Summary**: One paragraph on how the org did. Give the DXI score and its change from the comparison snapshot, the impact scores against the benchmark, how the drivers did against the benchmark, and the time allocation split with its shift. Give the numbers. Lead with the 2 to 4 strongest signals: the biggest strengths to keep, the biggest risks to look into, and meaningful changes since the last snapshot.
3. **What moved**: split into **Gains** and **Drops**, with the change in points for each. For each big drop, say why. Then the workflows furthest from p75, with their units.
4. **Tools**: the lowest-scoring tools and the biggest changes, with respondent counts. Leave this heading out if the snapshot has no CSAT items.
5. **What people are saying**: the few themes that matter most, largest first. See the rules below.

## Comment themes

The comments should add something the scores do not already show. Do not repeat the driver list as a list of comment topics.

- Prefer up to 3 to 5 themes that explain a score, show a cause, cross several drivers, or raise a concern the scores hide.
- Quote at most a few short lines. Never name or guess who wrote a comment, and leave out any names of people that appear in comments.
- If nothing reaches the bar, say the comments had no strong themes. Do not pad.

## Rules

- Say which two snapshots you compared at the top.
- Report only what the data shows. Use comments to explain scores, not to override them.
- If comments are unavailable, say so and write a scores-only summary.
- Protect anonymity. Do not over-interpret comments or scores from small groups, and treat low-response rows as inconclusive.
- Do not give recommendations unless the user asks. If they ask for next steps, give up to three. Tie each to a driver or workflow, and give a next step and the metric to check in the next snapshot. Separate what the team can do itself from what needs help from outside the team.

## Examples

- **"How did the last snapshot go?"** Org-wide summary against the previous snapshot.
- **"How did my team score? I manage the Platform team."** Team-scoped. Pass the Platform team id as `team_ids` to every score call, and say the comment themes are org-wide.
- **"Summarize our snapshot" with only one completed snapshot.** Call `compareSnapshotScores` without `comparison_snapshot_id`, report against the benchmark only, and say at the top that there is nothing to compare with yet.

## Common issues

- **No team matches the name.** Say so and list the closest names from `listTeams`. Do not guess, and do not fall back to an org-wide summary without saying that is what you did.
- **Several teams match the name.** Ask which one, or if the request makes it obvious, say which you chose at the top.
- **Every result for the team is hidden.** The team is below the response threshold. Say that, and do not report the team's scores. Offer the org-wide summary instead.
- **A tool returns an `error` field.** Report the error text and continue with the data you have.
- **A snapshot has far fewer responses than the other.** Say so in Context, and treat changes as weaker signals.
