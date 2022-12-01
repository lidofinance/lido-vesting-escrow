def test_claim_full(deployed_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance


def test_claim_less(deployed_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim(recipient, balance / 10, {"from": recipient})

    assert token.balanceOf(recipient) == balance / 10


def test_claim_beneficiary(
    deployed_vesting, token, random_guy, recipient, chain, end_time, balance
):
    chain.sleep(end_time - chain.time())
    deployed_vesting.claim(random_guy, {"from": recipient})

    assert token.balanceOf(random_guy) == balance


def test_claim_before_start(deployed_vesting, token, recipient, chain, start_time):
    chain.sleep(start_time - chain.time() - 5)
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0


def test_claim_before_cliff(
    deployed_vesting_with_cliff, token, recipient, chain, start_time, cliff
):
    chain.sleep(start_time - chain.time() + cliff - 5)
    deployed_vesting_with_cliff.claim({"from": recipient})

    assert token.balanceOf(recipient) == 0


def test_claim_after_cliff(
    deployed_vesting_with_cliff,
    token,
    recipient,
    chain,
    start_time,
    cliff,
    balance,
    end_time,
):
    chain.sleep(start_time - chain.time() + cliff + 5)
    tx = deployed_vesting_with_cliff.claim({"from": recipient})
    expected_amount = balance * (tx.timestamp - start_time) // (end_time - start_time)

    assert token.balanceOf(recipient) == expected_amount
    assert deployed_vesting_with_cliff.total_claimed() == expected_amount


def test_claim_after_end(deployed_vesting, token, recipient, chain, end_time, balance):
    chain.sleep(end_time - chain.time() + 100)
    deployed_vesting.claim({"from": recipient})

    assert token.balanceOf(recipient) == balance


def test_claim_partial(
    deployed_vesting, token, recipient, chain, start_time, end_time, balance
):
    chain.sleep(deployed_vesting.start_time() - chain.time() + 31337)
    tx = deployed_vesting.claim({"from": recipient})
    expected_amount = balance * (tx.timestamp - start_time) // (end_time - start_time)

    assert token.balanceOf(recipient) == expected_amount
    assert deployed_vesting.total_claimed() == expected_amount


def test_claim_multiple(
    deployed_vesting, token, recipient, chain, start_time, end_time, balance
):
    chain.sleep(start_time - chain.time() - 1000)
    balance = 0
    for i in range(11):
        chain.sleep((end_time - start_time) // 10)
        deployed_vesting.claim({"from": recipient})
        new_balance = token.balanceOf(recipient)
        assert new_balance > balance
        balance = new_balance

    assert token.balanceOf(recipient) == balance
