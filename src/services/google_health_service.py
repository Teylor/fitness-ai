"""Google Health synchronization service."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.db.models import (
    Ingredient as IngredientModel,
    MealEntry as MealEntryModel,
    Recipe as RecipeModel,
    SleepLog,
    StepLog,
    WeightLog,
)
from src.models.health import SleepRecord, StepRecord, WeightRecord
from src.services.body_progress_service import BodyProgressService
from src.services.google_health_client import GoogleHealthClient
from src.services.meal_service import MACRO_KEYS, MealService
from src.utils.errors import ValidationError
from src.utils.macros import calc_ingredient_macros


class GoogleHealthService:
    """Service to coordinate bidirectional Google Health API synchronization."""

    def __init__(
        self,
        client: Optional[GoogleHealthClient] = None,
        meal_service: Optional[MealService] = None,
        body_progress_service: Optional[BodyProgressService] = None,
    ):
        self.client = client or GoogleHealthClient()
        self.meal_service = meal_service or MealService()
        self.body_progress_service = body_progress_service or BodyProgressService()

    def _parse_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return datetime.now().strftime("%d-%m-%Y")
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return date_str
        except ValueError:
            raise ValidationError(
                f"invalid date '{date_str}' (expected DD-MM-YYYY format)"
            )

    def _date_to_iso(self, date_str: str) -> str:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d")

    def sync_meals(
        self,
        date: Optional[str] = None,
        raw_nutrition_points: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Upload meals recorded on a specific date to Google Health as nutrition-log dataPoints."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)
        iso_date = self._date_to_iso(valid_date)

        # Clear any existing Google Health nutrition datapoints for this date to avoid duplicates
        try:
            raw_points = (
                raw_nutrition_points
                if raw_nutrition_points is not None
                else self.client.get_nutrition_datapoints()
            )
            pts_to_delete = []
            for pt in raw_points:
                nlog = pt.get("nutritionLog", {}) or {}
                interval = nlog.get("interval", {}) or {}
                st = interval.get("startTime", "")
                if st.startswith(iso_date):
                    name = pt.get("name")
                    if not name and "dataPointId" in pt:
                        name = f"users/me/dataTypes/nutrition-log/dataPoints/{pt['dataPointId']}"
                    if name:
                        pts_to_delete.append(name)
            if pts_to_delete:
                self.client.batch_delete_datapoints("nutrition-log", pts_to_delete)
        except Exception:
            pass

        meal_rows = list(MealEntryModel.select().where(MealEntryModel.date == valid_date))
        if not meal_rows:
            return {
                "status": "ok",
                "date": valid_date,
                "synced_count": 0,
                "total_kcal": 0.0,
                "meals": [],
            }

        # Batch-prefetch ingredients and recipes to eliminate N+1 queries
        ing_ids = {r.item_id for r in meal_rows if r.item_type == "ingredient"}
        rec_ids = {r.item_id for r in meal_rows if r.item_type == "recipe"}
        ing_map = (
            {
                i.id: i
                for i in IngredientModel.select().where(IngredientModel.id.in_(ing_ids))
            }
            if ing_ids
            else {}
        )
        rec_map = (
            {
                r.id: r
                for r in RecipeModel.select().where(RecipeModel.id.in_(rec_ids))
            }
            if rec_ids
            else {}
        )

        meal_type_map = {
            "desayuno": ("BREAKFAST", "08:00:00Z", "08:30:00Z"),
            "tentempie": ("SNACK", "11:00:00Z", "11:30:00Z"),
            "comida": ("LUNCH", "14:00:00Z", "14:30:00Z"),
            "merienda": ("BEFORE_DINNER", "18:00:00Z", "18:30:00Z"),
            "cena": ("DINNER", "21:00:00Z", "21:30:00Z"),
        }

        synced_meals = []
        datapoints_to_post = []
        total_kcal = 0.0

        for row in meal_rows:
            item_name = f"Meal #{row.id}"
            is_supplement = False
            if row.item_type == "ingredient":
                ing = ing_map.get(row.item_id)
                if ing is not None:
                    item_name = ing.name
                    is_supplement = bool(getattr(ing, "is_supplement", False))
                    macros = calc_ingredient_macros(ing, row.quantity)
                else:
                    macros = self.meal_service._entry_macros(row)
                    item_name = macros.get("name", item_name)
                    is_supplement = bool(macros.get("is_supplement", False))
            elif row.item_type == "recipe":
                rec = rec_map.get(row.item_id)
                if rec is not None:
                    item_name = rec.name
                    macros = {
                        key: round((getattr(rec, key) or 0.0) * row.quantity, 2)
                        for key in MACRO_KEYS
                    }
                else:
                    macros = self.meal_service._entry_macros(row)
                    item_name = macros.get("name", item_name)
            else:
                macros = self.meal_service._entry_macros(row)

            kcal = float(macros.get("kcal", 0.0))
            protein = float(macros.get("protein", 0.0))
            carbs = float(macros.get("carbs", 0.0))
            fat = float(macros.get("fat", 0.0))

            # Skip zero-calorie/zero-macro supplements (e.g., Creatine) from nutrition-log
            if is_supplement and kcal == 0.0 and protein == 0.0 and carbs == 0.0 and fat == 0.0:
                continue

            meal_type_val = getattr(row, "meal_type", "tentempie") or "tentempie"
            gh_meal_type, start_time_suffix, end_time_suffix = meal_type_map.get(
                meal_type_val, ("SNACK", "12:00:00Z", "12:30:00Z")
            )

            total_kcal += kcal
            datapoint = {
                "nutritionLog": {
                    "interval": {
                        "startTime": f"{iso_date}T{start_time_suffix}",
                        "endTime": f"{iso_date}T{end_time_suffix}",
                    },
                    "foodDisplayName": item_name,
                    "mealType": gh_meal_type,
                    "energy": {
                        "kcal": round(kcal, 2),
                    },
                    "totalCarbohydrate": {
                        "grams": round(carbs, 2),
                    },
                    "totalFat": {
                        "grams": round(fat, 2),
                    },
                    "nutrients": [
                        {
                            "nutrient": "PROTEIN",
                            "quantity": {
                                "grams": round(protein, 2),
                            },
                        }
                    ],
                }
            }
            datapoints_to_post.append(datapoint)
            synced_meals.append({
                "meal_id": row.id,
                "name": item_name,
                "meal_type": meal_type_val,
                "quantity": row.quantity,
                "unit": row.unit,
                "kcal": kcal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            })

        if len(datapoints_to_post) == 1:
            self.client.post_nutrition_datapoint(datapoints_to_post[0])
        elif len(datapoints_to_post) > 1:
            with ThreadPoolExecutor(max_workers=min(4, len(datapoints_to_post))) as pool:
                list(pool.map(self.client.post_nutrition_datapoint, datapoints_to_post))

        return {
            "status": "ok",
            "date": valid_date,
            "synced_count": len(synced_meals),
            "total_kcal": round(total_kcal, 2),
            "meals": synced_meals,
        }

    def clear_nutrition_logs(self) -> Dict[str, Any]:
        """Fetch and remove all nutrition-log dataPoints from Google Health."""
        self.client._ensure_authenticated()
        raw_points = self.client.get_nutrition_datapoints()
        names = []
        for pt in raw_points:
            name = pt.get("name")
            if not name and "dataPointId" in pt:
                name = f"users/me/dataTypes/nutrition-log/dataPoints/{pt['dataPointId']}"
            if name:
                names.append(name)

        if names:
            self.client.batch_delete_datapoints("nutrition-log", names)

        return {"status": "ok", "deleted_count": len(names)}

    def fetch_sleep(
        self,
        date: Optional[str] = None,
        days: int = 1,
        raw_points: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Fetch sleep sessions from Google Health and store them in sleep_logs."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)

        if raw_points is None:
            raw_points = self.client.get_sleep_datapoints()
        saved_records: List[SleepRecord] = []

        for pt in raw_points:
            sleep = pt.get("sleep", {}) if isinstance(pt, dict) else {}
            interval = sleep.get("interval", {}) or {}
            st = interval.get("startTime", f"{self._date_to_iso(valid_date)}T23:00:00Z")
            et = interval.get("endTime", f"{self._date_to_iso(valid_date)}T07:00:00Z")

            deep = rem = light = 0.0
            duration: Optional[float] = None
            for stage in (sleep.get("summary") or {}).get("stagesSummary") or []:
                minutes = float(stage.get("minutes", 0) or 0)
                stage_type = (stage.get("type") or "").upper()
                if stage_type == "DEEP":
                    deep += minutes
                elif stage_type == "REM":
                    rem += minutes
                elif stage_type == "LIGHT":
                    light += minutes

            summary = sleep.get("summary") or {}
            if summary:
                duration = float(summary.get("minutesAsleep", 0) or 0)
            if duration is None or duration <= 0:
                try:
                    s_dt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                    e_dt = datetime.fromisoformat(et.replace("Z", "+00:00"))
                    duration = round((e_dt - s_dt).total_seconds() / 60.0, 1)
                except Exception:
                    duration = 480.0

            log_date = valid_date
            try:
                log_dt = datetime.fromisoformat(et.replace("Z", "+00:00"))
                log_date = log_dt.strftime("%d-%m-%Y")
            except Exception:
                pass

            row, created = SleepLog.get_or_create(
                date=log_date,
                start_time=st,
                defaults={
                    "end_time": et,
                    "duration_minutes": duration,
                    "deep_sleep_minutes": deep,
                    "rem_sleep_minutes": rem,
                    "light_sleep_minutes": light,
                    "source": "google_health",
                },
            )
            if not created and (
                row.end_time != et
                or row.duration_minutes != duration
                or row.deep_sleep_minutes != deep
                or row.rem_sleep_minutes != rem
                or row.light_sleep_minutes != light
            ):
                row.end_time = et
                row.duration_minutes = duration
                row.deep_sleep_minutes = deep
                row.rem_sleep_minutes = rem
                row.light_sleep_minutes = light
                row.save()
            saved_records.append(
                SleepRecord(
                    id=row.id,
                    date=row.date,
                    start_time=row.start_time,
                    end_time=row.end_time,
                    duration_minutes=row.duration_minutes,
                    deep_sleep_minutes=row.deep_sleep_minutes,
                    rem_sleep_minutes=row.rem_sleep_minutes,
                    light_sleep_minutes=row.light_sleep_minutes,
                    source=row.source,
                )
            )

        return {
            "status": "ok",
            "date": valid_date,
            "count": len(saved_records),
            "records": [asdict(r) for r in saved_records],
        }

    @staticmethod
    def _to_weight_record(row: WeightLog) -> WeightRecord:
        return WeightRecord(
            id=row.id,
            date=row.date,
            weight_kg=row.weight_kg,
            bmi=row.bmi,
            body_fat_pct=row.body_fat_pct,
            source=row.source,
        )

    def fetch_weight(
        self,
        date: Optional[str] = None,
        days: int = 7,
        raw_points: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Fetch weight measurements from Google Health and store them in weight_logs."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)

        if raw_points is None:
            raw_points = self.client.get_weight_datapoints()
        saved_records: List[WeightRecord] = []

        for pt in raw_points:
            weight = pt.get("weight", {}) if isinstance(pt, dict) else {}
            sample = weight.get("sampleTime") or {}
            ts = sample.get("physicalTime") or f"{self._date_to_iso(valid_date)}T08:00:00Z"
            weight_kg = round(float(weight.get("weightGrams", 0) or 0) / 1000.0, 2)
            bmi = None
            body_fat = None

            log_date = valid_date
            try:
                log_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                log_date = log_dt.strftime("%d-%m-%Y")
            except Exception:
                pass

            exists = WeightLog.get_or_none(
                (WeightLog.date == log_date) & (WeightLog.source == "google_health")
            )
            if exists is not None:
                if weight_kg > 0 and exists.weight_kg != weight_kg:
                    exists.weight_kg = weight_kg
                    exists.save()
                    self.body_progress_service.sync_weight_from_google_health(
                        log_date, weight_kg
                    )
                    saved_records.append(self._to_weight_record(exists))
                elif log_date == valid_date and exists.weight_kg > 0:
                    existing_bp = self.body_progress_service.get_by_date(log_date)
                    if existing_bp is None or existing_bp.weight_kg is None:
                        self.body_progress_service.sync_weight_from_google_health(
                            log_date, exists.weight_kg
                        )
                continue

            row = WeightLog.create(
                date=log_date,
                weight_kg=weight_kg,
                bmi=bmi,
                body_fat_pct=body_fat,
                source="google_health",
            )
            if weight_kg > 0:
                self.body_progress_service.sync_weight_from_google_health(
                    log_date, weight_kg
                )
            saved_records.append(self._to_weight_record(row))

        latest = saved_records[-1].weight_kg if saved_records else None

        return {
            "status": "ok",
            "date": valid_date,
            "count": len(saved_records),
            "latest_weight_kg": latest,
            "records": [asdict(r) for r in saved_records],
        }

    def fetch_steps(
        self,
        date: Optional[str] = None,
        days: int = 1,
        raw_points: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Fetch step count data from Google Health and store/update in step_logs."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)
        iso_date = self._date_to_iso(valid_date)

        if raw_points is None:
            raw_points = self.client.get_steps_datapoints()
        daily_steps: Dict[str, int] = {}

        for pt in raw_points:
            steps_obj = pt.get("steps", {}) if isinstance(pt, dict) else {}
            count_val = steps_obj.get("count", 0)
            if not count_val and "stepCount" in steps_obj:
                count_val = steps_obj.get("stepCount", 0)
            if not count_val and "count" in pt:
                count_val = pt.get("count", 0)
            try:
                count = int(count_val)
            except (ValueError, TypeError):
                count = 0

            interval = steps_obj.get("interval", {}) or pt.get("interval", {}) or {}
            civ_start = interval.get("civilStartTime")
            pt_date = None
            if isinstance(civ_start, dict) and isinstance(civ_start.get("date"), dict):
                d_obj = civ_start["date"]
                if d_obj.get("year") and d_obj.get("month") and d_obj.get("day"):
                    pt_date = (
                        f"{int(d_obj['day']):02d}-"
                        f"{int(d_obj['month']):02d}-"
                        f"{int(d_obj['year']):04d}"
                    )

            if not pt_date:
                st = (
                    interval.get("startTime")
                    or (civ_start if isinstance(civ_start, str) else None)
                    or f"{iso_date}T00:00:00Z"
                )
                pt_date = valid_date
                try:
                    clean_ts = st.replace("Z", "+00:00")
                    pt_dt = datetime.fromisoformat(clean_ts)
                    pt_date = pt_dt.strftime("%d-%m-%Y")
                except Exception:
                    if str(st).startswith(iso_date):
                        pt_date = valid_date

            daily_steps[pt_date] = daily_steps.get(pt_date, 0) + count

        total_steps_for_date = daily_steps.get(valid_date, 0)

        # Update or create row for valid_date
        row, created = StepLog.get_or_create(
            date=valid_date,
            defaults={
                "steps": total_steps_for_date,
                "source": "google_health",
            },
        )
        if not created and (row.steps != total_steps_for_date or row.source != "google_health"):
            row.steps = total_steps_for_date
            row.source = "google_health"
            row.save()

        # Also persist other dates if found in the retrieved data points
        for d, st_count in daily_steps.items():
            if d != valid_date:
                other_row, other_created = StepLog.get_or_create(
                    date=d,
                    defaults={
                        "steps": st_count,
                        "source": "google_health",
                    },
                )
                if not other_created and (
                    other_row.steps != st_count or other_row.source != "google_health"
                ):
                    other_row.steps = st_count
                    other_row.source = "google_health"
                    other_row.save()

        return {
            "status": "ok",
            "date": valid_date,
            "steps": total_steps_for_date,
            "source": "google_health",
        }

    def sync_all(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Perform full bidirectional synchronization (push meals, pull sleep, weight, and steps)."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)

        def _safe_get_nutrition() -> Optional[List[Dict[str, Any]]]:
            try:
                return self.client.get_nutrition_datapoints()
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=4) as pool:
            fut_nutrition = pool.submit(_safe_get_nutrition)
            fut_sleep = pool.submit(self.client.get_sleep_datapoints)
            fut_weight = pool.submit(self.client.get_weight_datapoints)
            fut_steps = pool.submit(self.client.get_steps_datapoints)

            raw_nutrition = fut_nutrition.result()
            raw_sleep = fut_sleep.result()
            raw_weight = fut_weight.result()
            raw_steps = fut_steps.result()

        meals_res = self.sync_meals(valid_date, raw_nutrition_points=raw_nutrition)
        sleep_res = self.fetch_sleep(valid_date, raw_points=raw_sleep)
        weight_res = self.fetch_weight(valid_date, raw_points=raw_weight)
        steps_res = self.fetch_steps(valid_date, raw_points=raw_steps)

        return {
            "status": "ok",
            "date": valid_date,
            "meals_synced": meals_res["synced_count"],
            "total_kcal_synced": meals_res["total_kcal"],
            "sleep_sessions_fetched": sleep_res["count"],
            "weight_records_fetched": weight_res["count"],
            "latest_weight_kg": weight_res["latest_weight_kg"],
            "steps_fetched": steps_res["steps"],
        }
