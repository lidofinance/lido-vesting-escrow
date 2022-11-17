from brownie.test import given, strategy


@given(sleep_time=strategy("uint", max_value=100000))
def test_claim_partial(
    activated_vesting,
    token,
    recipient,
    chain,
    start_time,
    sleep_time,
    end_time,
    balance,
):
    chain.sleep(start_time - chain.time() + sleep_time)
    tx = activated_vesting.claim({"from": recipient})
    expected_amount = balance * (tx.timestamp - start_time) // (end_time - start_time)

    assert token.balanceOf(recipient) == expected_amount
