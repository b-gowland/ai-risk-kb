from automation_engine import DOMAIN_SOURCE_MAP, MONITORING_SOURCES


def test_domain_source_map_keys_match_real_monitoring_source_names() -> None:
    source_names = {source["name"] for source in MONITORING_SOURCES}

    assert set(DOMAIN_SOURCE_MAP).issubset(source_names)
