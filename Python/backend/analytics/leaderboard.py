def compute_leaderboard(filtered_df):
    leaderboard_df = filtered_df[filtered_df["engine_hp"] > 0].copy()
    leaderboard_df["efficiency_score"] = (leaderboard_df["highway_mpg"] / (leaderboard_df["engine_hp"] / 100)).round(2)
    leaderboard_df = leaderboard_df.sort_values("efficiency_score", ascending=False).head(10)
    return [
        {
            "make": row["make"],
            "model": row["model"],
            "year": int(row["year"]),
            "engine_hp": float(row["engine_hp"]),
            "highway_mpg": float(row["highway_mpg"]),
            "efficiency_score": float(row["efficiency_score"]),
        }
        for _, row in leaderboard_df.iterrows()
    ]
