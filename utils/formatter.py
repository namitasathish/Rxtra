def format_prescription_info(info: dict) -> str:
    return (f"{info['medicine']} — {info['dosage_mg']}mg, "
            f"{info['frequency_per_day']}×/day for {info['duration_days']} days")
