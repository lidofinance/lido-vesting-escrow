import brownie


def test_delegate(deployed_vesting, recipient, voting_adapter):
    data = voting_adapter.encode_delegate_calldata(recipient)
    with brownie.reverts("not implemented"):
        deployed_vesting.delegate(data, {"from": recipient})


def test_vote_after_upgrade(
    deployed_vesting, recipient, voting_adapter_for_update, vesting_factory, owner, voting_adapter
):
    vesting_factory.update_voting_adapter(voting_adapter_for_update, {"from": owner})
    data = voting_adapter.encode_delegate_calldata(recipient)
    with brownie.reverts("not implemented"):
        deployed_vesting.delegate(data, {"from": recipient})


def test_delegate_from_not_recipient_fail(deployed_vesting, not_recipient, voting_adapter):
    data = voting_adapter.encode_delegate_calldata(not_recipient)
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.delegate(data, {"from": not_recipient})
