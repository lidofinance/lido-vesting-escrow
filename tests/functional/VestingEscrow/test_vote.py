import brownie


def test_vote(deployed_vesting, recipient):
    tx = deployed_vesting.vote(154, True, {"from": recipient})
    assert len(tx.events) == 1


def test_vote_from_not_recipient_fail(deployed_vesting, not_recipient):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.vote(154, True, {"from": not_recipient})
