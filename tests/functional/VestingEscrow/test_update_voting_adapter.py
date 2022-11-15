import brownie


def test_update_voting_adapter(vesting, recipient, voting_adapter_for_update):
    tx = vesting.update_voting_adapter(voting_adapter_for_update, {"from": recipient})
    assert len(tx.events) == 1
    vote_tx = vesting.vote(312, True, {"from": recipient})
    assert len(vote_tx.events) == 1
    delegate_tx = vesting.set_delegate({"from": recipient})
    assert len(delegate_tx.events) == 1


def test_vote_non_recipient(vesting, admin, voting_adapter_for_update):
    with brownie.reverts("recipient only"):
        vesting.update_voting_adapter(voting_adapter_for_update, {"from": admin})
