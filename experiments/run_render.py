import os
from experiments.simulations.src.render import (
    render_optimisation_analysis_report,
    render_optimisation_figures,
    render_trajectory_figures,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "experiments", "simulations", "data")
OUTPUT_DIR = os.path.join(REPO_ROOT, "experiments", "simulations", "outputs")


def main():
    single_data_path = os.path.join(DATA_DIR, "single_trajectory.pkl")
    comparison_data_path = os.path.join(DATA_DIR, "trajectory_comparison.pkl")
    optimal_data_path = os.path.join(DATA_DIR, "optimal_grids.pkl")
    optimality_data_path = os.path.join(DATA_DIR, "optimality_loss.pkl")

    fig_output_dir = os.path.join(OUTPUT_DIR, "figures")
    md_output_path = os.path.join(OUTPUT_DIR, "optimisation_analysis_report.md")

    render_trajectory_figures(
        comparison_data_path, single_data_path, output_dir=fig_output_dir
    )
    render_optimisation_figures(
        optimal_data_path, optimality_data_path, output_dir=fig_output_dir
    )
    render_optimisation_analysis_report(
        optimal_data_path, optimality_data_path, output_path=md_output_path
    )


if __name__ == "__main__":
    main()
