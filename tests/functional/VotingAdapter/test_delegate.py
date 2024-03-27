from brownie import ZERO_ADDRESS

def test_delegate(voting_adapter, recipient):
    data = voting_adapter.encode_delegate_calldata(recipient)
    tx = voting_adapter.delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events["SetDelegate"]["voter"] == voting_adapter.address
    assert tx.events["SetDelegate"]["delegate"] == recipient.address

    reset_data = voting_adapter.encode_delegate_calldata(ZERO_ADDRESS)
    tx_reset = voting_adapter.delegate(reset_data, {"from": recipient})
    assert len(tx_reset.events) == 1
    assert tx_reset.events["ResetDelegate"]["voter"] == voting_adapter.address
    assert tx_reset.events["ResetDelegate"]["delegate"] == recipient.address