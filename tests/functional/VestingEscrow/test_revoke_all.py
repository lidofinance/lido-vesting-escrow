import brownie

from tests.conftest import fully_revocable

pytestmark = [fully_revocable]


def test_revoke_all_owner_only(deployed_vesting, not_owner):
    with brownie.reverts("msg.sender not owner"):
        deployed_vesting.revoke_all({"from": not_owner})


def test_revoke_all(deployed_vesting, owner, token, balance):
    owner_balance = token.balanceOf(owner)
    tx = deployed_vesting.revoke_all({"from": owner})

    assert deployed_vesting.disabled_at() == tx.timestamp
    assert deployed_vesting.unclaimed() == 0
    assert deployed_vesting.locked() == 0
    assert token.balanceOf(owner) == balance + owner_balance


def test_revoke_all_twice(deployed_vesting, owner):
    deployed_vesting.revoke_all({"from": owner})
    with brownie.reverts("already fully revoked"):
        deployed_vesting.revoke_all({"from": owner})


def test_revoke_all_after_end_time(deployed_vesting, token, owner, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_all({"from": owner})
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(owner) == balance + owner_balance
    assert token.balanceOf(recipient) == 0


def test_revoke_all_before_start_time(deployed_vesting, token, owner, recipient, chain, end_time, balance):
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_all({"from": owner})
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == balance + owner_balance


def test_claim_after_revoke_all(
    deployed_vesting, token, owner, recipient, chain, start_time, end_time, sleep_time, balance
):
    chain.sleep(start_time - chain.time() + sleep_time)
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_all({"from": owner})
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})
    assert deployed_vesting.unclaimed() == 0

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == balance + owner_balance


def test_revoke_all_after_partial_claim(
    deployed_vesting, token, owner, recipient, chain, start_time, end_time, sleep_time, balance
):
    chain.sleep(start_time - chain.time() + sleep_time)
    claim_amount = 10**18
    deployed_vesting.claim(recipient, claim_amount, {"from": recipient})
    chain.sleep(end_time - chain.time())
    owner_balance = token.balanceOf(owner)
    deployed_vesting.revoke_all({"from": owner})
    assert deployed_vesting.unclaimed() == 0

    assert token.balanceOf(recipient) == claim_amount
    assert token.balanceOf(owner) == balance - claim_amount + owner_balance


def test_revoke_all_after_revoke_unvested(
    deployed_vesting, token, owner, chain, start_time, end_time, sleep_time, balance
):
    chain.sleep(start_time - chain.time() + sleep_time)
    owner_balance = token.balanceOf(owner)
    tx = deployed_vesting.revoke_unvested({"from": owner})
    expected_amount = balance * (tx.timestamp - start_time) // (end_time - start_time)
    assert token.balanceOf(owner) == balance - expected_amount + owner_balance
    deployed_vesting.revoke_all({"from": owner})
    assert token.balanceOf(owner) == balance + owner_balance
