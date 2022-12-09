from eth_abi import abi


def test_encode_delegate_calldata(voting_adapter, recipient):
    data = voting_adapter.encode_delegate_calldata(recipient)
    assert data == "0x" + abi.encode(["address"], [recipient.address]).hex()


def test_encode_snapshot_set_delegate_calldata(voting_adapter, recipient):
    data = voting_adapter.encode_snapshot_set_delegate_calldata(recipient)
    assert data == "0x" + abi.encode(["address"], [recipient.address]).hex()


def test_encode_aragon_vote_calldata(voting_adapter):
    vote_id = 154
    supports = True
    data = voting_adapter.encode_aragon_vote_calldata(vote_id, supports)
    assert data == "0x" + abi.encode(["uint256", "bool"], [vote_id, supports]).hex()
