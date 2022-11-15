import brownie


def test_reinit_impossible_from_admin(vesting, admin, token, recipient, voting_adapter):
    with brownie.reverts("can only initialize once"):
        vesting.initialize(
            recipient, token, recipient, 0, 0, 0, 0, voting_adapter, {"from": admin}
        )


def test_reinit_impossible_from_admin(vesting, token, recipient, voting_adapter):
    with brownie.reverts("can only initialize once"):
        vesting.initialize(
            recipient, token, recipient, 0, 0, 0, 0, voting_adapter, {"from": recipient}
        )


def test_reinit_impossible_with_renounce(
    vesting, admin, recipient, token, voting_adapter
):
    vesting.renounce_ownership({"from": admin})
    with brownie.reverts("can only initialize once"):
        vesting.initialize(
            recipient, token, recipient, 0, 0, 0, 0, voting_adapter, {"from": recipient}
        )
