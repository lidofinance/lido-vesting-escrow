import brownie
from brownie import ZERO_ADDRESS


def test_change_manager(deployed_vesting, owner, random_guy):
    deployed_vesting.change_manager(random_guy, {"from": owner})
    assert deployed_vesting.manager() == random_guy


def test_change_manager_from_not_owner(deployed_vesting, not_owner):
    with brownie.reverts("msg.sender not owner"):
        deployed_vesting.change_manager(not_owner, {"from": not_owner})


def test_change_manager_to_zero(deployed_vesting, owner):
    deployed_vesting.change_manager(ZERO_ADDRESS, {"from": owner})
    assert deployed_vesting.manager() == ZERO_ADDRESS
