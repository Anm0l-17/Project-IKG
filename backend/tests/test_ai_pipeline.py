from app.ai.embeddings import embedding_service
from app.ai.matching import candidate_matching_service
from app.ai.ner import entity_extraction_service
from app.models.article import Article
from app.models.event import Event


def test_embedding_service_generation_and_similarity():
    text1 = "Union Cabinet approves Semiconductor Mission in India"
    text2 = "Cabinet approves Semiconductor Mission in India today"
    text3 = "IPL Cricket tournament scheduled in Mumbai"

    vec1 = embedding_service.generate_embedding(text1)
    vec2 = embedding_service.generate_embedding(text2)
    vec3 = embedding_service.generate_embedding(text3)

    assert len(vec1) == 384
    assert len(vec2) == 384
    assert len(vec3) == 384

    sim_12 = embedding_service.cosine_similarity(vec1, vec2)
    sim_13 = embedding_service.cosine_similarity(vec1, vec3)

    # Similar text should have higher cosine similarity than unrelated text
    assert sim_12 > sim_13
    assert sim_12 >= 0.70


def test_entity_extraction_service():
    sample_text = "The Ministry of Education introduced the National Education Policy Bill in Delhi with ISRO support."
    entities = entity_extraction_service.extract_entities(sample_text)

    entity_names = [e.canonical_name for e in entities]
    entity_types = [e.entity_type for e in entities]

    assert "Ministry of Education" in entity_names
    assert "National Education Policy Bill" in entity_names
    assert "Delhi" in entity_names
    assert "ISRO" in entity_names

    assert "Ministry" in entity_types
    assert "Bill" in entity_types
    assert "State" in entity_types
    assert "Organization" in entity_types


def test_candidate_matching_service_cascade():
    article = Article(
        headline="Ministry of Defense approves new submarine project",
        summary="Defense Ministry has cleared a major submarine procurement scheme for Indian Navy.",
    )

    event1 = Event(
        canonical_title="Ministry of Defense approves new submarine project",
        summary="Defense Ministry has cleared a major submarine procurement scheme for Indian Navy.",
    )

    event2 = Event(
        canonical_title="Weather forecast for Mumbai coastal areas",
        summary="Heavy rain forecast for Konkan region.",
    )

    match_result = candidate_matching_service.match_article_to_events(
        article, [event1, event2]
    )

    assert match_result.is_match is True
    assert match_result.event == event1
    assert match_result.similarity_score > 0.70
    assert match_result.stage in (
        "STAGE1_VECTOR",
        "STAGE2_CROSS_ENCODER",
        "FUZZY_FALLBACK",
    )
