import brownie
import math


def test_revoke_unvested_owner_or_manager_only(activated_vesting, recipient):
    with brownie.reverts("msg.sender not owner or manager"):
        activated_vesting.revoke_unvested({"from": recipient})


def test_disabled_at_is_initially_end_time(activated_vesting):
    assert activated_vesting.disabled_at() == activated_vesting.end_time()


def test_revoke_unvested(activated_vesting, owner):
    tx = activated_vesting.revoke_unvested({"from": owner})

    assert activated_vesting.disabled_at() == tx.timestamp
    assert activated_vesting.locked() == 0


def test_revoke_unvested_from_manager(activated_vesting, manager):
    tx = activated_vesting.revoke_unvested({"from": manager})

    assert activated_vesting.disabled_at() == tx.timestamp


def test_revoke_unvested_after_end_time(
    activated_vesting, token, owner, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time())
    activated_vesting.revoke_unvested({"from": owner})
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance
    assert token.balanceOf(owner) == 0


def test_revoke_unvested_before_start_time(
    activated_vesting, token, owner, recipient, chain, end_time
):
    activated_vesting.revoke_unvested({"from": owner})
    chain.sleep(end_time - chain.time())
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == activated_vesting.total_locked()


def test_revoke_unvested_partially_ununclaimed(
    activated_vesting, token, owner, recipient, chain, start_time, end_time
):
    chain.sleep(start_time - chain.time() + 31337)
    tx = activated_vesting.revoke_unvested({"from": owner})
    chain.sleep(end_time - chain.time())
    activated_vesting.claim({"from": recipient})

    expected_amount = 10**20 * (tx.timestamp - start_time) // (end_time - start_time)
    assert token.balanceOf(recipient) == expected_amount
    assert token.balanceOf(owner) == activated_vesting.total_locked() - expected_amount


def test_revoke_unvested_partially_claimed(
    activated_vesting, token, owner, recipient, chain, start_time, end_time, balance
):
    sleep_time = (end_time - start_time) // 2
    chain.sleep(start_time - chain.time() + sleep_time)
    chain.mine()
    claim_amount = 10**18
    activated_vesting.claim(recipient, claim_amount, {"from": recipient})

    expected_revoke_amount = activated_vesting.locked({"from": recipient})
    activated_vesting.revoke_unvested({"from": owner})
    assert token.balanceOf(recipient) == claim_amount
    assert math.isclose(
        token.balanceOf(owner),
        expected_revoke_amount,
        abs_tol=balance / (end_time - start_time) * 1,
    )  # we use non strict comparison due to the fact that unvested amount is defined based on timestamps
