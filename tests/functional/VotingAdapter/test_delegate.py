def test_set_delegate(voting_adapter, recipient, delegate):
    tx = voting_adapter.set_delegate(delegate, recipient, {"from": recipient})
    assert len(tx.events) == 1
