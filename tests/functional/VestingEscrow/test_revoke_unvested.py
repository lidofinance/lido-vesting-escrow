import brownie


def test_revoke_unvested_admin_only(vesting, accounts):
    with brownie.reverts("admin only"):
        vesting.revoke_unvested({"from": accounts[1]})


def test_disabled_at_is_initially_end_time(vesting, accounts):
    assert vesting.disabled_at() == vesting.end_time()


def test_revoke_unvested(vesting, accounts):
    tx = vesting.revoke_unvested({"from": accounts[0]})

    assert vesting.disabled_at() == tx.timestamp


def test_revoke_unvested_to_different_address(vesting, accounts, token):
    tx = vesting.revoke_unvested(accounts[2], {"from": accounts[0]})

    assert vesting.disabled_at() == tx.timestamp
    assert token.balanceOf(accounts[2]) == 10**20


def test_revoke_unvested_after_end_time(
    vesting, token, accounts, chain, end_time
):
    chain.sleep(end_time - chain.time())
    vesting.revoke_unvested({"from": accounts[0]})
    vesting.claim({"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 10**20
    assert token.balanceOf(accounts[0]) == 0


def test_revoke_unvested_before_start_time(
    vesting, token, accounts, chain, end_time
):
    vesting.revoke_unvested({"from": accounts[0]})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert token.balanceOf(accounts[0]) == vesting.total_locked()


def test_revoke_unvested_partially_ununclaimed(
    vesting, token, accounts, chain, start_time, end_time
):
    chain.sleep(start_time - chain.time() + 31337)
    tx = vesting.revoke_unvested({"from": accounts[0]})
    chain.sleep(end_time - chain.time())
    vesting.claim({"from": accounts[1]})

    expected_amount = 10**20 * (tx.timestamp - start_time) // (end_time - start_time)
    assert token.balanceOf(accounts[1]) == expected_amount
    assert token.balanceOf(accounts[0]) == vesting.total_locked() - expected_amount


def test_revoke_unvested_partially_claimed(
    vesting, token, accounts, chain, start_time, end_time
):
    sleep_time = (end_time - start_time) // 2
    chain.sleep(start_time - chain.time() + sleep_time)
    claim_amount = 10**18
    vesting.claim(accounts[1], claim_amount, {"from": accounts[1]})

    expected_clawback_amount = 10**20 / 2
    vesting.revoke_unvested({"from": accounts[0]})
    assert token.balanceOf(accounts[1]) == claim_amount
    assert token.balanceOf(accounts[0]) == expected_clawback_amount
