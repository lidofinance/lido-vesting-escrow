import brownie
from brownie import ZERO_ADDRESS


def test_change_owner(vesting_factory, owner, random_guy):
    vesting_factory.change_owner(random_guy, {"from": owner})
    assert vesting_factory.owner() == random_guy


def test_change_owner_from_not_owner(vesting_factory, not_owner):
    with brownie.reverts("msg.sender not owner"):
        vesting_factory.change_owner(not_owner, {"from": not_owner})


def test_change_owner_not_zero(vesting_factory, owner):
    with brownie.reverts("zero owner address"):
        vesting_factory.change_owner(ZERO_ADDRESS, {"from": owner})
