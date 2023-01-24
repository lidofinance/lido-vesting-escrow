import brownie
from brownie import ZERO_ADDRESS


def test_change_owner(voting_adapter, owner, random_guy):
    voting_adapter.change_owner(random_guy, {"from": owner})
    assert voting_adapter.owner() == random_guy


def test_change_owner_from_not_owner(voting_adapter, not_owner):
    with brownie.reverts("msg.sender not owner"):
        voting_adapter.change_owner(not_owner, {"from": not_owner})


def test_change_owner_not_zero(voting_adapter, owner):
    with brownie.reverts("zero owner address"):
        voting_adapter.change_owner(ZERO_ADDRESS, {"from": owner})
