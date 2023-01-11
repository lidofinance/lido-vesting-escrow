import brownie


def test_vote(deployed_vesting, recipient, voting_adapter):
    vote_id = 154
    supports = True
    data = voting_adapter.encode_aragon_vote_calldata(vote_id, supports)
    tx = deployed_vesting.aragon_vote(data, {"from": recipient})
    assert len(tx.events) == 1


def test_vote_after_upgrade(
    deployed_vesting, recipient, voting_adapter_for_update, vesting_factory, owner, voting_adapter
):
    vesting_factory.update_voting_adapter(voting_adapter_for_update, {"from": owner})
    vote_id = 154
    supports = True
    data = voting_adapter.encode_aragon_vote_calldata(vote_id, supports)
    tx = deployed_vesting.aragon_vote(data, {"from": recipient})
    assert len(tx.events) == 1


def test_vote_from_not_recipient_fail(deployed_vesting, not_recipient, voting_adapter):
    vote_id = 154
    supports = True
    data = voting_adapter.encode_aragon_vote_calldata(vote_id, supports)
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.aragon_vote(data, {"from": not_recipient})
