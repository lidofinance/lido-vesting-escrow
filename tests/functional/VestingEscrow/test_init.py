import brownie


def test_reinit_impossible_from_admin(vesting, admin, token, recipient):
    with brownie.reverts("can only initialize once"):
        vesting.initialize(
            recipient, token, recipient, 0, 0, 0, 0, {"from": admin}
        )

def test_reinit_impossible_from_admin(vesting, token, recipient):
    with brownie.reverts("can only initialize once"):
        vesting.initialize(
            recipient, token, recipient, 0, 0, 0, 0, {"from": recipient}
        )

def test_reinit_impossible_with_renonunce(vesting, admin, recipient, token):
    vesting.renounce_ownership({"from": admin})
    with brownie.reverts("can only initialize once"):
        vesting.initialize(
            recipient, token, recipient, 0, 0, 0, 0, {"from": recipient}
        )
