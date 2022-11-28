import brownie
import pytest


@pytest.fixture
def token2(ERC20, owner):
    return ERC20.deploy("XYZ", "XYZ", 18, {"from": owner})


def test_claim_non_vested_token(deployed_vesting, token2, recipient, balance):
    token2._mint_for_testing(balance, {"from": recipient})
    token2.transfer(deployed_vesting, balance, {"from": recipient})

    deployed_vesting.recover_erc20(token2, {"from": recipient})
    assert token2.balanceOf(recipient) == balance


def test_claim_of_locked_tokens(
    deployed_vesting, token, recipient
):
    deployed_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == 0


def test_claim_of_extra_locked_tokens(
    deployed_vesting, token, recipient, owner
):
    extra = 10 ** 17
    token._mint_for_testing(extra, {"from": owner})
    token.transfer(deployed_vesting, extra, {"from": owner})
    deployed_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == extra


def test_claim_of_extra_locked_tokens_partially_claimed(
    deployed_vesting, token, recipient, owner, random_guy, chain, end_time
):
    extra = 10 ** 17
    claim_amount = 3 * extra
    token._mint_for_testing(extra, {"from": owner})
    token.transfer(deployed_vesting, extra, {"from": owner})
    chain.sleep(end_time - chain.time() + 1)
    deployed_vesting.claim(random_guy, claim_amount, {"from": recipient})
    deployed_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(random_guy) == claim_amount
    assert token.balanceOf(recipient) == extra


def test_claim_of_locked_tokens_after_end(
    deployed_vesting, token, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time() + 1)
    deployed_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == 0
    assert deployed_vesting.locked() == 0
    assert deployed_vesting.unclaimed() == balance


def test_claim_of_locked_tokens_after_end_partially_claimed(
    deployed_vesting, token, recipient, chain, end_time, balance, random_guy
):
    chain.sleep(end_time - chain.time() + 1)
    claim_amount = 10**17
    deployed_vesting.claim(random_guy, claim_amount, {"from": recipient})
    deployed_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == 0
    assert deployed_vesting.locked() == 0
    assert deployed_vesting.unclaimed() == balance - claim_amount


def test_claim_vested_token_not_recipient(deployed_vesting, token, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.recover_erc20(token, {"from": not_recipient})


def test_claim_non_vested_token_not_recipient(deployed_vesting, token2, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.recover_erc20(token2, {"from": not_recipient})
