import pytest

from tests.conftest import fully_revocable
from tests.utils import mint_or_transfer_for_testing


@pytest.fixture
def token2(ERC20, owner):
    return ERC20.deploy("XYZ", "XYZ", 18, {"from": owner})


@pytest.fixture
def token_no_return(ERC20NoReturn, owner):
    return ERC20NoReturn.deploy("XYZ", "XYZ", 18, {"from": owner})


def test_recover_non_vested_token(deployed_vesting, token2, recipient, balance):
    token2._mint_for_testing(balance, {"from": recipient})
    token2.transfer(deployed_vesting, balance, {"from": recipient})

    deployed_vesting.recover_erc20(token2, balance, {"from": recipient})
    assert token2.balanceOf(recipient) == balance


def test_recover_non_vested_token_with_bad_impl(deployed_vesting, token_no_return, recipient, balance):
    token_no_return._mint_for_testing(balance, {"from": recipient})
    token_no_return.transfer(deployed_vesting, balance, {"from": recipient})

    deployed_vesting.recover_erc20(token_no_return, balance, {"from": recipient})
    assert token_no_return.balanceOf(recipient) == balance


def test_recover_locked_tokens(deployed_vesting, token, recipient, balance):
    deployed_vesting.recover_erc20(token, balance, {"from": recipient})
    assert token.balanceOf(recipient) == 0


def test_recover_extra_locked_tokens(deployed_vesting, token, recipient, owner, balance, deployed):
    extra = 10**17
    mint_or_transfer_for_testing(owner, owner, token, extra, deployed)
    token.transfer(deployed_vesting, extra, {"from": owner})
    deployed_vesting.recover_erc20(token, balance, {"from": recipient})
    assert token.balanceOf(recipient) == extra


def test_recover_extra_locked_tokens_partially_claimed(
    deployed_vesting, token, recipient, owner, random_guy, chain, end_time, balance, deployed
):
    extra = 10**17
    claim_amount = 3 * extra
    mint_or_transfer_for_testing(owner, owner, token, extra, deployed)
    token.transfer(deployed_vesting, extra, {"from": owner})
    chain.sleep(end_time - chain.time() + 1)
    deployed_vesting.claim(random_guy, claim_amount, {"from": recipient})
    deployed_vesting.recover_erc20(token, balance, {"from": recipient})
    assert token.balanceOf(random_guy) == claim_amount
    assert token.balanceOf(recipient) == extra


def test_recover_locked_tokens_after_end(deployed_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time() + 1)
    deployed_vesting.recover_erc20(token, balance, {"from": recipient})
    assert token.balanceOf(recipient) == 0
    assert deployed_vesting.locked() == 0
    assert deployed_vesting.unclaimed() == balance


def test_recover_locked_tokens_after_end_partially_claimed(
    deployed_vesting, token, recipient, chain, end_time, balance, random_guy
):
    chain.sleep(end_time - chain.time() + 1)
    claim_amount = 10**17
    deployed_vesting.claim(random_guy, claim_amount, {"from": recipient})
    deployed_vesting.recover_erc20(token, balance, {"from": recipient})
    assert token.balanceOf(recipient) == 0
    assert deployed_vesting.locked() == 0
    assert deployed_vesting.unclaimed() == balance - claim_amount


def test_recover_ether(deployed_vesting, anyone, recipient, random_guy, one_eth, destructible):
    random_guy.transfer(destructible, one_eth)
    destructible.destruct(deployed_vesting)
    assert deployed_vesting.balance() == one_eth
    balance_before = recipient.balance()
    deployed_vesting.recover_ether({"from": anyone})
    assert recipient.balance() == balance_before + one_eth
    assert deployed_vesting.balance() == 0


def test_recover_extra_after_revoke_unvested(deployed_vesting, token, balance, recipient, owner, deployed):
    extra = 10**17
    mint_or_transfer_for_testing(owner, owner, token, extra, deployed)
    token.transfer(deployed_vesting, extra, {"from": owner})

    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_unvested({"from": owner})
    assert token.balanceOf(owner) == balance + owner_balance

    deployed_vesting.recover_erc20(token, extra + 1, {"from": recipient})
    assert token.balanceOf(recipient) == extra


def test_recover_extra_after_revoke_unvested_partially(
    deployed_vesting, token, balance, recipient, owner, chain, start_time, end_time, sleep_time, deployed
):
    extra = 10**17
    mint_or_transfer_for_testing(owner, owner, token, extra, deployed)
    token.transfer(deployed_vesting, extra, {"from": owner})

    chain.sleep(start_time - chain.time() + sleep_time)
    owner_balance = token.balanceOf(owner)
    tx = deployed_vesting.revoke_unvested({"from": owner})
    expected_amount = 10**20 * (tx.timestamp - start_time) // (end_time - start_time)
    assert token.balanceOf(owner) == expected_amount + owner_balance

    deployed_vesting.recover_erc20(token, extra + 1, {"from": recipient})
    assert token.balanceOf(recipient) == extra

    deployed_vesting.claim({"from": recipient})
    assert token.balanceOf(recipient) == extra + balance - expected_amount


@fully_revocable
def test_recover_extra_after_revoke_all(
    deployed_vesting, token, balance, recipient, owner, chain, start_time, sleep_time, deployed
):
    extra = 10**17
    mint_or_transfer_for_testing(owner, owner, token, extra, deployed)
    token.transfer(deployed_vesting, extra, {"from": owner})

    chain.sleep(start_time - chain.time() + sleep_time)
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_all({"from": owner})
    assert token.balanceOf(owner) == balance + owner_balance

    deployed_vesting.recover_erc20(token, balance, {"from": recipient})
    assert token.balanceOf(recipient) == extra
