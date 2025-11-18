Display PnL
    pnl = path_data["mark-to-market"]
    pnl_df = pnl.explode().reset_index()
    pnl_df.columns = ["tick", "mark to market"]
    sns.lineplot(
        pnl_df,
        x="tick",
        y="mark to market",
        color="blue",
    )