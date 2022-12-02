def test_snapshot_set_delegate(voting_adapter, recipient):
    tx = voting_adapter.snapshot_set_delegate(recipient, {"from": recipient})
    assert len(tx.events) == 1
