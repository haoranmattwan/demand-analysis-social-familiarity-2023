# Social Familiarity and Reinforcement Value

[![DOI](https://img.shields.io/badge/DOI-10.3389%2Ffpsyg.2023.1158365-0A7BBB)](https://doi.org/10.3389/fpsyg.2023.1158365)
[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)

Reproducible R and Python analyses for:

> Schulingkamp, R., Wan, H., & Hackenberg, T. D. (2023). Social familiarity and reinforcement value: A behavioral-economic analysis of demand for social interaction with cagemate and non-cagemate female rats. *Frontiers in Psychology, 14*, 1158365. https://doi.org/10.3389/fpsyg.2023.1158365

Four focal rats completed fixed-ratio schedules for 10-, 30-, and 60-second access to a cagemate or non-cagemate. Social-interaction rate declined as price increased and was well described by the zero-bounded exponential (ZBEn) demand model. The published analysis found no systematic effects of partner familiarity or interaction duration on demand intensity or elasticity.

## Data availability

Data are distributed separately through the Open Science Framework (OSF) and are intentionally not tracked in this repository. [Find the study data on OSF by the exact article title](https://osf.io/search/?q=%22Social%20familiarity%20and%20reinforcement%20value%22), download the analysis-ready CSV, and save it as `Analysis/Table1.csv`.

If the downloaded file has another location or name, set `SOCIAL_DEMAND_DATA` to its path before running an analysis. The publisher's [supplementary materials](https://doi.org/10.3389/fpsyg.2023.1158365) provide an archival cross-check. No data are bundled with releases from this repository.

The article and the existing repository history do not identify a stable OSF project URL. The title-search link is used here rather than inventing a project identifier; it should be replaced with the permanent OSF record URL when available.

## Reproduce the analyses

Clone the repository, download the data from OSF, and run either workflow from the repository root.

### R

The R environment is recorded in `renv.lock`.

```r
install.packages("renv")
renv::restore()
```

```bash
quarto render Analysis/analysis_R.qmd
```

### Python

Python 3.10 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python Analysis/analysis_Py.py
```

The notebook `Analysis/analysis_Py.ipynb` is a thin interactive entry point to the same Python source, preventing the script and notebook from diverging.

## Validation targets

With the published data, both workflows check the principal reported results:

| Analysis | Parameter | Published value |
|---|---:|---:|
| 24 subject-condition demand curves | Mean R² | 0.91 |
| Cagemate vs. non-cagemate | Elasticity, α | *p* = .710 |
| Cagemate vs. non-cagemate | Demand intensity, Q₀ | *p* = .471 |
| 10 vs. 30 vs. 60 seconds | Elasticity, α | *p* = .226 |
| 10 vs. 30 vs. 60 seconds | Demand intensity, Q₀ | *p* = .805 |

The compatibility analysis retains the aggregate familiarity equation in the archived publication code, including its asymmetric `Q0` term, because that specification reproduces the reported statistics. Both workflows also report a corrected symmetric specification as a sensitivity analysis. That sensitivity result is not a replacement for the published analysis and must be interpreted in light of the small sample, repeated-measures design, and confounding of familiarity with condition order.

## Repository structure

| Path | Purpose |
|---|---|
| `Analysis/analysis_R.qmd` | Publication-aligned R workflow and rendered report source |
| `Analysis/analysis_Py.py` | Publication-aligned Python workflow |
| `Analysis/analysis_Py.ipynb` | Interactive entry point to the Python workflow |
| `Figure/` | Publication figures and source artwork |
| `Presentation/` | Public presentation materials |
| `fpsyg-14-1158365.pdf` | Local reference copy of the open-access article; ignored by Git |

Historical code, data, manuscript drafts, correspondence, and generated outputs may remain in a local working archive, but `.gitignore` prevents them from entering version control.

## Analytic scope

The primary workflows reproduce the subject-level nonlinear fits and aggregate frequentist comparisons reported in the article. Earlier repository versions described exploratory Bayesian multilevel models as part of the publication; they were not reported in the article and are therefore not presented as confirmatory replications here.

The analysis uses the ZBEn model of Gilroy et al. (2021). It estimates demand intensity (`Q0`) and elasticity (`alpha`), derives essential value, and numerically approximates `Pmax` and `Omax`. See the article for the experimental design, exclusions, ethics statement, and substantive interpretation.

## Open-science and reuse notes

- Analysis code is licensed under the [MIT License](LICENSE).
- The published article is open access under CC BY 4.0; its copyright remains with the article authors.
- Data should be cited using the metadata on the OSF record.
- Generated reports, caches, local environments, private research materials, and data are excluded from version control.
- Please cite the article and this repository when reusing the workflow. Machine-readable citation metadata are provided in `CITATION.cff`.

## Contributing

Corrections that improve computational reproducibility are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for scope, validation expectations, and data-handling rules.
