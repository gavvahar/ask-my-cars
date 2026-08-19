from typing import Optional

import anthropic
from fastapi import APIRouter, HTTPException, Query

from .. import ai_summary, filtering, state

router = APIRouter()


@router.post("/api/ai-summary")
def ai_summary_route(
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
    if filtered_df.empty:
        raise HTTPException(status_code=400, detail="No cars match these filters.")

    try:
        summary = ai_summary.generate_summary(filtered_df)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (anthropic.APIError, ConnectionError) as e:
        raise HTTPException(status_code=502, detail="The AI summary service is unavailable right now.") from e

    return {"summary": summary}
