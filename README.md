# ci-triage-demo

Small Python project and two GitHub Actions workflows. `ci.yml` is started by hand and produces four kinds of CI logs. `push-ci.yml` runs on every push and pull request.

Trigger `ci.yml` with `workflow_dispatch` and a `scenario` choice. The default is `green`. Each run executes only the steps for that choice.

Nothing in the job log names the choice. The run title does (`ci (green)`, and so on). Descriptions of what each path is for live in this file.

## What each scenario does

| Scenario | What runs | What the log shows |
| --- | --- | --- |
| `green` | `tests/test_calc.py::test_add` | `add(2, 2)` is 4. The test passes. |
| `infra` | `pip install` against `https://pypi.invalid/simple` | A real DNS or connection error from pip. No tests run. |
| `real_bug` | `tests/test_calc.py::test_total` | `total(2, 2)` returns 5. pytest fails with `assert 5 == 4`. Re-running the job fails the same way. |
| `flaky` | `tests/test_events.py::test_event_count` | On attempt 1 the collected events are only `created`, so the assertion expects `['created', 'updated']` and gets `['created']`. On attempt 2 and later both events are present and the test passes. |

`add` is correct. `total` always returns `a + b + 1`. The green path never calls `total`. The real-bug path never calls `add`.

## Why `flaky` is simulated

GitHub Actions will not produce a real race on demand. `test_event_count` reads `GITHUB_RUN_ATTEMPT`, which Actions sets to `1` on the first try and increments on each re-run. The first attempt drops one event so the failure looks like a missed delivery. Later attempts keep both events. The branch exists only so a re-run of the failed job can go green.

Locally, if `GITHUB_RUN_ATTEMPT` is unset, the test passes.

## PowerShell

From this repo, with the [GitHub CLI](https://cli.github.com/) authenticated:

```powershell
gh workflow run ci.yml -f scenario=green
gh workflow run ci.yml -f scenario=infra
gh workflow run ci.yml -f scenario=real_bug
gh workflow run ci.yml -f scenario=flaky
```

`gh workflow run` does not print the run id. List recent runs; the number in the output is the id:

```powershell
gh run list --workflow ci.yml --limit 5
```

Re-run only the failed jobs of one run. For `flaky`, the new attempt sees `GITHUB_RUN_ATTEMPT` greater than `1`, so `test_event_count` passes. `infra` and `real_bug` fail again.

```powershell
gh run rerun <id> --failed
```

## Push workflow

`push-ci.yml` runs on every `push` and every `pull_request`, for any branch. It installs pytest and runs `tests/test_push_demo.py`. That test calls `word_count` in `demo/words.py`. As committed here, `word_count("one two three")` is `3`, so the check passes.

Demo a failure, then a fix, from PowerShell:

```powershell
git checkout -b demo/word-count
```

In `demo/words.py`, change the return to `len(text.split()) - 1`.

```powershell
git add demo/words.py
git commit -m "Return the wrong word count"
git push -u origin HEAD
```

GitHub runs `push-ci` on that branch. pytest fails with `assert 2 == 3`. Wait for the Slack message about that run.

Put the return back to `len(text.split())`, then:

```powershell
git add demo/words.py
git commit -m "Return the word count"
git push
```

The following run on that branch passes.
