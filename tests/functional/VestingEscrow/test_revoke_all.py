import brownie
import pytest

pytestmark = [pytest.mark.parametrize("vesting", [1], indirect=True)]


def test_revoke_unvested_admin_only(vesting, recipient):
    with brownie.reverts("admin only"):
        vesting.revoke_all({"from": recipient})


def test_revoke_all(vesting, admin, token):
    tx = vesting.revoke_all({"from": admin})

    assert vesting.disabled_at() == tx.timestamp
    assert vesting.unclaimed() == 0
    assert token.balanceOf(admin) == 10**20


def test_revoke_all_to_different_address(vesting, admin, accounts, token):
    tx = vesting.revoke_all(accounts[2], {"from": admin})

    assert vesting.disabled_at() == tx.timestamp
    assert vesting.unclaimed() == 0
    assert token.balanceOf(accounts[2]) == 10**20


def test_revoke_all_after_end_time(vesting, token, admin, recipient, chain, end_time):
    chain.sleep(end_time - chain.time())
    vesting.revoke_unvested({"from": admin})
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 10**20
    assert token.balanceOf(admin) == 0


def test_revoke_all_before_start_time(
    vesting, token, admin, recipient, chain, end_time
):
    vesting.revoke_all({"from": admin})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(admin) == vesting.total_locked()


def test_revoke_all_partially_ununclaimed(
    vesting, token, admin, recipient, chain, start_time, end_time
):
    chain.sleep(start_time - chain.time() + 31337)
    tx = vesting.revoke_all({"from": admin})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": recipient})
    assert vesting.unclaimed() == 0

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(admin) == vesting.total_locked()
