import brownie


def test_reinit_impossible_from_owner(
    activated_vesting, owner, token, recipient, voting_adapter
):
    with brownie.reverts("can only initialize once"):
        activated_vesting.initialize(
            token, recipient, 0, 0, 0, voting_adapter, {"from": owner}
        )


def test_reinit_impossible_from_not_owner(
    activated_vesting, token, not_owner, voting_adapter
):
    with brownie.reverts("can only initialize once"):
        activated_vesting.initialize(
            token, not_owner, 0, 0, 0, voting_adapter, {"from": not_owner}
        )
