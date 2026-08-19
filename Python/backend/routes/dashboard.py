from typing import Optional

from fastapi import APIRouter, Query

from .. import filtering, state
from ..analytics import charts, kpis, leaderboard

router = APIRouter()


@router.get("/api/dashboard")
def dashboard(
    makes: Optional[str] = Query(default=None),
    year_min: Optional[int] = Query(default=None),
    year_max: Optional[int] = Query(default=None),
    fuel_types: Optional[str] = Query(default=None),
):
    filtered_df = filtering.apply_filters(
        state.get_df(),
        makes=filtering.parse_list_param(makes),
        year_min=year_min,
        year_max=year_max,
        fuel_types=filtering.parse_list_param(fuel_types),
    )
    return {
        "kpis": kpis.compute_kpis(filtered_df),
        "charts": {
            "hp_mpg": charts.build_hp_mpg_chart(filtered_df),
            "mpg_by_style": charts.build_mpg_by_style_chart(filtered_df),
            "hp_msrp": charts.build_hp_msrp_chart(filtered_df),
            "year_trends": charts.build_year_trend_charts(filtered_df),
        },
        "leaderboard": leaderboard.compute_leaderboard(filtered_df),
    }
