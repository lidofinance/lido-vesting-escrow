

def test_delegate(voting_adapter, recipient):
    data = voting_adapter.encode_delegate_calldata(recipient)
    tx = voting_adapter.delegate(data, {"from": recipient})
    assert len(tx.events) == 1
