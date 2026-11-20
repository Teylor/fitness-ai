"""Body Progress domain service."""

from datetime import datetime
from typing import Any, List, Optional

from src.db.models import BodyProgressLog as BodyProgressLogModel
from src.models.body_progress import BodyProgressRecord
from src.utils.errors import NotFoundError, ValidationError


class BodyProgressService:
    """CRUD and monthly listing for daily body progress measurements."""

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            parsed = datetime.strptime(value, "%d-%m-%Y")
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                f"invalid date '{value}' (expected DD-MM-YYYY)"
            ) from exc
        if parsed.strftime("%d-%m-%Y") != value:
            raise ValidationError(f"invalid date '{value}' (expected DD-MM-YYYY)")
        return parsed

    @staticmethod
    def _parse_month(value: str) -> tuple[int, int]:
        try:
            parsed = datetime.strptime(value, "%Y-%m")
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                f"invalid month '{value}' (expected YYYY-MM)"
            ) from exc
        if parsed.strftime("%Y-%m") != value:
            raise ValidationError(f"invalid month '{value}' (expected YYYY-MM)")
        return parsed.year, parsed.month

    @staticmethod
    def _parse_metric(name: str, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            num = float(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"invalid numeric value for '{name}'") from exc
        if num <= 0:
            raise ValidationError(f"'{name}' must be greater than 0")
        return round(num, 2)

    @staticmethod
    def _to_domain(row) -> BodyProgressRecord:
        return BodyProgressRecord(
            id=row.id,
            date=row.date,
            weight_kg=row.weight_kg,
            waist_cm=row.waist_cm,
            chest_cm=row.chest_cm,
            arm_cm=row.arm_cm,
            leg_cm=row.leg_cm,
            notes=row.notes,
            created_at=str(row.created_at) if row.created_at is not None else None,
            updated_at=str(row.updated_at) if row.updated_at is not None else None,
        )

    def log_progress(
        self,
        date: Optional[str] = None,
        weight_kg: Optional[float] = None,
        waist_cm: Optional[float] = None,
        chest_cm: Optional[float] = None,
        arm_cm: Optional[float] = None,
        leg_cm: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> BodyProgressRecord:
        """Create or update (upsert) a body progress entry for a given date."""
        target_date = date.strip() if isinstance(date, str) and date.strip() else datetime.now().strftime("%d-%m-%Y")
        self._parse_date(target_date)

        parsed_weight = self._parse_metric("weight_kg", weight_kg)
        parsed_waist = self._parse_metric("waist_cm", waist_cm)
        parsed_chest = self._parse_metric("chest_cm", chest_cm)
        parsed_arm = self._parse_metric("arm_cm", arm_cm)
        parsed_leg = self._parse_metric("leg_cm", leg_cm)

        if all(
            v is None
            for v in (parsed_weight, parsed_waist, parsed_chest, parsed_arm, parsed_leg)
        ):
            raise ValidationError(
                "at least one measurement (weight_kg, waist_cm, chest_cm, arm_cm, leg_cm) is required"
            )

        clean_notes = notes.strip() if isinstance(notes, str) and notes.strip() else None
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with BodyProgressLogModel._meta.database.atomic():
            row = BodyProgressLogModel.get_or_none(
                BodyProgressLogModel.date == target_date
            )
            if row is None:
                row = BodyProgressLogModel.create(
                    date=target_date,
                    weight_kg=parsed_weight,
                    waist_cm=parsed_waist,
                    chest_cm=parsed_chest,
                    arm_cm=parsed_arm,
                    leg_cm=parsed_leg,
                    notes=clean_notes,
                )
            else:
                row.weight_kg = parsed_weight
                row.waist_cm = parsed_waist
                row.chest_cm = parsed_chest
                row.arm_cm = parsed_arm
                row.leg_cm = parsed_leg
                row.notes = clean_notes
                row.updated_at = now_str
                row.save()

        return self._to_domain(row)

    def get_by_date(self, date: str) -> Optional[BodyProgressRecord]:
        """Return the body progress record for a specific date, or None."""
        self._parse_date(date)
        row = BodyProgressLogModel.get_or_none(BodyProgressLogModel.date == date)
        return None if row is None else self._to_domain(row)

    def list_progress(self, month: Optional[str] = None) -> List[BodyProgressRecord]:
        """List body progress records ordered chronologically ascending.

        Args:
            month: Optional YYYY-MM filter (e.g. '2026-11').
        """
        filter_ym = self._parse_month(month) if month else None
        entries: List[tuple[datetime, BodyProgressRecord]] = []
        for row in BodyProgressLogModel.select():
            dt = self._parse_date(row.date)
            if filter_ym and (dt.year, dt.month) != filter_ym:
                continue
            entries.append((dt, self._to_domain(row)))
        entries.sort(key=lambda item: item[0])
        return [record for _, record in entries]

    def delete_progress(self, progress_id: int) -> bool:
        """Delete a body progress record by id. Raises NotFoundError if absent."""
        row = BodyProgressLogModel.get_or_none(BodyProgressLogModel.id == progress_id)
        if row is None:
            raise NotFoundError(f"body progress id {progress_id} not found")
        row.delete_instance()
        return True
