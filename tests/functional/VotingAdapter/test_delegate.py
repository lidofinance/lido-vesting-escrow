from brownie import ZERO_ADDRESS

def test_delegate(voting_adapter, recipient):
    data = voting_adapter.encode_delegate_calldata(recipient)
    tx = voting_adapter.delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events["AssignDelegate"]["voter"] == voting_adapter.address
    assert tx.events["AssignDelegate"]["assignedDelegate"] == recipient.address

    reset_data = voting_adapter.encode_delegate_calldata(ZERO_ADDRESS)
    tx_reset = voting_adapter.delegate(reset_data, {"from": recipient})
    assert len(tx_reset.events) == 1
    assert tx_reset.events["UnassignDelegate"]["voter"] == voting_adapter.address
    assert tx_reset.events["UnassignDelegate"]["unassignedDelegate"] == recipient.address
