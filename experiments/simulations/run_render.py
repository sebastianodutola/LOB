from src.render import (
    render_optimisation_analysis_report,
    render_optimisation_figures,
    render_trajectory_figures,
)

single_data_path = "data/single_trajectory.pkl"
comparison_data_path = "data/trajectory_comparison.pkl"
optimal_data_path = "data/optimal_grids.pkl"
optimality_data_path = "data/optimality_loss.pkl"

fig_output_dir = "outputs/figures"
md_output_path = "outputs/optimisation_analysis_report.md"

render_trajectory_figures(
    comparison_data_path, single_data_path, output_dir=fig_output_dir
)
render_optimisation_figures(
    optimal_data_path, optimality_data_path, output_dir=fig_output_dir
)
render_optimisation_analysis_report(
    optimal_data_path, optimality_data_path, output_path=md_output_path
)
