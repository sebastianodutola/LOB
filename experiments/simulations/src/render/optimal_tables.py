"""
Statistical analysis and reporting for optimal skew coefficient results.
Generates markdown tables and fits power law model to optimization data.
"""

import os
import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm


def load_data(pickle_path):
    """Load pickled optimization results."""
    with open(pickle_path, "rb") as f:
        return pickle.load(f)


def create_dataframe(grids, informed_frac_space, price_vol_space):
    """Convert grid results to long-form dataframe."""
    data = []
    for i in range(len(informed_frac_space)):
        for j in range(len(price_vol_space)):
            data.append(
                {
                    "informed fraction": informed_frac_space[i],
                    "price volatility": price_vol_space[j],
                    "optimal sc-returns": grids["optimal sc-returns"][i, j],
                    "optimal sc-msd": grids["optimal sc-msd"][i, j],
                    "optimal sc-pnl": grids["optimal sc-pnl"][i, j],
                    "average returns": grids["optimal returns"][i, j],
                    "final pnl": grids["optimal pnl"][i, j],
                }
            )
    return pd.DataFrame(data)


def fit_power_law_model(df):
    """Fit log-linear model to optimal skew coefficients."""
    X = np.log(df[["informed fraction", "price volatility"]])
    X = sm.add_constant(X)
    y = np.log(df["optimal sc-returns"])

    model = sm.OLS(y, X).fit()
    return model


def ols_summary_to_markdown(model):
    """Convert OLS regression results to markdown table with key diagnostics."""
    # Coefficients table
    coef_table = []
    coef_table.append("| Variable | Coefficient | Std Error | t-statistic | P>\|t\| |")
    coef_table.append("|----------|-------------|-----------|-------------|-------|")

    for i, name in enumerate(model.model.exog_names):
        coef_table.append(
            f"| {name} | {model.params[i]:.4f} | {model.bse[i]:.4f} | "
            f"{model.tvalues[i]:.3f} | {model.pvalues[i]:.4f} |"
        )

    # Model diagnostics
    diagnostics = [
        "",
        "**Model Diagnostics:**",
        f"- R-squared: {model.rsquared:.4f}",
        f"- Adjusted R-squared: {model.rsquared_adj:.4f}",
        f"- F-statistic: {model.fvalue:.2f}",
        f"- Prob (F-statistic): {model.f_pvalue:.4e}",
        f"- AIC: {model.aic:.2f}",
        f"- BIC: {model.bic:.2f}",
        f"- Number of observations: {int(model.nobs)}",
    ]

    return "\n".join(coef_table + diagnostics)


def dataframe_to_markdown(df, float_format=".6e"):
    """Convert dataframe to markdown table with custom float formatting."""
    df_copy = df.copy()

    # Format float columns
    for col in df_copy.select_dtypes(include=[np.number]).columns:
        df_copy[col] = df_copy[col].apply(lambda x: f"{x:{float_format}}")

    return df_copy.to_markdown(index=False)


def compute_relative_diffference(df, column1, column2):
    """Compute summary statistics, optionally as relative difference."""
    values = (df[column1] - df[column2]) / np.abs(df[column1])
    label = f"{column1} vs {column2} (rel diff)"

    return {
        "metric": label,
        "mean": np.mean(values),
        "std": np.std(values),
        "min": np.min(values),
        "max": np.max(values),
    }


def create_summary_table(stats_list):
    """Create markdown table from list of summary statistics."""
    lines = []
    lines.append("| Metric | Mean | Std | Min | Max |")
    lines.append("|--------|------|-----|-----|-----|")

    for stats in stats_list:
        lines.append(
            f"| {stats['metric']} | {stats['mean']:.6e} | {stats['std']:.6e} | "
            f"{stats['min']:.6e} | {stats['max']:.6e} |"
        )

    return "\n".join(lines)


def render_optimisation_analysis_report(data_path, output_path=None):
    """
    Generate markdown report with tables and regression results.

    Usage:
        generate_analysis_report('optimal_sc_grids.pkl')
        generate_analysis_report('data.pkl', 'output/report.md')
    """
    # Load data
    print(f"Loading data from {data_path}...")
    data = load_data(data_path)

    # Create dataframe
    df = create_dataframe(
        data["grids"], data["informed fraction space"], data["price volatility space"]
    )

    # Fit model
    print("Fitting power law model...")
    model = fit_power_law_model(df)

    # Extract slices for fixed parameters
    fixed_if_df = df[
        ((df["informed fraction"] - 0.5).abs() < 1e-12)
        & ((df["price volatility"] * 1000).round() % 20 == 0)
    ][["price volatility", "optimal sc-returns", "average returns", "final pnl"]]

    fixed_pv_df = df[
        ((df["price volatility"] - 0.05).abs() < 1e-12)
        & ((df["informed fraction"] * 100).round() % 20 == 0)
    ][["informed fraction", "optimal sc-returns", "average returns", "final pnl"]]

    rel_diff_sc_msd = compute_relative_diffference(
        df, "optimal sc-returns", "optimal sc-msd"
    )
    rel_diff_sc_pnl = compute_relative_diffference(
        df, "optimal sc-returns", "optimal sc-pnl"
    )

    # Build report
    report = []
    report.append("# Optimal Skew Coefficient Analysis Report")
    report.append("")

    report.append("## Power Law Model")
    report.append("")
    report.append(
        "Fitting: log(optimal_sc) ~ const + β₁·log(informed_frac) + β₂·log(price_vol)"
    )
    report.append("")
    report.append(ols_summary_to_markdown(model))
    report.append("")

    report.append("## Summary Statistics")
    report.append("")
    summary_table = create_summary_table([rel_diff_sc_msd, rel_diff_sc_pnl])
    report.append(summary_table)
    report.append("")

    report.append("## Fixed Informed Fraction (0.5)")
    report.append("")
    report.append(dataframe_to_markdown(fixed_if_df))
    report.append("")

    report.append("## Fixed Price Volatility (0.05)")
    report.append("")
    report.append(dataframe_to_markdown(fixed_pv_df))
    report.append("")

    # Output report
    report_text = "\n".join(report)

    if output_path:
        print(f"Writing report to {output_path}...")
        with open(output_path, "w") as f:
            f.write(report_text)
        print("Report generation complete.")
    else:
        print("\n" + report_text)

    return {"model": model, "dataframe": df, "report_text": report_text}


def main():
    top_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    data_path = os.path.join(top_dir, "data/optimal_sc_grids.pkl")
    output_path = os.path.join(top_dir, "data/analysis_report.md")

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Data file not found at {data_path}. "
            "Please ensure 'optimal_sc_grids.pkl' exists in the script directory."
        )

    render_optimisation_analysis_report(data_path, output_path)


if __name__ == "__main__":
    main()
