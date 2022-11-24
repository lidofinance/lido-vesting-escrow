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
