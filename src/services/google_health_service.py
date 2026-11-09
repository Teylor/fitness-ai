"""Google Health synchronization service."""

from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.db.models import (
    Ingredient as IngredientModel,
    MealEntry as MealEntryModel,
    Recipe as RecipeModel,
    SleepLog,
    WeightLog,
)
from src.models.health import SleepRecord, WeightRecord
from src.services.google_health_client import GoogleHealthClient
from src.services.meal_service import MealService
from src.utils.errors import ValidationError


class GoogleHealthService:
    """Service to coordinate bidirectional Google Health API synchronization."""

    def __init__(
        self,
        client: Optional[GoogleHealthClient] = None,
        meal_service: Optional[MealService] = None,
    ):
        self.client = client or GoogleHealthClient()
        self.meal_service = meal_service or MealService()

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

    def sync_meals(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Upload meals recorded on a specific date to Google Health as nutrition dataPoints."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)
        iso_date = self._date_to_iso(valid_date)

        meal_rows = list(MealEntryModel.select().where(MealEntryModel.date == valid_date))
        if not meal_rows:
            return {
                "status": "ok",
                "date": valid_date,
                "synced_count": 0,
                "total_kcal": 0.0,
                "meals": [],
            }

        synced_meals = []
        total_kcal = 0.0

        for row in meal_rows:
            macros = self.meal_service._entry_macros(row)
            item_name = f"Meal #{row.id}"
            if row.item_type == "ingredient":
                ing = IngredientModel.get_or_none(IngredientModel.id == row.item_id)
                if ing:
                    item_name = ing.name
            elif row.item_type == "recipe":
                rec = RecipeModel.get_or_none(RecipeModel.id == row.item_id)
                if rec:
                    item_name = rec.name

            kcal = macros.get("kcal", 0.0)
            protein = macros.get("protein", 0.0)
            carbs = macros.get("carbs", 0.0)
            fat = macros.get("fat", 0.0)

            total_kcal += kcal
            datapoint = {
                "dataTypeName": "nutrition",
                "startTime": f"{iso_date}T12:00:00Z",
                "endTime": f"{iso_date}T12:30:00Z",
                "value": {
                    "meal_type": row.item_type,
                    "name": item_name,
                    "calories": kcal,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                    "quantity": row.quantity,
                    "unit": row.unit,
                },
            }
            self.client.post_nutrition_datapoint(datapoint)
            synced_meals.append({
                "meal_id": row.id,
                "name": item_name,
                "quantity": row.quantity,
                "unit": row.unit,
                "kcal": kcal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            })

        return {
            "status": "ok",
            "date": valid_date,
            "synced_count": len(synced_meals),
            "total_kcal": round(total_kcal, 2),
            "meals": synced_meals,
        }

    def fetch_sleep(self, date: Optional[str] = None, days: int = 1) -> Dict[str, Any]:
        """Fetch sleep sessions from Google Health and store them in sleep_logs."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)
        dt = datetime.strptime(valid_date, "%d-%m-%Y")
        start_iso = (dt - timedelta(days=days - 1)).strftime("%Y-%m-%dT00:00:00Z")
        end_iso = dt.strftime("%Y-%m-%dT23:59:59Z")

        raw_points = self.client.get_sleep_datapoints(start_time=start_iso, end_time=end_iso)
        saved_records: List[SleepRecord] = []

        for pt in raw_points:
            st = pt.get("startTime", f"{self._date_to_iso(valid_date)}T23:00:00Z")
            et = pt.get("endTime", f"{self._date_to_iso(valid_date)}T07:00:00Z")
            val = pt.get("value", {})
            duration = val.get("duration_minutes")
            if duration is None:
                try:
                    s_dt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                    e_dt = datetime.fromisoformat(et.replace("Z", "+00:00"))
                    duration = round((e_dt - s_dt).total_seconds() / 60.0, 1)
                except Exception:
                    duration = 480.0

            deep = float(val.get("deep_sleep_minutes", 0.0))
            rem = float(val.get("rem_sleep_minutes", 0.0))
            light = float(val.get("light_sleep_minutes", 0.0))

            log_date = valid_date
            try:
                log_dt = datetime.fromisoformat(et.replace("Z", "+00:00"))
                log_date = log_dt.strftime("%d-%m-%Y")
            except Exception:
                pass

            row, _ = SleepLog.get_or_create(
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

    def fetch_weight(self, date: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Fetch weight measurements from Google Health and store them in weight_logs."""
        self.client._ensure_authenticated()
        valid_date = self._parse_date(date)
        dt = datetime.strptime(valid_date, "%d-%m-%Y")
        start_iso = (dt - timedelta(days=days - 1)).strftime("%Y-%m-%dT00:00:00Z")
        end_iso = dt.strftime("%Y-%m-%dT23:59:59Z")

        raw_points = self.client.get_weight_datapoints(start_time=start_iso, end_time=end_iso)
        saved_records: List[WeightRecord] = []

        for pt in raw_points:
            ts = pt.get("startTime", f"{self._date_to_iso(valid_date)}T08:00:00Z")
            val = pt.get("value", {})
            weight_kg = float(val.get("weight_kg", val.get("value", 70.0)))
            bmi = val.get("bmi")
            body_fat = val.get("body_fat_pct")

            log_date = valid_date
            try:
                log_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                log_date = log_dt.strftime("%d-%m-%Y")
            except Exception:
                pass

            row = WeightLog.create(
                date=log_date,
                weight_kg=weight_kg,
                bmi=bmi,
                body_fat_pct=body_fat,
                source="google_health",
            )
            saved_records.append(
                WeightRecord(
                    id=row.id,
                    date=row.date,
                    weight_kg=row.weight_kg,
                    bmi=row.bmi,
                    body_fat_pct=row.body_fat_pct,
                    source=row.source,
                )
            )

        latest = saved_records[-1].weight_kg if saved_records else None

        return {
            "status": "ok",
            "date": valid_date,
            "count": len(saved_records),
            "latest_weight_kg": latest,
            "records": [asdict(r) for r in saved_records],
        }

    def sync_all(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Perform full bidirectional synchronization (push meals, pull sleep and weight)."""
        valid_date = self._parse_date(date)
        meals_res = self.sync_meals(valid_date)
        sleep_res = self.fetch_sleep(valid_date)
        weight_res = self.fetch_weight(valid_date)

        return {
            "status": "ok",
            "date": valid_date,
            "meals_synced": meals_res["synced_count"],
            "total_kcal_synced": meals_res["total_kcal"],
            "sleep_sessions_fetched": sleep_res["count"],
            "weight_records_fetched": weight_res["count"],
            "latest_weight_kg": weight_res["latest_weight_kg"],
        }
