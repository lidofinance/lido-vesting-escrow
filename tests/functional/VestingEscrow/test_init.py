import brownie
from brownie import ZERO_ADDRESS


def test_reinit_impossible_from_owner(deployed_vesting, owner, token, recipient, voting_adapter, balance):
    with brownie.reverts("can only initialize once"):
        deployed_vesting.initialize(
            token,
            balance,
            recipient,
            owner,
            ZERO_ADDRESS,
            0,
            0,
            0,
            voting_adapter,
            {"from": owner},
        )
