import brownie


def test_set_delegate(deployed_vesting, recipient, voting_adapter):
    data = voting_adapter.encode_snapshot_set_delegate_calldata(recipient)
    tx = deployed_vesting.snapshot_set_delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events[0]["delegator"] == deployed_vesting.address
    assert tx.events[0]["delegate"] == recipient


def test_set_delegate_after_upgrade(
    deployed_vesting, recipient, voting_adapter_for_update, vesting_factory, owner, voting_adapter
):
    vesting_factory.update_voting_adapter(voting_adapter_for_update, {"from": owner})
    data = voting_adapter.encode_snapshot_set_delegate_calldata(recipient)
    tx = deployed_vesting.snapshot_set_delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events[0]["delegator"] == deployed_vesting.address
    assert tx.events[0]["delegate"] == recipient


def test_set_delegate_from_not_recipient_fail(deployed_vesting, not_recipient, voting_adapter):
    data = voting_adapter.encode_snapshot_set_delegate_calldata(not_recipient)
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.snapshot_set_delegate(data, {"from": not_recipient})
