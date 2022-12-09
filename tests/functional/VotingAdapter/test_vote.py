def test_aragon_vote(voting_adapter, recipient, balance, token):
    token._mint_for_testing(balance, {"from": recipient})
    token.transfer(voting_adapter.address, balance, {"from": recipient})
    vote_id = 154
    supports = True
    data = voting_adapter.encode_aragon_vote_calldata(vote_id, supports)
    tx = voting_adapter.aragon_vote(data, {"from": recipient})
    assert len(tx.events) == 1
