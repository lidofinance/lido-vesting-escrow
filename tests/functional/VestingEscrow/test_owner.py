import brownie
from brownie import ZERO_ADDRESS


def test_change_owner(deployed_vesting, owner, random_guy):
    deployed_vesting.change_owner(random_guy, {"from": owner})
    assert deployed_vesting.owner() == random_guy


def test_change_owner_from_not_owner(deployed_vesting, not_owner):
    with brownie.reverts("msg.sender not owner"):
        deployed_vesting.change_owner(not_owner, {"from": not_owner})


def test_change_owner_not_zero(deployed_vesting, owner):
    with brownie.reverts("zero owner address"):
        deployed_vesting.change_owner(ZERO_ADDRESS, {"from": owner})


def test_revoke_ownership(deployed_vesting, owner):
    deployed_vesting.revoke_ownership({"from": owner})
    assert deployed_vesting.owner() == ZERO_ADDRESS
    assert deployed_vesting.manager() == ZERO_ADDRESS


def test_revoke_ownership_from_not_owner(deployed_vesting, not_owner):
    with brownie.reverts("msg.sender not owner"):
        deployed_vesting.revoke_ownership({"from": not_owner})
