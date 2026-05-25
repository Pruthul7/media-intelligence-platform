# processing/models/entities.py

import spacy
from loguru import logger

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        logger.info("Loading spaCy NER model...")
        _nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy loaded.")
    return _nlp


def extract_entities(text: str) -> dict:
    """
    Returns:
        {
          "organizations": ["Tesla", "SEC"],
          "people":        ["Elon Musk"],
          "locations":     ["California", "India"],
        }
    """
    if not text or len(text.strip()) < 5:
        return {"organizations": [], "people": [], "locations": []}
    try:
        nlp = get_nlp()
        doc = nlp(text[:1000])
        orgs      = list({e.text.strip() for e in doc.ents if e.label_ == "ORG"})
        people    = list({e.text.strip() for e in doc.ents if e.label_ == "PERSON"})
        locations = list({e.text.strip() for e in doc.ents if e.label_ in ("GPE", "LOC")})
        return {
            "organizations": orgs[:10],
            "people":        people[:10],
            "locations":     locations[:10],
        }
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        return {"organizations": [], "people": [], "locations": []}