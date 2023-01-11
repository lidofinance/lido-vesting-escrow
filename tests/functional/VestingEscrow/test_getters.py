def test_locked_unclaimed(chain, deployed_vesting, end_time):
    assert deployed_vesting.locked() == deployed_vesting.total_locked()
    assert deployed_vesting.unclaimed() == 0
    chain.sleep(end_time - chain.time())
    chain.mine()
    assert deployed_vesting.locked() == 0
    assert deployed_vesting.unclaimed() == deployed_vesting.total_locked()
    deployed_vesting.claim({"from": deployed_vesting.recipient()})
    assert deployed_vesting.unclaimed() == 0
