from information_flow.experiment import run_carrier_addressed_test


def test_carrier_addressing_survives_controls():
    result = run_carrier_addressed_test(n=24, train_steps=350, recall_steps=220)
    m = result["metrics"]
    assert abs(m["matched_isolated_routing"]) > 4.0 * abs(
        m["frequency_mismatch_control"]
    )
    assert abs(m["matched_isolated_routing"]) > 2.0 * abs(
        m["spatial_separation_control"]
    )
