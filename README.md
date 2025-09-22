# Social Familiarity and Reinforcement Value: A Behavioral-Economic Analysis

This repository contains the analysis scripts, figures, and presentation materials for the peer-reviewed publication:

> Schulingkamp, R., Wan, H., & Hackenberg, T. D. (2023). Social familiarity and reinforcement value: a behavioral-economic analysis of demand for social interaction with cagemate and non-cagemate female rats. *Frontiers in Psychology*, *14*, 1158365. https://doi.org/10.3389/fpsyg.2023.1158365

---

## Project Overview

This study investigates how social familiarity (cagemate vs. non-cagemate) and reinforcement duration (10s, 30s, 60s) affect the value of social interaction for rats. The core of the project is a behavioral-economic analysis where the price of social access was systematically increased to generate demand functions.

A key feature of this repository is its dual-paradigm analytical approach. The data is analyzed using both:
1.  A **frequentist approach**, with nonlinear models fit for each subject individually.
2.  A **Bayesian multilevel approach**, which models all subjects simultaneously to better handle the small sample size and account for repeated measures.

The data for this study is available in the Supplementary Material of the original publication, which can be accessed at the publisher's website: <https://www.frontiersin.org/articles/10.3389/fpsyg.2023.1158365/full#supplementary-material>.

## Repository Structure

The project materials are organized into the following folders:

* **/Analysis**: Contains the primary analysis scripts.
    * `analysis.qmd`: A Quarto document with the complete **R** code for both the frequentist (`minpack.lm`) and Bayesian (`brms`) analyses.
    * `analysis.ipynb`: A Jupyter Notebook with the corresponding **Python** translation, replicating the analyses using `lmfit` (frequentist) and `PyMC` (Bayesian).

* **/Figure**: Contains the figures as they appear in the final publication.

* **/Presentation**: Includes a slide deck or poster used to present the findings of this research.

---

## Methodology Snapshot

This project applies a modeling approach to quantify how rats value social interaction.

* **Nonlinear Demand Modeling**: The core of both analyses is the **Zero-Bounded Exponential (ZBEn) model**, which describes consumption as a function of price.
* **Frequentist Analysis**: Individual-level demand curves were fit for each of the 24 unique subject-condition combinations using nonlinear least-squares.
* **Bayesian Multilevel Analysis**: A custom nonlinear hierarchical model was implemented in Stan (via `brms`) and `PyMC` to analyze the data, allowing for more robust parameter estimation given the sample size. Posterior distributions of contrasts were examined to determine the effects of familiarity and duration.

---

## Software and Execution

To run the analyses, you will need the appropriate software environment for your chosen language.

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