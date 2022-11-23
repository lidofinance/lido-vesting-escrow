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


def test_claim_of_locked_tokens_before_end(activated_vesting, token, recipient, chain, end_time):
    chain.sleep(end_time - chain.time() - 1)
    with brownie.reverts("recover vesting token before end"):
        activated_vesting.recover_erc20(token, {"from": recipient})


def test_claim_of_locked_tokens_after_end(activated_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time() + 1)
    activated_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == balance
    assert activated_vesting.locked() == 0
    assert activated_vesting.unclaimed() == 0


def test_claim_of_locked_tokens_after_end_unclaimed(activated_vesting, token, recipient, chain, end_time, balance, random_guy):
    chain.sleep(end_time - chain.time() + 1)
    claim_amount = 10 ** 17
    activated_vesting.claim(random_guy, claim_amount, {"from": recipient})
    activated_vesting.recover_erc20(token, {"from": recipient})
    assert token.balanceOf(recipient) == balance - claim_amount
    assert activated_vesting.locked() == 0
    assert activated_vesting.unclaimed() == 0


def test_claim_non_vested_token_not_recipient(activated_vesting, token, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.recover_erc20(token, {"from": not_recipient})

def test_claim_vested_token_not_recipient(activated_vesting, token2, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.recover_erc20(token2, {"from": not_recipient})