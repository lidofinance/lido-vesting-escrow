import brownie

def test_locked_unclaimed(chain, activated_vesting, end_time):
    assert activated_vesting.locked() == activated_vesting.total_locked()
    assert activated_vesting.unclaimed() == 0
    chain.sleep(end_time - chain.time())
    chain.mine()
    assert activated_vesting.locked() == 0
    assert activated_vesting.unclaimed() == activated_vesting.total_locked()
    activated_vesting.claim({"from": activated_vesting.recipient()})
    assert activated_vesting.unclaimed() == 0

def test_locked_unclaimed_not_activated(ya_deployed_vesting, owner, token, balance):
    assert ya_deployed_vesting.locked() == 0
    assert ya_deployed_vesting.unclaimed() == 0
    token._mint_for_testing(balance, {"from": owner})
    token.transfer(ya_deployed_vesting, balance, {"from": owner})
    assert ya_deployed_vesting.locked() == 0
    assert ya_deployed_vesting.unclaimed() == 0
