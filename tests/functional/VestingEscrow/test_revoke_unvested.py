import brownie
import math


def test_revoke_unvested_admin_only(vesting, recipient):
    with brownie.reverts("admin only"):
        vesting.revoke_unvested({"from": recipient})


def test_disabled_at_is_initially_end_time(vesting):
    assert vesting.disabled_at() == vesting.end_time()


def test_revoke_unvested(vesting, admin):
    tx = vesting.revoke_unvested({"from": admin})

    assert vesting.disabled_at() == tx.timestamp


def test_revoke_unvested_to_different_address(vesting, accounts, admin, token, balance):
    tx = vesting.revoke_unvested(accounts[2], {"from": admin})

    assert vesting.disabled_at() == tx.timestamp
    assert token.balanceOf(accounts[2]) == balance


def test_revoke_unvested_after_end_time(
    vesting, token, admin, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time())
    vesting.revoke_unvested({"from": admin})
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance
    assert token.balanceOf(admin) == 0


def test_revoke_unvested_before_start_time(
    vesting, token, admin, recipient, chain, end_time
):
    vesting.revoke_unvested({"from": admin})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(admin) == vesting.total_locked()


def test_revoke_unvested_partially_ununclaimed(
    vesting, token, admin, recipient, chain, start_time, end_time
):
    chain.sleep(start_time - chain.time() + 31337)
    tx = vesting.revoke_unvested({"from": admin})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": recipient})

    expected_amount = 10**20 * (tx.timestamp - start_time) // (end_time - start_time)
    assert token.balanceOf(recipient) == expected_amount
    assert token.balanceOf(admin) == vesting.total_locked() - expected_amount


def test_revoke_unvested_partially_claimed(
    vesting, token, admin, recipient, chain, start_time, end_time, balance
):
    sleep_time = (end_time - start_time) // 2
    chain.sleep(start_time - chain.time() + sleep_time)
    chain.mine()
    claim_amount = 10**18
    vesting.claim(recipient, claim_amount, {"from": recipient})

    expected_revoke_amount = vesting.locked({"from": recipient})
    vesting.revoke_unvested({"from": admin})
    assert token.balanceOf(recipient) == claim_amount
    assert math.isclose(
        token.balanceOf(admin),
        expected_revoke_amount,
        abs_tol=balance / (end_time - start_time) * 1,
    ) # we use non strict comparison due to the fact that unvested amount is defined based on timestamps
