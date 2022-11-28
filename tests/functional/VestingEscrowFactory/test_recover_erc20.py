import brownie
import pytest


@pytest.fixture
def token2(ERC20, owner):
    return ERC20.deploy("XYZ", "XYZ", 18, {"from": owner})


def test_claim_non_vested_token(vesting_factory, token2, owner, balance, random_guy):
    token2._mint_for_testing(balance, {"from": random_guy})
    token2.transfer(vesting_factory, balance, {"from": random_guy})

    vesting_factory.recover_erc20(token2, {"from": owner})
    assert token2.balanceOf(owner) == balance
    assert token2.balanceOf(vesting_factory) == 0


def test_claim_vested_token(vesting_factory, token, owner, balance, random_guy):
    token._mint_for_testing(balance, {"from": random_guy})
    token.transfer(vesting_factory, balance, {"from": random_guy})

    vesting_factory.recover_erc20(token, {"from": owner})
    assert token.balanceOf(owner) == balance
    assert token.balanceOf(vesting_factory) == 0


def test_claim_vested_token_not_owner(vesting_factory, token, recipient):
    with brownie.reverts("msg.sender not owner"):
        vesting_factory.recover_erc20(token, {"from": recipient})


def test_claim_non_vested_token_not_owner(vesting_factory, token2, recipient):
    with brownie.reverts("msg.sender not owner"):
        vesting_factory.recover_erc20(token2, {"from": recipient})
