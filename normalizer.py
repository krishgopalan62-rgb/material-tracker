# normalizer.py
# Maps raw supplier product descriptions to standardized names and categories.
# Uses keyword matching so slight naming variations all resolve to the same standard name.
# To add a new material: copy the closest existing block and adjust the keywords and return values.

def normalize(raw_description: str):
    """
    Input:  a raw string from a supplier website, e.g. "2X4X8 KD SPF Stud"
    Output: a tuple of (standard_name, category), e.g. ("2x4x8 Stud", "Lumber")
    """
    d = raw_description.strip().lower()

    # ── LUMBER ────────────────────────────────────────────────────────────────
    if "2x4" in d or "2 x 4" in d:
        if ("x8" in d or "8ft" in d or "8 ft" in d or "8'" in d) and "10" not in d and "12" not in d:
            return ("2x4x8 Stud", "Lumber")
        elif "x10" in d or "10ft" in d or "10'" in d:
            return ("2x4x10 Stud", "Lumber")
        elif "x12" in d or "12ft" in d or "12'" in d:
            return ("2x4x12 Stud", "Lumber")
        else:
            return ("2x4 Stud (length unspecified)", "Lumber")

    if "2x6" in d or "2 x 6" in d:
        if ("x8" in d or "8ft" in d or "8'" in d) and "10" not in d and "12" not in d:
            return ("2x6x8", "Lumber")
        elif "x10" in d or "10ft" in d or "10'" in d:
            return ("2x6x10", "Lumber")
        elif "x12" in d or "12ft" in d or "12'" in d:
            return ("2x6x12", "Lumber")
        else:
            return ("2x6 (length unspecified)", "Lumber")

    if "2x8" in d or "2 x 8" in d:
        return ("2x8 Lumber", "Lumber")

    if "lsl" in d or "laminated strand" in d:
        return ("LSL Rim Board", "Lumber")

    # ── SHEET GOODS ───────────────────────────────────────────────────────────
    if ("3/4" in d or ".75" in d) and ("ply" in d or "plywood" in d):
        return ('3/4" Plywood 4x8', "Sheet Goods")

    if ("1/2" in d) and ("ply" in d or "plywood" in d):
        return ('1/2" Plywood 4x8', "Sheet Goods")

    if "osb" in d and ("7/16" in d or ".4375" in d):
        return ('7/16" OSB 4x8', "Sheet Goods")

    if "osb" in d and "5/8" in d:
        return ('5/8" OSB 4x8', "Sheet Goods")

    # ── DRYWALL ───────────────────────────────────────────────────────────────
    if "drywall" in d or "gypsum" in d or "gyp bd" in d:
        if "5/8" in d and ("type x" in d or "type-x" in d or "x type" in d):
            return ('5/8" Type X Drywall 4x8', "Drywall")
        elif "5/8" in d:
            return ('5/8" Drywall 4x8', "Drywall")
        elif "1/2" in d:
            return ('1/2" Drywall 4x8', "Drywall")
        else:
            return ("Drywall (size unspecified)", "Drywall")

    # ── CONCRETE & REBAR ──────────────────────────────────────────────────────
    if "25mpa" in d or "25 mpa" in d:
        return ("Concrete 25MPa", "Concrete")

    if "30mpa" in d or "30 mpa" in d:
        return ("Concrete 30MPa", "Concrete")

    if "rebar" in d or "re-bar" in d or "reinforcing bar" in d:
        if "10m" in d or "#10" in d:
            return ("#10M Rebar", "Concrete")
        elif "15m" in d or "#15" in d:
            return ("#15M Rebar", "Concrete")
        elif "20m" in d or "#20" in d:
            return ("#20M Rebar", "Concrete")
        else:
            return ("Rebar (size unspecified)", "Concrete")

    # ── INSULATION ────────────────────────────────────────────────────────────
    if "batt" in d or "insulation" in d:
        if "r14" in d or "r-14" in d:
            return ("R-14 Batt Insulation", "Insulation")
        elif "r20" in d or "r-20" in d:
            return ("R-20 Batt Insulation", "Insulation")
        elif "r22" in d or "r-22" in d:
            return ("R-22 Batt Insulation", "Insulation")
        elif "r24" in d or "r-24" in d:
            return ("R-24 Batt Insulation", "Insulation")
        else:
            return ("Insulation (R-value unspecified)", "Insulation")

    # ── FASTENERS ─────────────────────────────────────────────────────────────
    if "nail" in d:
        return ("Nails (general)", "Fasteners")

    if "screw" in d and "drywall" not in d:
        return ("Screws (general)", "Fasteners")

    if "screw" in d and "drywall" in d:
        return ("Drywall Screws", "Fasteners")

    # ── DEFAULT ───────────────────────────────────────────────────────────────
    # If nothing matched, keep the raw description and flag as Uncategorized.
    # Review these rows in the dashboard and add matching rules above for recurring ones.
    return (raw_description, "Uncategorized")