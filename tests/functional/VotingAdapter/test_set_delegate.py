def test_snapshot_set_delegate(voting_adapter, recipient):
    data = voting_adapter.encode_snapshot_set_delegate_calldata(recipient)
    tx = voting_adapter.snapshot_set_delegate(data, {"from": recipient})
    assert len(tx.events) == 1
