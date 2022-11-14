import brownie
import pytest

pytestmark = [pytest.mark.parametrize("vesting", [1], indirect=True)]


def test_revoke_unvested_admin_only(vesting, accounts):
    with brownie.reverts("admin only"):
        vesting.revoke_all({"from": accounts[1]})


def test_revoke_all(vesting, accounts, token, start_time):
    tx = vesting.revoke_all({"from": accounts[0]})

    assert vesting.disabled_at() == tx.timestamp
    assert vesting.unclaimed() == 0
    assert token.balanceOf(accounts[0]) == 10**20


def test_revoke_all_to_different_address(vesting, accounts, token, start_time):
    tx = vesting.revoke_all(accounts[2], {"from": accounts[0]})

    assert vesting.disabled_at() == tx.timestamp
    assert vesting.unclaimed() == 0
    assert token.balanceOf(accounts[2]) == 10**20


def test_revoke_all_after_end_time(
    vesting, token, accounts, chain, end_time
):
    chain.sleep(end_time - chain.time())
    vesting.revoke_unvested({"from": accounts[0]})
    vesting.claim({"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 10**20
    assert token.balanceOf(accounts[0]) == 0


def test_revoke_all_before_start_time(
    vesting, token, accounts, chain, end_time
):
    vesting.revoke_all({"from": accounts[0]})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert token.balanceOf(accounts[0]) == vesting.total_locked()


def test_revoke_all_partially_ununclaimed(
    vesting, token, accounts, chain, start_time, end_time
):
    chain.sleep(start_time - chain.time() + 31337)
    tx = vesting.revoke_all({"from": accounts[0]})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": accounts[1]})
    assert vesting.unclaimed() == 0

    assert token.balanceOf(accounts[1]) == 0
    assert token.balanceOf(accounts[0]) == vesting.total_locked()
