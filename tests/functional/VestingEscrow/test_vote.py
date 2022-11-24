import brownie


def test_vote(deployed_vesting, recipient):
    tx = deployed_vesting.vote(154, True, {"from": recipient})
    assert len(tx.events) == 1


def test_vote_from_owner_fail(deployed_vesting, owner):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.vote(154, True, {"from": owner})


def test_vote_from_owner_fail(deployed_vesting, manager):
    with brownie.reverts("msg.sender not recipient"):
        deployed_vesting.vote(154, True, {"from": manager})
