from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, File, UploadFile, HTTPException

from ..services.raw_population_service import populate_two_dumps_raw

router = APIRouter()


def _temp(upload: UploadFile):
    suffix = Path(upload.filename or "").suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(upload.file, tmp)
        return tmp.name


@router.post("/monthly/populate-two-dumps")
def populate_two_dumps(incentive_dump: UploadFile = File(...), revenue_share_dump: UploadFile = File(...), period: str = ""):
    if not period:
        raise HTTPException(400, "period is required")
    inc_path = rs_path = None
    try:
        inc_path = _temp(incentive_dump)
        rs_path = _temp(revenue_share_dump)
        return populate_two_dumps_raw(inc_path, rs_path, period)
    except Exception as exc:
        raise HTTPException(500, f"Populate failed: {exc}") from exc
    finally:
        for path in (inc_path, rs_path):
            if path:
                Path(path).unlink(missing_ok=True)
