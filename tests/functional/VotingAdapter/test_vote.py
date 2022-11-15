def test_vote(voting_adapter, recipient, voting, balance, token):
    token._mint_for_testing(balance, {"from": recipient})
    token.transfer(voting_adapter.address, balance, {"from": recipient})
    tx = voting_adapter.vote(voting, 154, True, {"from": recipient})
    assert len(tx.events) == 1
