def test_activate_event(deployed_vesting, owner, token, recipient, balance):
    token._mint_for_testing(balance, {"from": owner})
    token.transfer(deployed_vesting, balance, {"from": owner})
    tx = deployed_vesting.activate(
        {"from": recipient},
    )
    assert len(tx.events) == 1
    assert tx.events[0]["recipient"] == recipient
