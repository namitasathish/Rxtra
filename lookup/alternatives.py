import requests

def get_alternatives(medicine_name: str) -> list[str]:
    """
    Returns list of brand-name alternatives using RxNav API.
    """
    try:
        # Step 1: Fetch RxCUI (RxNorm Concept ID)
        r1 = requests.get(
            "https://rxnav.nlm.nih.gov/REST/rxcui.json",
            params={"name": medicine_name},
            timeout=5
        )
        data1 = r1.json()
        rxcui = data1.get("idGroup", {}).get("rxnormId", [])
        if not rxcui:
            return ["No alternatives found (RxCUI not found)"]
        rxcui = rxcui[0]

        # Step 2: Fetch branded names (relationship type BN)
        r2 = requests.get(
            "https://rxnav.nlm.nih.gov/REST/rxcui/{}/related.json".format(rxcui),
            params={"tty": "BN"},
            timeout=5
        )
        data2 = r2.json()
        groups = data2.get("relatedGroup", {}).get("conceptGroup", [])
        names = []
        for grp in groups:
            for concept in grp.get("conceptProperties", []):
                names.append(concept.get("name"))

        return names or ["No branded alternatives found"]
    except Exception as e:
        return [f"Error fetching alternatives: {str(e)}"]
