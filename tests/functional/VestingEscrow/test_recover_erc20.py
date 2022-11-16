import brownie
import pytest


@pytest.fixture
def token2(ERC20, owner):
    yield ERC20.deploy("XYZ", "XYZ", 18, {"from": owner})


def test_claim_non_vested_token(activated_vesting, token2, owner, balance):
    token2._mint_for_testing(balance, {"from": owner})
    token2.transfer(activated_vesting, balance)

    activated_vesting.recover_erc20(token2, {"from": owner})
    assert token2.balanceOf(owner) == balance


def test_claim_non_vested_token_manager(
    activated_vesting, token2, owner, manager, balance
):
    token2._mint_for_testing(balance, {"from": owner})
    token2.transfer(activated_vesting, balance)

    activated_vesting.recover_erc20(token2, {"from": manager})
    assert token2.balanceOf(owner) == balance


def test_do_not_allow_claim_of_vested_token(activated_vesting, token, owner):
    with brownie.reverts():
        activated_vesting.recover_erc20(token, {"from": owner})


def test_do_not_allow_claim_by_recipient(activated_vesting, token, recipient):
    with brownie.reverts():
        activated_vesting.recover_erc20(token, {"from": recipient})
