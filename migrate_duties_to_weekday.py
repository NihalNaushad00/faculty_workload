#!/usr/bin/env python3
"""
Add duty_day to existing duties and backfill it from the start date weekday.
"""

from sqlalchemy import text

from app import create_app, db
from app.models import AdditionalDuty

app = create_app()


def normalize_duty_day(date_value):
    weekday = date_value.strftime('%A')
    if weekday in {'Saturday', 'Sunday'}:
        return 'Monday'
    return weekday


def ensure_duty_day_column():
    columns = db.session.execute(text("PRAGMA table_info(additional_duty)")).fetchall()
    column_names = {column[1] for column in columns}

    if 'duty_day' not in column_names:
        db.session.execute(text("ALTER TABLE additional_duty ADD COLUMN duty_day VARCHAR(20)"))
        db.session.commit()


def migrate():
    with app.app_context():
        print("=" * 70)
        print("DUTY WEEKDAY MIGRATION")
        print("=" * 70)

        ensure_duty_day_column()
        updated = 0

        duties = AdditionalDuty.query.order_by(AdditionalDuty.id).all()
        for duty in duties:
            normalized_day = normalize_duty_day(duty.start_date)
            if duty.duty_day == normalized_day:
                continue

            duty.duty_day = normalized_day
            updated += 1

        db.session.commit()

        print(f"Updated duties: {updated}")
        print("=" * 70)


if __name__ == '__main__':
    migrate()
