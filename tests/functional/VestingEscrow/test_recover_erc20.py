import brownie
import pytest


@pytest.fixture
def token2(ERC20, owner):
    return ERC20.deploy("XYZ", "XYZ", 18, {"from": owner})


def test_claim_non_vested_token(activated_vesting, token2, recipient, balance):
    token2._mint_for_testing(balance, {"from": recipient})
    token2.transfer(activated_vesting, balance, {"from": recipient})

    activated_vesting.recover_erc20(token2, {"from": recipient})
    assert token2.balanceOf(recipient) == balance


def test_claim_of_locked_tokens(activated_vesting, token, recipient):
    activated_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == 0


def test_claim_of_additional_vesting_tokens(
    activated_vesting, token, recipient, balance
):
    token._mint_for_testing(balance, {"from": recipient})
    token.transfer(activated_vesting, balance, {"from": recipient})
    assert token.balanceOf(recipient) == 0
    activated_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == balance


def test_claim_non_vested_token_not_recipient(activated_vesting, token, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.recover_erc20(token, {"from": not_recipient})
