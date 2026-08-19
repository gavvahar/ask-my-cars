from fastapi import APIRouter

from .. import filtering, state

router = APIRouter()


@router.get("/api/filters/options")
def filter_options():
    return filtering.get_filter_options(state.get_df())
