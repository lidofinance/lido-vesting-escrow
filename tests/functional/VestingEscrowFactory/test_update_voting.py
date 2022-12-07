import brownie


def test_recover_non_vested_token(
    vesting_factory, voting_adapter_for_update, voting_adapter, owner
):
    assert vesting_factory.voting_adapter() == voting_adapter

    vesting_factory.update_voting_adapter(voting_adapter_for_update, {"from": owner})

    assert vesting_factory.voting_adapter() == voting_adapter_for_update


def test_vote_from_not_recipient_fail(
    vesting_factory, voting_adapter_for_update, not_owner
):
    with brownie.reverts("msg.sender not owner"):
        vesting_factory.update_voting_adapter(
            voting_adapter_for_update, {"from": not_owner}
        )
