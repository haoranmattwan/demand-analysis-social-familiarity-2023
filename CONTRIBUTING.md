# Contributing

Contributions should improve the accuracy, transparency, or portability of the published-study replication.

## Before opening a pull request

1. Obtain the analysis data from OSF; do not commit data files or private research materials.
2. Make the same substantive change in the R and Python workflows when applicable.
3. Run the validation checks in both workflows.
4. Explain any change to the model specification and report its effect on the results.
5. Do not commit rendered reports, caches, local environments, correspondence, drafts, or Qualtrics exports.

## Validation

From the repository root, run:

```bash
quarto render Analysis/analysis_R.qmd
python Analysis/analysis_Py.py
```

The workflows should reproduce the validation targets listed in `README.md`. A change that alters those values must be scientifically and computationally justified.

## Reporting issues

Include the operating system, R or Python version, dependency versions, the command used, and the complete error message. Do not attach restricted or private data to a public issue.
