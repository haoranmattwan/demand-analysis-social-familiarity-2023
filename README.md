# A Behavioral-Economic Demand Analysis of Social Reinforcement
### An R and Python Replication of Schulingkamp et al. (2023), *Frontiers in Psychology*

This repository contains the complete, reproducible analysis scripts for the peer-reviewed publication:

> Schulingkamp, R., Wan, H., & Hackenberg, T. D. (2023). Social familiarity and reinforcement value: a behavioral-economic analysis of demand for social interaction with cagemate and non-cagemate female rats. *Frontiers in Psychology*, *14*, 1158365. https://doi.org/10.3389/fpsyg.2023.1158365

The data for this study is available in the Supplementary Material of the original publication at the **[publisher's website](https://www.frontiersin.org/articles/10.3389/fpsyg.2023.1158365/full#supplementary-material)**.

---

## Project Objective

The goal of this project is to apply a behavioral-economic demand analysis to quantify the reinforcing value of a non-tangible good (social interaction). The analysis demonstrates how to model consumption as a function of price and test how experimental manipulations (social familiarity and reinforcer magnitude) affect key economic parameters.

A core feature of this repository is its demonstration of two distinct analytical frameworks for fitting a complex nonlinear model to a small-N, repeated-measures dataset:

1.  A **frequentist, individual-level analysis** using nonlinear least-squares (`lmfit`).
2.  A **Bayesian hierarchical analysis** using a custom nonlinear multilevel model (`PyMC`), which leverages partial pooling for more robust parameter estimation.

## Repository Contents

| File / Folder | Description |
| :--- | :--- |
| **`/Analysis/`** | Contains the primary scripts that replicate all findings in the paper. |
| `analysis.qmd` | A Quarto document with the complete **R** workflow for both frequentist and Bayesian analyses. |
| `analysis.ipynb` | A Jupyter Notebook providing a **Python** translation of the analyses. |
| **`/Figure/`** | All figures as they appear in the final publication. |
| **`/Presentation/`** | Contains the poster that was presented at SQAB. |

---

## Methodological Approach

The analysis applies a computational modeling approach to quantify the value of social interaction by fitting a specialized behavioral-economic model to the experimental data.

* **Nonlinear Demand Curve Modeling**: The core of the analysis is the application of the **Zero-Bounded Exponential (ZBEn) model**, a nonlinear function that describes how consumption changes as a function of price.
* **Dual Analytical Frameworks**: To ensure the robustness of the findings, the ZBEn model was fit using two distinct statistical frameworks:
    * **Frequentist (Individual-Level) Analysis**: Demand models were fit for each subject individually using nonlinear least-squares. This approach allows for a direct assessment of between-subject variability.
    * **Bayesian (Hierarchical) Analysis**: A custom nonlinear hierarchical model was implemented to analyze the entire dataset within a single framework. This approach is statistically powerful for small-N designs as it regularizes individual-level estimates through partial pooling and provides full posterior inference.
* **Hypothesis Testing via Contrasts**: Hypotheses about the effects of the experimental manipulations were tested by performing linear contrasts on the key model parameters ($log(Q_0)$ and $log(\alpha)$) within both the frequentist and Bayesian frameworks.

---

## How to Reproduce This Analysis

First, download the supplementary data from the publisher's website and place it in the `/Analysis/` directory. Then, set up the appropriate software environment.

### R Environment (`/Analysis/analysis.qmd`)

* **Required Packages**: `readr`, `dplyr`, `tidyr`, `minpack.lm`, `multcomp`, `brms`, `tidybayes`.
* **Installation**:
    ```R
    install.packages(c("readr", "dplyr", "tidyr", "minpack.lm", "multcomp", "brms", "tidybayes"))
    ```

### Python Environment (`/Analysis/analysis.ipynb`)

* **Required Packages**: `pandas`, `numpy`, `scipy`, `lmfit`, `pymc`, `arviz`.
* **Installation**:
    ```bash
    pip install pandas numpy scipy lmfit pymc arviz
    ```