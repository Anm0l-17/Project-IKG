import logging
import re
from typing import ClassVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractedEntityDTO(BaseModel):
    canonical_name: str
    entity_type: str
    confidence: float = 1.0


class EntityExtractionService:
    """
    Named Entity Recognition (NER) Service for extracting Indian ministries,
    bills, acts, states, persons, and organizations.
    """

    INDIAN_STATES: ClassVar[tuple[str, ...]] = (
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Delhi",
    )

    ORGANIZATIONS: ClassVar[tuple[str, ...]] = (
        "ISRO",
        "DRDO",
        "RBI",
        "SEBI",
        "NITI Aayog",
        "Supreme Court",
        "High Court",
        "Parliament",
        "Lok Sabha",
        "Rajya Sabha",
        "Cabinet",
    )

    def __init__(self):
        self.nlp = None
        try:
            import spacy

            self.nlp = spacy.load("en_core_web_sm")
        except (ImportError, OSError, RuntimeError):
            self.nlp = None

    def extract_entities(self, text: str) -> list[ExtractedEntityDTO]:
        entities: dict[str, ExtractedEntityDTO] = {}

        if not text:
            return []

        # 1. Ministry Pattern Matching: "Ministry of [Words]"
        for match in re.finditer(r"(Ministry of [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text):
            name = match.group(1).strip()
            entities[name] = ExtractedEntityDTO(
                canonical_name=name, entity_type="Ministry", confidence=0.95
            )

        # 2. Bill / Act Pattern Matching: "[Words] Bill/Act"
        for match in re.finditer(
            r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s(?:Bill|Act))", text
        ):
            name = match.group(1).strip()
            etype = "Act" if "Act" in name else "Bill"
            entities[name] = ExtractedEntityDTO(
                canonical_name=name, entity_type=etype, confidence=0.90
            )

        # 3. Indian States Taxonomy
        for state in self.INDIAN_STATES:
            if re.search(r"\b" + re.escape(state) + r"\b", text):
                entities[state] = ExtractedEntityDTO(
                    canonical_name=state, entity_type="State", confidence=1.0
                )

        # 4. Known Institutions & Organizations
        for org in self.ORGANIZATIONS:
            if re.search(r"\b" + re.escape(org) + r"\b", text):
                entities[org] = ExtractedEntityDTO(
                    canonical_name=org, entity_type="Organization", confidence=0.95
                )

        # 5. spaCy Model Extraction (if available)
        if self.nlp is not None:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ("PERSON", "ORG", "GPE"):
                        name = ent.text.strip()
                        if len(name) > 2 and name not in entities:
                            etype = {
                                "PERSON": "Person",
                                "ORG": "Organization",
                                "GPE": "Location",
                            }[ent.label_]
                            entities[name] = ExtractedEntityDTO(
                                canonical_name=name, entity_type=etype, confidence=0.85
                            )
            except (AttributeError, KeyError, RuntimeError, TypeError) as error:
                logger.warning("spaCy entity extraction failed: %s", error)

        return list(entities.values())


entity_extraction_service = EntityExtractionService()
