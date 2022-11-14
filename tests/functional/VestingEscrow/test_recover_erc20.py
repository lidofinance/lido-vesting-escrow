import brownie
import pytest


@pytest.fixture
def token2(ERC20, admin):
    yield ERC20.deploy("XYZ", "XYZ", 18, {"from": admin})


def test_claim_non_vested_token(vesting, token2, admin, recipient, balance):
    token2._mint_for_testing(balance, {"from": admin})
    token2.transfer(vesting, balance)

    vesting.recover_erc20(token2, {"from": recipient})
    assert token2.balanceOf(recipient) == balance


def test_do_not_allow_claim_of_vested_token(vesting, token, recipient):
    with brownie.reverts():
        vesting.recover_erc20(token, {"from": recipient})


def test_allow_vested_token_recover_to_be_claim_at_end(
    vesting, token, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time() + 1)
    chain.mine()
    vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == balance
