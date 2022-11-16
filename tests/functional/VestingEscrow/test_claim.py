def test_claim_full(activated_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance


def test_claim_less(activated_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    activated_vesting.claim(
        recipient, activated_vesting.total_locked() / 10, {"from": recipient}
    )

    assert token.balanceOf(recipient) == balance / 10


def test_claim_beneficiary(
    activated_vesting, token, random_guy, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time())
    activated_vesting.claim(random_guy, {"from": recipient})

    assert token.balanceOf(random_guy) == balance


def test_claim_before_start(activated_vesting, token, recipient, chain, start_time):
    chain.sleep(start_time - chain.time() - 5)
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0


def test_claim_after_end(activated_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time() + 100)
    activated_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance


def test_claim_partial(
    activated_vesting, token, recipient, chain, start_time, end_time
):
    chain.sleep(activated_vesting.start_time() - chain.time() + 31337)
    tx = activated_vesting.claim({"from": recipient})
    expected_amount = (
        activated_vesting.total_locked()
        * (tx.timestamp - start_time)
        // (end_time - start_time)
    )

    assert token.balanceOf(recipient) == expected_amount
    assert activated_vesting.total_claimed() == expected_amount


def test_claim_multiple(
    activated_vesting, token, recipient, chain, start_time, end_time, balance
):
    chain.sleep(start_time - chain.time() - 1000)
    balance = 0
    for i in range(11):
        chain.sleep((end_time - start_time) // 10)
        activated_vesting.claim({"from": recipient})
        new_balance = token.balanceOf(recipient)
        assert new_balance > balance
        balance = new_balance

    assert token.balanceOf(recipient) == balance
