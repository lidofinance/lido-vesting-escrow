import brownie


def test_update_voting_adapter(activated_vesting, recipient, voting_adapter_for_update):
    tx = activated_vesting.update_voting_adapter(
        voting_adapter_for_update, {"from": recipient}
    )
    assert len(tx.events) == 1
    vote_tx = activated_vesting.vote(312, True, {"from": recipient})
    assert len(vote_tx.events) == 1
    delegate_tx = activated_vesting.set_delegate({"from": recipient})
    assert len(delegate_tx.events) == 1


def test_update_voting_adapter_from_owner_fail(
    activated_vesting, owner, voting_adapter_for_update
):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.update_voting_adapter(
            voting_adapter_for_update, {"from": owner}
        )


def test_update_voting_adapter_from_manager_fail(
    activated_vesting, manager, voting_adapter_for_update
):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.update_voting_adapter(
            voting_adapter_for_update, {"from": manager}
        )
