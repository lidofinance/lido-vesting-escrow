import brownie
from brownie import ZERO_ADDRESS

def test_set_delegate(deployed_vesting, recipient):
    with brownie.reverts("not implemented"):
        deployed_vesting.delegate(ZERO_ADDRESS, {"from": recipient})


def test_set_delegate_to_custom_delegate(deployed_vesting, recipient, random_guy):
    with brownie.reverts("not implemented"):
        deployed_vesting.delegate(ZERO_ADDRESS, random_guy, {"from": recipient})


def test_set_delegate_from_owner_fail(deployed_vesting, owner):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.delegate(ZERO_ADDRESS, {"from": owner})


def test_set_delegate_from_manager_fail(deployed_vesting, manager):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.delegate(ZERO_ADDRESS, {"from": manager})
