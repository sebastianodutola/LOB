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


def create_dataframe_optimal_sc(grids, informed_frac_space, price_vol_space):
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


def create_dataframe_optimality_loss(OL_data):
    data = []
    ifs = OL_data["informed fraction space"]
    pvs = OL_data["price volatility space"]
    for i in range(len(ifs)):
        for j in range(len(pvs)):
            data.append(
                {
                    "informed fraction": ifs[i],
                    "price volatility": pvs[j],
                    "optimal returns": OL_data["optimal returns"][i, j],
                    "optimality loss absolute returns": OL_data[
                        "optimality loss absolute returns"
                    ][i, j],
                    "optimality loss returns": OL_data["optimality loss returns"][i, j],
                    "optimality loss msd": OL_data["optimality loss msd"][i, j],
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


def fit_extended_power_law_model(df):
    """Fit power law model with interaction term to optimal skew coefficients"""
    X = np.log(df[["informed fraction", "price volatility"]])
    X["lnIF * lnPV"] = X["informed fraction"] * X["price volatility"]
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


def compute_mult_difference(df, column1, column2):
    """Compute log difference"""
    values = np.exp(np.abs(np.log(df[column1]) - np.log(df[column2]))) - 1
    label = f"{column1} vs {column2} (log diff)"

    return {
        "metric": label,
        "median": np.median(values),
        "q10": np.quantile(values, 0.1),
        "q90": np.quantile(values, 0.9),
        "q75": np.quantile(values, 0.75),
        "q25": np.quantile(values, 0.25),
        "min": np.min(values),
        "max": np.max(values),
    }


def compute_ol_stats(df, column):
    """Compute summary stats for a given data frame column"""
    metric = f"{column}"
    values = df[column]
    return {
        "metric": metric,
        "median": np.median(values),
        "q10": np.quantile(values, 0.1),
        "q90": np.quantile(values, 0.9),
        "q75": np.quantile(values, 0.75),
        "q25": np.quantile(values, 0.25),
        "min": np.min(values),
        "max": np.max(values),
    }


def compute_ol_stats_with_mask(df, column, mask):
    """Compute summary stats for a given data frame column"""
    metric = f"{column}"
    values = df[column].to_numpy()
    values = np.ma.masked_array(values, mask).compressed()
    return {
        "metric": f"{metric} masked",
        "median": np.median(values),
        "q10": np.quantile(values, 0.1),
        "q90": np.quantile(values, 0.9),
        "q75": np.quantile(values, 0.75),
        "q25": np.quantile(values, 0.25),
        "min": np.min(values),
        "max": np.max(values),
    }


def create_summary_table(stats_list):
    """Create markdown table from list of summary statistics."""
    lines = []
    lines.append(
        "| Metric | Median | 10th Quantile | 25th Quantile | 75th Quantile | 90th Quantile | Min | Max |"
    )
    lines.append("|--------|------|-----|-----|-----|-----|-----|------|")

    for stats in stats_list:
        lines.append(
            f"| {stats['metric']} | {stats['median']:.6e} | {stats['q10']:.6e} | "
            f"{stats['q25']:.6e} | {stats['q75']:.6e} |"
            f"{stats['q90']:.6e} | {stats['min']:.6e} | {stats['max']:.6e}"
        )

    return "\n".join(lines)


def render_optimisation_analysis_report(
    data_path_optimal_grids, data_path_optimality_loss, output_path=None
):
    """
    Generate markdown report with tables and regression results.

    Usage:
        generate_analysis_report('optimal_sc_grids.pkl')
        generate_analysis_report('data.pkl', 'output/report.md')
    """
    # Load data
    print(f"Loading data from {data_path_optimal_grids} ...")
    optimal_sc_data = load_data(data_path_optimal_grids)
    print(f"Loading data from {data_path_optimality_loss} ...")
    optimality_loss_data = load_data(data_path_optimality_loss)

    # Create dataframes
    df_osc = create_dataframe_optimal_sc(
        optimal_sc_data["grids"],
        optimal_sc_data["informed fraction space"],
        optimal_sc_data["price volatility space"],
    )

    df_ol = create_dataframe_optimality_loss(optimality_loss_data)

    # Fit model
    print("Fitting power law model...")
    model = fit_power_law_model(df_osc)

    # Fit model with log(xy) interaction term
    print("Fitting adapted power law")
    model_ext = fit_extended_power_law_model(df_osc)

    # Extract slices for fixed parameters
    fixed_if_df = df_osc[
        ((df_osc["informed fraction"] - 0.5).abs() < 1e-12)
        & ((df_osc["price volatility"] * 1000).round() % 20 == 0)
    ][["price volatility", "optimal sc-returns", "average returns", "final pnl"]]

    fixed_pv_df = df_osc[
        ((df_osc["price volatility"] - 0.05).abs() < 1e-12)
        & ((df_osc["informed fraction"] * 100).round() % 20 == 0)
    ][["informed fraction", "optimal sc-returns", "average returns", "final pnl"]]

    mult_diff_sc_msd = compute_mult_difference(
        df_osc, "optimal sc-returns", "optimal sc-msd"
    )
    mult_diff_sc_pnl = compute_mult_difference(
        df_osc, "optimal sc-returns", "optimal sc-pnl"
    )

    optimality_loss_ret_abs = compute_ol_stats(
        df_ol, "optimality loss absolute returns"
    )

    optimality_loss_ret = compute_ol_stats(df_ol, "optimality loss returns")
    optimality_loss_msd = compute_ol_stats(df_ol, "optimality loss msd")

    # Masked array:
    threshold = 0.2 * np.median(df_ol[df_ol["optimal returns"] > 0]["optimal returns"])
    mask = (np.abs(df_ol["optimal returns"]) < threshold) | (
        df_ol["informed fraction"] < 0.2
    )
    optimality_loss_ret_masked = compute_ol_stats_with_mask(
        df_ol, "optimality loss returns", mask
    )

    # Build report
    report = []
    report.append("# Optimal Skew Coefficient Analysis Report")
    report.append("")

    report.append("## Power Law Model")
    report.append("")
    report.append(
        "Fitting: $\log(c^*) \sim a_0 + a_1 \cdot \log(informed\ frac) + a_2 \cdot \log(price\ vol)$"
    )
    report.append("")
    report.append(ols_summary_to_markdown(model))
    report.append("")

    report.append("## Power Law Model with Interaction Term")
    report.append("")
    report.append(
        "Fitting: $\log(c^*) \sim a_0 + a_1 \cdot \log(informed\ frac) + a_2 \cdot \log(price\ vol) + a_3 \cdot log(price\ vol) \cdot log(informed \ frac)$"
    )
    report.append(ols_summary_to_markdown(model_ext))
    report.append("")

    report.append("## Summary Statistics")
    report.append("")
    summary_table = create_summary_table(
        [
            mult_diff_sc_msd,
            mult_diff_sc_pnl,
            optimality_loss_ret_abs,
            optimality_loss_ret,
            optimality_loss_msd,
            optimality_loss_ret_masked,
        ]
    )
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

    return {
        "model": model,
        "optimality-loss dataframe": df_ol,
        "optimal-sc dataframe": df_osc,
        "report_text": report_text,
    }


def main():
    top_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    data_path_osg = os.path.join(top_dir, "data/optimal_sc_grids.pkl")
    data_path_ol = os.path.join(top_dir, "data/optimality_loss.pkl")
    output_path = os.path.join(top_dir, "data/analysis_report.md")

    if not os.path.exists(data_path_osg):
        raise FileNotFoundError(
            f"Data file not found at {data_path_osg}. "
            "Please ensure 'optimal_sc_grids.pkl' exists in the script directory."
        )
    if not os.path.exists(data_path_ol):
        raise FileNotFoundError(
            f"Data file not found at {data_path_ol}. "
            "Please ensure 'optimality_loss.pkl.pkl' exists in the script directory."
        )

    render_optimisation_analysis_report(data_path_osg, data_path_ol, output_path)


if __name__ == "__main__":
    main()
