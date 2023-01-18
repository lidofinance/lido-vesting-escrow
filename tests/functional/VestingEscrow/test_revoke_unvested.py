import math

import brownie


def test_revoke_unvested_owner_or_manager_only(deployed_vesting, recipient):
    with brownie.reverts("msg.sender not owner or manager"):
        deployed_vesting.revoke_unvested({"from": recipient})


def test_disabled_at_is_initially_end_time(deployed_vesting):
    assert deployed_vesting.disabled_at() == deployed_vesting.end_time()


def test_revoke_unvested(deployed_vesting, owner, token, balance):
    owner_balance = token.balanceOf(owner)
    tx = deployed_vesting.revoke_unvested({"from": owner})

    assert deployed_vesting.disabled_at() == tx.timestamp
    assert deployed_vesting.locked() == 0
    assert token.balanceOf(owner) == balance + owner_balance


def test_revoke_unvested_from_manager(deployed_vesting, manager):
    tx = deployed_vesting.revoke_unvested({"from": manager})

    assert deployed_vesting.disabled_at() == tx.timestamp
    assert deployed_vesting.locked() == 0


def test_revoke_unvested_after_end_time(deployed_vesting, token, owner, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_unvested({"from": owner})
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance
    assert token.balanceOf(owner) == 0 + owner_balance


def test_revoke_unvested_before_start_time(deployed_vesting, token, owner, recipient, chain, end_time):
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_unvested({"from": owner})
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == deployed_vesting.total_locked() + owner_balance


def test_revoke_unvested_partially_unclaimed(deployed_vesting, token, owner, recipient, chain, start_time, end_time, sleep_time):
    chain.sleep(start_time - chain.time() + sleep_time)
    owner_balance = token.balanceOf(owner)
    tx = deployed_vesting.revoke_unvested({"from": owner})
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})

    expected_amount = 10**20 * (tx.timestamp - start_time) // (end_time - start_time)
    assert token.balanceOf(recipient) == expected_amount
    assert token.balanceOf(owner) == deployed_vesting.total_locked() - expected_amount + owner_balance


def test_revoke_unvested_partially_claimed(
    deployed_vesting, token, owner, recipient, chain, start_time, end_time, sleep_time, balance
):
    chain.sleep(start_time - chain.time() + sleep_time)
    chain.mine()
    claim_amount = 10**18
    deployed_vesting.claim(recipient, claim_amount, {"from": recipient})

    expected_revoke_amount = deployed_vesting.locked({"from": recipient})
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_unvested({"from": owner})
    assert token.balanceOf(recipient) == claim_amount
    assert math.isclose(
        token.balanceOf(owner),
        expected_revoke_amount + owner_balance,
        abs_tol=balance / (end_time - start_time) * 1,
    )  # we use non strict comparison due to the fact that unvested amount is defined based on timestamps
