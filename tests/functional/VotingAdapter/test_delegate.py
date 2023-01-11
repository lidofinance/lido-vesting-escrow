import brownie


def test_delegate(voting_adapter, recipient):
    data = voting_adapter.encode_delegate_calldata(recipient)
    with brownie.reverts("not implemented"):
        voting_adapter.delegate(data, {"from": recipient})
