import pytest
from brownie import ZERO_ADDRESS


def test_claim_full(vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance


def test_claim_less(vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    vesting.claim(recipient, vesting.total_locked() / 10, {"from": recipient})

    assert token.balanceOf(recipient) == balance / 10


def test_claim_beneficiary(
    vesting, token, accounts, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time())
    vesting.claim(accounts[2], {"from": recipient})

    assert token.balanceOf(accounts[2]) == balance


def test_claim_before_start(vesting, token, recipient, chain, start_time):
    chain.sleep(start_time - chain.time() - 5)
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0


def test_claim_after_end(vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time() + 100)
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance


def test_claim_partial(vesting, token, recipient, chain, start_time, end_time):
    chain.sleep(vesting.start_time() - chain.time() + 31337)
    tx = vesting.claim({"from": recipient})
    expected_amount = (
        vesting.total_locked() * (tx.timestamp - start_time) // (end_time - start_time)
    )

    assert token.balanceOf(recipient) == expected_amount
    assert vesting.total_claimed() == expected_amount


def test_claim_multiple(
    vesting, token, recipient, chain, start_time, end_time, balance
):
    chain.sleep(start_time - chain.time() - 1000)
    balance = 0
    for i in range(11):
        chain.sleep((end_time - start_time) // 10)
        vesting.claim({"from": recipient})
        new_balance = token.balanceOf(recipient)
        assert new_balance > balance
        balance = new_balance

    assert token.balanceOf(recipient) == balance
