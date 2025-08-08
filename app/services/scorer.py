import re
from fuzzywuzzy import fuzz
from typing import List, Tuple


SKILL_PATTERN = re.compile(r"\b[A-Za-z0-9\+\#\.\-]{2,}\b")


def extract_skills(text: str) -> List[str]:
    # crude keyword extraction (can replace with NER later)
    words = set(SKILL_PATTERN.findall(text))
    return sorted(words, key=lambda x: x.lower())


def match_skills(
    jd_skills: List[str], resume_skills: List[str]
) -> Tuple[List[str], List[str], int]:
    strengths = []
    missing = []

    for skill in jd_skills:
        matched = any(
            fuzz.partial_ratio(skill.lower(), r.lower()) > 80 for r in resume_skills
        )
        if matched:
            strengths.append(skill)
        else:
            missing.append(skill)

    match_score = round(100 * len(strengths) / max(len(jd_skills), 1))
    return strengths, missing, match_score
