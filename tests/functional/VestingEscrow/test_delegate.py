import brownie
from brownie import ZERO_ADDRESS


def test_delegate(deployed_vesting, recipient):
    with brownie.reverts("not implemented"):
        deployed_vesting.delegate({"from": recipient})


def test_delegate_to_custom_delegate(deployed_vesting, recipient, random_guy):
    with brownie.reverts("not implemented"):
        deployed_vesting.delegate(random_guy, {"from": recipient})


def test_delegate_from_not_recipient_fail(deployed_vesting, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.delegate({"from": not_recipient})
