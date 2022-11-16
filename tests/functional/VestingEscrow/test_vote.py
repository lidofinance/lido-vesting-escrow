import brownie


def test_vote(activated_vesting, recipient):
    tx = activated_vesting.vote(154, True, {"from": recipient})
    assert len(tx.events) == 1


def test_vote_from_owner_fail(activated_vesting, owner):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.vote(154, True, {"from": owner})


def test_vote_from_owner_fail(activated_vesting, manager):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.vote(154, True, {"from": manager})
