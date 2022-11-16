import brownie


def test_claim_not_activated(deployed_vesting, recipient, chain, end_time):
    chain.sleep(end_time - chain.time())
    with brownie.reverts("not activated"):
        deployed_vesting.claim({"from": recipient})
