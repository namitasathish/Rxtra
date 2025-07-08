import re

def parse_prescription(text: str) -> dict:
    # Simple regex-based parsing
    med_match = re.search(r"([A-Za-z]+)", text)
    dose_match = re.search(r"(\d+)\s*mg", text)
    freq_match = re.search(r"(\d+)[×x]\s*/\s*day", text, re.IGNORECASE)
    dur_match = re.search(r"for\s*(\d+)\s*days", text, re.IGNORECASE)

    return {
        "medicine": med_match.group(1) if med_match else "",
        "dosage_mg": int(dose_match.group(1)) if dose_match else 0,
        "frequency_per_day": int(freq_match.group(1)) if freq_match else 1,
        "duration_days": int(dur_match.group(1)) if dur_match else 1,
        "quantity": int(dur_match.group(1)) if dur_match else 1
    }
