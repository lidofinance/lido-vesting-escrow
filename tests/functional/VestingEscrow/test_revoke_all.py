import brownie
import pytest

pytestmark = [
    pytest.mark.parametrize(
        "deployed_vesting", [pytest.param(1, id="fully_revocable")], indirect=True
    )
]


def test_revoke_all_owner_only(activated_vesting, not_owner):
    with brownie.reverts("msg.sender not owner"):
        activated_vesting.revoke_all({"from": not_owner})


def test_revoke_all(activated_vesting, owner, token):
    tx = activated_vesting.revoke_all({"from": owner})

    assert activated_vesting.disabled_at() == tx.timestamp
    assert activated_vesting.unclaimed() == 0
    assert token.balanceOf(owner) == 10**20


def test_revoke_all_after_end_time(
    activated_vesting, token, owner, recipient, chain, end_time
):
    chain.sleep(end_time - chain.time())
    activated_vesting.revoke_all({"from": owner})
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(owner) == 10**20
    assert token.balanceOf(recipient) == 0


def test_revoke_all_before_start_time(
    activated_vesting, token, owner, recipient, chain, end_time
):
    activated_vesting.revoke_all({"from": owner})
    chain.sleep(end_time - chain.time())
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == activated_vesting.total_locked()


def test_revoke_all_partially_ununclaimed(
    activated_vesting, token, owner, recipient, chain, start_time, end_time
):
    chain.sleep(start_time - chain.time() + 31337)
    tx = activated_vesting.revoke_all({"from": owner})
    chain.sleep(end_time - chain.time())
    activated_vesting.claim({"from": recipient})
    assert activated_vesting.unclaimed() == 0

    assert token.balanceOf(recipient) == 0
    assert token.balanceOf(owner) == activated_vesting.total_locked()
