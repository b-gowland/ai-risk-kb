from automation_engine import GapDetectionEngine


def test_gap_detection_uses_mdx_structure_without_false_positives(sample_mdx_path) -> None:
    detector = GapDetectionEngine()
    gaps = detector.check_entry(sample_mdx_path)

    controls_gaps = [gap for gap in gaps if "controls summary" in gap.description.lower()]
    layer_3_gaps = [gap for gap in gaps if gap.layer == "layer_3"]
    layer_4_gaps = [gap for gap in gaps if gap.layer == "layer_4"]
    incident_gaps = [gap for gap in gaps if gap.gap_type == "missing_incident"]

    assert not controls_gaps
    assert not layer_3_gaps
    assert not layer_4_gaps
    assert not incident_gaps


def test_gap_detection_entry_id_is_canonical(sample_mdx_path) -> None:
    detector = GapDetectionEngine()
    gaps = detector.check_entry(sample_mdx_path)

    assert all(gap.entry_id == "A1" for gap in gaps)
