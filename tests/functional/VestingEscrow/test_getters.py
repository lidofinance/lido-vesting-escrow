def test_locked_unclaimed(chain, activated_vesting, end_time):
    assert activated_vesting.locked() == activated_vesting.total_locked()
    assert activated_vesting.unclaimed() == 0
    chain.sleep(end_time - chain.time())
    chain.mine()
    assert activated_vesting.locked() == 0
    assert activated_vesting.unclaimed() == activated_vesting.total_locked()
    activated_vesting.claim({"from": activated_vesting.recipient()})
    assert activated_vesting.unclaimed() == 0
