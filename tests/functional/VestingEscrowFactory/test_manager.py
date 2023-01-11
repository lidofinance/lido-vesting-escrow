import brownie
from brownie import ZERO_ADDRESS


def test_change_manager(vesting_factory, owner, random_guy):
    vesting_factory.change_manager(random_guy, {"from": owner})
    assert vesting_factory.manager() == random_guy


def test_change_manager_from_not_owner(vesting_factory, not_owner):
    with brownie.reverts("msg.sender not owner"):
        vesting_factory.change_manager(not_owner, {"from": not_owner})


def test_change_manager_to_zero(vesting_factory, owner):
    vesting_factory.change_manager(ZERO_ADDRESS, {"from": owner})
    assert vesting_factory.manager() == ZERO_ADDRESS
