import brownie
from brownie import ZERO_ADDRESS
from eth_abi import encode


def test_delegate(deployed_vesting, voting_adapter, random_guy, recipient):
    # Can assign delegate
    data = voting_adapter.encode_delegate_calldata(random_guy)
    tx = deployed_vesting.delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events["AssignDelegate"]["voter"] == deployed_vesting.address
    assert tx.events["AssignDelegate"]["assignedDelegate"] == random_guy.address

    # Can change delegate
    data = voting_adapter.encode_delegate_calldata(recipient)
    tx = deployed_vesting.delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events["AssignDelegate"]["voter"] == deployed_vesting.address
    assert tx.events["AssignDelegate"]["assignedDelegate"] == recipient.address

    # Encoding invalid parameters will fail
    data = encode(["address", "address"], [random_guy.address, random_guy.address])
    with brownie.reverts(""):
        deployed_vesting.delegate(data, {"from": recipient})
    data = encode(["string"], [""])
    with brownie.reverts(""):
        deployed_vesting.delegate(data, {"from": recipient})
    data = encode(["string"], ["0xdeadbeef"])
    with brownie.reverts(""):
        deployed_vesting.delegate(data, {"from": recipient})

    # Can unassign delegate
    reset_data = voting_adapter.encode_delegate_calldata(ZERO_ADDRESS)
    tx_reset = deployed_vesting.delegate(reset_data, {"from": recipient})
    assert len(tx_reset.events) == 1
    assert tx_reset.events["UnassignDelegate"]["voter"] == deployed_vesting.address
    assert tx_reset.events["UnassignDelegate"]["unassignedDelegate"] == recipient.address


def test_delegate_after_upgrade(
    deployed_vesting, recipient, voting_adapter_for_update, vesting_factory, owner, voting_adapter
):
    vesting_factory.update_voting_adapter(voting_adapter_for_update, {"from": owner})
    data = voting_adapter.encode_delegate_calldata(recipient)
    tx = deployed_vesting.delegate(data, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events["AssignDelegate"]["voter"] == deployed_vesting.address
    assert tx.events["AssignDelegate"]["assignedDelegate"] == recipient.address


def test_delegate_from_not_recipient_fail(deployed_vesting, not_recipient, voting_adapter):
    data = voting_adapter.encode_delegate_calldata(not_recipient)
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.delegate(data, {"from": not_recipient})
