import brownie
from brownie import ZERO_ADDRESS


def test_init_fail_on_zero_revokable_target(accounts, VestingEscrowFactory, vesting_target_fully_revokable):
    with brownie.reverts("target_simple should not be ZERO_ADDRESS"):
        VestingEscrowFactory.deploy(ZERO_ADDRESS, vesting_target_fully_revokable, {"from": accounts[0]})

def test_init_fail_on_zero_simple_target(accounts, VestingEscrowFactory, vesting_target_simple):
    with brownie.reverts("target_fully_revokable should not be ZERO_ADDRESS"):
        VestingEscrowFactory.deploy(vesting_target_simple, ZERO_ADDRESS, {"from": accounts[0]})
