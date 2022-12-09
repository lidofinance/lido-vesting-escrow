import brownie
from brownie import ZERO_ADDRESS


def test_reinit_impossible_from_owner(deployed_vesting, owner, token, recipient, balance):
    with brownie.reverts("can only initialize once"):
        deployed_vesting.initialize(
            token,
            balance,
            recipient,
            0,
            0,
            0,
            0,
            ZERO_ADDRESS,
            {"from": owner},
        )
