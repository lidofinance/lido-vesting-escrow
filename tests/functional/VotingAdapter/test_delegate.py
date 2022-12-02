import brownie


def test_delegate(voting_adapter, recipient):
    with brownie.reverts("not implemented"):
        tx = voting_adapter.delegate(recipient, {"from": recipient})
