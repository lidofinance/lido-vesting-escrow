import brownie
from brownie import ZERO_ADDRESS


def test_reinit_impossible_from_owner(
    activated_vesting, owner, token, recipient, voting_adapter, balance
):
    with brownie.reverts("can only initialize once"):
        activated_vesting.initialize(
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


def test_reinit_impossible_from_not_owner(
    activated_vesting, token, not_owner, voting_adapter, owner, balance
):
    with brownie.reverts("can only initialize once"):
        activated_vesting.initialize(
            token,
            balance,
            not_owner,
            owner,
            ZERO_ADDRESS,
            0,
            0,
            0,
            voting_adapter,
            {"from": not_owner},
        )
