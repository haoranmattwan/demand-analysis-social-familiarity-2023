"""Publication-aligned ZBEn demand analysis for Schulingkamp et al. (2023).

Run from the repository root:

    python Analysis/analysis_Py.py

The analysis data are distributed through OSF and are not tracked here. By
default, this script looks for Analysis/Table1.csv. Set SOCIAL_DEMAND_DATA or
pass --data to use another location.
"""

from __future__ import annotations

import argparse
import os
import platform
import sys
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import least_squares
from scipy.stats import f as f_distribution
from scipy.stats import norm


ARTICLE_DOI = "10.3389/fpsyg.2023.1158365"
EXPECTED_COLUMNS = (
    "Rat",
    "Social Familiarity",
    "Social Duration",
    "Social FR",
    "Interaction Rate",
)
VALIDATION_TARGETS = {
    "mean_r_squared": 0.910,
    "familiarity_alpha_p": 0.0163,
    "familiarity_q0_p": 0.471,
    "duration_alpha_p": 0.226,
    "duration_q0_p": 0.805,
}


def ihs(x: np.ndarray | float) -> np.ndarray:
    """Base-10 inverse-hyperbolic-sine transform used by the ZBEn model."""
    values = np.asarray(x, dtype=float)
    return np.log10(0.5 * values + np.sqrt(0.25 * values**2 + 1.0))


def inverse_ihs(y: np.ndarray | float) -> np.ndarray:
    """Inverse of :func:`ihs`."""
    values = np.asarray(y, dtype=float)
    return (10.0 ** (2.0 * values) - 1.0) / (10.0**values)


def zben(fr: np.ndarray, log_alpha: float, q0: float) -> np.ndarray:
    """Zero-bounded exponential demand model on the transformed scale."""
    ihs_q0 = ihs(q0)
    return ihs_q0 * np.exp((-np.exp(log_alpha) / ihs_q0) * q0 * fr)


def essential_value(alpha: float) -> float:
    return 1.0 / (100.0 * alpha)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce the publication-aligned demand analyses for "
            f"doi:{ARTICLE_DOI}."
        )
    )
    parser.add_argument(
        "--data",
        type=Path,
        help="Path to the OSF analysis-ready CSV (default: Analysis/Table1.csv).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory for generated CSV result tables.",
    )
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Report but do not enforce the rounded publication targets.",
    )
    return parser.parse_args()


def resolve_data_path(explicit_path: Path | None) -> Path:
    project_root = Path(__file__).resolve().parents[1]
    environment_path = os.getenv("SOCIAL_DEMAND_DATA")
    candidates = [
        explicit_path,
        Path(environment_path).expanduser() if environment_path else None,
        project_root / "Analysis" / "Table1.csv",
        Path.cwd() / "Analysis" / "Table1.csv",
        Path.cwd() / "Table1.csv",
    ]

    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(
        "Data not found. Download Table1.csv from OSF and place it in Analysis/, "
        "set SOCIAL_DEMAND_DATA, or pass --data."
    )


def load_and_validate(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(path)
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(raw.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    if raw.loc[:, EXPECTED_COLUMNS].isna().any(axis=None):
        raise ValueError("Required analysis fields contain missing values.")
    if (raw["Interaction Rate"] < 0).any() or (raw["Social FR"] <= 0).any():
        raise ValueError(
            "Interaction rates must be nonnegative and FR prices must be positive."
        )

    expected_familiarity = {"Cagemate", "Non-cagemate"}
    expected_duration = {"10 Sec", "30 Sec", "60 Sec"}
    if (
        raw["Rat"].nunique() != 4
        or set(raw["Social Familiarity"].unique()) != expected_familiarity
        or set(raw["Social Duration"].unique()) != expected_duration
    ):
        raise ValueError("The data do not contain the expected 4 x 2 x 3 design.")

    prepared = raw.rename(
        columns={
            "Rat": "rat",
            "Social Familiarity": "familiarity",
            "Social Duration": "duration",
            "Social FR": "fr",
            "Interaction Rate": "interaction_rate",
        }
    ).copy()
    prepared["lq"] = ihs(prepared["interaction_rate"].to_numpy())

    analysis = (
        prepared.groupby(
            ["rat", "familiarity", "duration", "fr"], as_index=False, sort=True
        )
        .agg(
            interaction_rate=("interaction_rate", "mean"),
            lq=("lq", "mean"),
            sessions=("lq", "size"),
        )
        .sort_values(["rat", "familiarity", "duration", "fr"])
        .reset_index(drop=True)
    )
    return raw, analysis


def fit_nonlinear(
    observed: np.ndarray,
    model: Callable[[np.ndarray], np.ndarray],
    initial: Sequence[float],
    lower: Sequence[float],
    upper: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, float, int]:
    """Fit a nonlinear least-squares model and estimate its covariance matrix."""
    observed = np.asarray(observed, dtype=float)
    result = least_squares(
        lambda parameters: observed - model(parameters),
        x0=np.asarray(initial, dtype=float),
        bounds=(np.asarray(lower, dtype=float), np.asarray(upper, dtype=float)),
        max_nfev=100_000,
        x_scale="jac",
    )
    if not result.success:
        raise RuntimeError(f"Nonlinear model did not converge: {result.message}")

    residual_df = observed.size - result.x.size
    if residual_df <= 0:
        raise ValueError("The fitted model has no residual degrees of freedom.")

    sse = float(np.dot(result.fun, result.fun))
    covariance = np.linalg.pinv(result.jac.T @ result.jac) * (sse / residual_df)
    return result.x, covariance, sse, residual_df


def fit_subject_curves(analysis: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str | bool]] = []
    minimum_fr = float(analysis["fr"].min())
    maximum_fr = float(analysis["fr"].max())
    price_grid = np.arange(minimum_fr, maximum_fr + 0.05, 0.1)

    for (rat, familiarity, duration), curve in analysis.groupby(
        ["rat", "familiarity", "duration"], sort=True
    ):
        fr = curve["fr"].to_numpy(dtype=float)
        observed = curve["lq"].to_numpy(dtype=float)
        parameters, _, sse, _ = fit_nonlinear(
            observed,
            lambda values: zben(fr, values[0], values[1]),
            initial=(-6.0, 50.0),
            lower=(-np.inf, np.finfo(float).eps),
            upper=(np.inf, np.inf),
        )
        log_alpha, q0 = parameters
        alpha = float(np.exp(log_alpha))
        total_sum_squares = float(np.sum((observed - observed.mean()) ** 2))
        r_squared = 1.0 - sse / total_sum_squares

        predicted_lq = zben(price_grid, log_alpha, q0)
        response_output = inverse_ihs(predicted_lq) * price_grid
        maximum_index = int(np.argmax(response_output))

        rows.append(
            {
                "rat": int(rat),
                "familiarity": str(familiarity),
                "duration": str(duration),
                "alpha": alpha,
                "q0": float(q0),
                "essential_value": essential_value(alpha),
                "pmax": float(price_grid[maximum_index]),
                "omax": float(response_output[maximum_index]),
                "r_squared": r_squared,
                "converged": True,
            }
        )

    return pd.DataFrame(rows)


def normal_contrast(
    parameters: np.ndarray,
    covariance: np.ndarray,
    weights: Sequence[float],
    label: str,
) -> dict[str, float | str]:
    contrast = np.asarray(weights, dtype=float)
    estimate = float(contrast @ parameters)
    standard_error = float(np.sqrt(contrast @ covariance @ contrast))
    z_value = estimate / standard_error
    return {
        "comparison": label,
        "estimate": estimate,
        "standard_error": standard_error,
        "z_value": z_value,
        "p_value": float(2.0 * norm.sf(abs(z_value))),
    }


def fit_familiarity_model(analysis: pd.DataFrame) -> pd.DataFrame:
    familiarity = (
        analysis.groupby(["rat", "familiarity", "fr"], as_index=False)
        .agg(lq=("lq", "mean"))
        .sort_values(["rat", "familiarity", "fr"])
    )
    is_cagemate = (familiarity["familiarity"] == "Cagemate").to_numpy(float)
    is_non_cagemate = (
        familiarity["familiarity"] == "Non-cagemate"
    ).to_numpy(float)
    fr = familiarity["fr"].to_numpy(float)
    observed = familiarity["lq"].to_numpy(float)

    def familiarity_model(parameters: np.ndarray) -> np.ndarray:
        log_alpha_cagemate, log_alpha_non_cagemate, q_cagemate, q_non = parameters
        condition_q0 = q_cagemate * is_cagemate + q_non * is_non_cagemate
        log_alpha = (
            log_alpha_cagemate * is_cagemate
            + log_alpha_non_cagemate * is_non_cagemate
        )
        return ihs(condition_q0) * np.exp(
            (-np.exp(log_alpha) / ihs(condition_q0)) * condition_q0 * fr
        )

    parameters, covariance, _, _ = fit_nonlinear(
        observed,
        familiarity_model,
        initial=(-6.0, -6.0, 50.0, 50.0),
        lower=(-np.inf, -np.inf, np.finfo(float).eps, np.finfo(float).eps),
        upper=(np.inf, np.inf, np.inf, np.inf),
    )
    return pd.DataFrame(
        [
            normal_contrast(
                parameters,
                covariance,
                (1.0, -1.0, 0.0, 0.0),
                "Elasticity (log alpha)",
            ),
            normal_contrast(
                parameters,
                covariance,
                (0.0, 0.0, 1.0, -1.0),
                "Demand intensity (Q0)",
            ),
        ]
    )


def nested_f_test(
    full_sse: float,
    full_df: int,
    reduced_sse: float,
    reduced_df: int,
    label: str,
) -> dict[str, float | int | str]:
    numerator_df = reduced_df - full_df
    f_value = ((reduced_sse - full_sse) / numerator_df) / (full_sse / full_df)
    return {
        "comparison": label,
        "df_numerator": numerator_df,
        "df_denominator": full_df,
        "f_value": f_value,
        "p_value": float(f_distribution.sf(f_value, numerator_df, full_df)),
    }


def fit_duration_models(analysis: pd.DataFrame) -> pd.DataFrame:
    duration = (
        analysis.groupby(["rat", "duration", "fr"], as_index=False)
        .agg(lq=("lq", "mean"))
        .sort_values(["rat", "duration", "fr"])
    )
    d10 = (duration["duration"] == "10 Sec").to_numpy(float)
    d30 = (duration["duration"] == "30 Sec").to_numpy(float)
    d60 = (duration["duration"] == "60 Sec").to_numpy(float)
    fr = duration["fr"].to_numpy(float)
    observed = duration["lq"].to_numpy(float)

    def full_model(parameters: np.ndarray) -> np.ndarray:
        a10, a30, a60, q10, q30, q60 = parameters
        log_alpha = a10 * d10 + a30 * d30 + a60 * d60
        q0 = q10 * d10 + q30 * d30 + q60 * d60
        return zben(fr, log_alpha, q0)

    def common_alpha_model(parameters: np.ndarray) -> np.ndarray:
        common_alpha, q10, q30, q60 = parameters
        q0 = q10 * d10 + q30 * d30 + q60 * d60
        return zben(fr, common_alpha, q0)

    def common_q0_model(parameters: np.ndarray) -> np.ndarray:
        a10, a30, a60, common_q0 = parameters
        log_alpha = a10 * d10 + a30 * d30 + a60 * d60
        return zben(fr, log_alpha, common_q0)

    full_parameters, _, full_sse, full_df = fit_nonlinear(
        observed,
        full_model,
        initial=(-6.0, -6.0, -6.0, 50.0, 50.0, 50.0),
        lower=(-np.inf, -np.inf, -np.inf, 1e-12, 1e-12, 1e-12),
        upper=(np.inf, np.inf, np.inf, np.inf, np.inf, np.inf),
    )
    common_alpha_parameters, _, common_alpha_sse, common_alpha_df = fit_nonlinear(
        observed,
        common_alpha_model,
        initial=(-6.0, 50.0, 50.0, 50.0),
        lower=(-np.inf, 1e-12, 1e-12, 1e-12),
        upper=(np.inf, np.inf, np.inf, np.inf),
    )
    common_q0_parameters, _, common_q0_sse, common_q0_df = fit_nonlinear(
        observed,
        common_q0_model,
        initial=(-6.0, -6.0, -6.0, 50.0),
        lower=(-np.inf, -np.inf, -np.inf, 1e-12),
        upper=(np.inf, np.inf, np.inf, np.inf),
    )

    # Keep named variables visible to static analysis and future debugging.
    _ = full_parameters, common_alpha_parameters, common_q0_parameters

    return pd.DataFrame(
        [
            nested_f_test(
                full_sse,
                full_df,
                common_alpha_sse,
                common_alpha_df,
                "Elasticity (alpha)",
            ),
            nested_f_test(
                full_sse,
                full_df,
                common_q0_sse,
                common_q0_df,
                "Demand intensity (Q0)",
            ),
        ]
    )


def build_validation(
    curves: pd.DataFrame,
    familiarity: pd.DataFrame,
    duration: pd.DataFrame,
) -> pd.DataFrame:
    computed = {
        "mean_r_squared": float(curves["r_squared"].mean()),
        "familiarity_alpha_p": float(familiarity.loc[0, "p_value"]),
        "familiarity_q0_p": float(familiarity.loc[1, "p_value"]),
        "duration_alpha_p": float(duration.loc[0, "p_value"]),
        "duration_q0_p": float(duration.loc[1, "p_value"]),
    }
    rows = []
    for statistic, expected in VALIDATION_TARGETS.items():
        calculated = computed[statistic]
        difference = abs(calculated - expected)
        rows.append(
            {
                "statistic": statistic,
                "computed": calculated,
                "expected": expected,
                "absolute_difference": difference,
                "passes": difference <= 0.01,
            }
        )
    return pd.DataFrame(rows)


def print_table(title: str, table: pd.DataFrame) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print(table.to_string(index=False, float_format=lambda value: f"{value:.4f}"))


def write_outputs(output_dir: Path, tables: dict[str, pd.DataFrame]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)


def main() -> int:
    args = parse_args()
    data_path = resolve_data_path(args.data)
    raw, analysis = load_and_validate(data_path)
    curves = fit_subject_curves(analysis)
    familiarity = fit_familiarity_model(analysis)
    duration = fit_duration_models(analysis)
    validation = build_validation(curves, familiarity, duration)

    design_summary = pd.DataFrame(
        [
            {
                "source": str(data_path),
                "session_rows": len(raw),
                "aggregated_rows": len(analysis),
                "rats": analysis["rat"].nunique(),
                "curves": len(curves),
            }
        ]
    )
    curve_summary = pd.DataFrame(
        [
            {
                "curves": len(curves),
                "mean_r_squared": curves["r_squared"].mean(),
                "minimum_r_squared": curves["r_squared"].min(),
                "maximum_r_squared": curves["r_squared"].max(),
            }
        ]
    )

    print_table("Validated analysis data", design_summary)
    print_table("Subject-condition ZBEn parameters", curves)
    print_table("Demand-curve fit summary", curve_summary)
    print_table("Familiarity tests", familiarity)
    print_table("Duration tests", duration)
    print_table("Analysis validation checks", validation)

    print("\nEnvironment")
    print("-----------")
    print(f"Python: {platform.python_version()}")
    print(f"NumPy: {np.__version__}")
    print(f"pandas: {pd.__version__}")
    print(f"SciPy: {scipy.__version__}")

    tables = {
        "subject_condition_parameters": curves,
        "familiarity_tests": familiarity,
        "duration_tests": duration,
        "validation": validation,
    }
    if args.output_dir is not None:
        write_outputs(args.output_dir, tables)
        print(f"\nGenerated tables written to: {args.output_dir.resolve()}")

    if not args.no_check and not validation["passes"].all():
        print(
            "\nERROR: At least one computed result differs materially from the "
            "expected value.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
