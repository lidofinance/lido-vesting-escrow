import brownie
import pytest

pytestmark = [pytest.mark.parametrize("deployed_vesting", [pytest.param(1, id="fully_revocable")], indirect=True)]


def test_revoke_all_owner_only(deployed_vesting, not_owner):
    with brownie.reverts("msg.sender not owner"):
        deployed_vesting.revoke_all({"from": not_owner})


def test_revoke_all(deployed_vesting, owner, token, balance):
    tx = deployed_vesting.revoke_all({"from": owner})

    assert deployed_vesting.disabled_at() == tx.timestamp
    assert deployed_vesting.unclaimed() == 0
    assert deployed_vesting.locked() == 0
    assert token.balanceOf(owner) == balance


def test_revoke_all_after_end_time(deployed_vesting, token, owner, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    deployed_vesting.revoke_all({"from": owner})
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(owner) == balance
    assert token.balanceOf(recipient) == 0


def test_revoke_all_before_start_time(deployed_vesting, token, owner, recipient, chain, end_time, balance):
    deployed_vesting.revoke_all({"from": owner})
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == balance


def test_revoke_all_partially_ununclaimed(
    deployed_vesting, token, owner, recipient, chain, start_time, end_time, balance
):
    chain.sleep(start_time - chain.time() + 31337)
    deployed_vesting.revoke_all({"from": owner})
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})
    assert deployed_vesting.unclaimed() == 0

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == balance
