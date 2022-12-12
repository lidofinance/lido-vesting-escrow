import brownie


def test_revoke_all_owner_only(deployed_vesting, owner):
    with brownie.reverts("not allowed for ordinary vesting"):
        deployed_vesting.revoke_all({"from": owner})
