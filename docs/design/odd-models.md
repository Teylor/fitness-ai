# ODD Models

> Definition of entities, relationships, and business rules.

## Overview

### BodyProgressRecord (`body_progress_logs`)
- Daily body measurements entry (`date` unique `DD-MM-YYYY`): `weight_kg`, `waist_cm`, `chest_cm`, `arm_cm`, `leg_cm`, `notes`.
- Partial entries are allowed as long as at least one metric is provided (`> 0`). Re-logging on the same date updates the existing record.
