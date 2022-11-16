import brownie
from brownie import ZERO_ADDRESS


def test_reactivate_impossible_from_admin(activated_vesting, balance, owner):
    with brownie.reverts("can only activate once"):
        activated_vesting.activate(
            balance,
            owner,
            ZERO_ADDRESS,
            {"from": owner},
        )
