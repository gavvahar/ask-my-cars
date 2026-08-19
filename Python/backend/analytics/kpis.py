def compute_kpis(filtered_df):
    count = len(filtered_df)
    avg_mpg = f"{filtered_df['highway_mpg'].mean():.1f}" if count else None
    avg_hp = f"{filtered_df['engine_hp'].mean():.1f}" if count else None
    return {"count": count, "avg_mpg": avg_mpg, "avg_hp": avg_hp}
