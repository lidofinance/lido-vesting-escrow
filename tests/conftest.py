import pytest

WEEK = 7 * 24 * 60 * 60  # seconds
YEAR = 365.25 * 24 * 60 * 60  # seconds


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


@pytest.fixture(scope="session")
def balance():
    return 10**20


@pytest.fixture(scope="session")
def owner(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def manager(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
def recipient(accounts):
    return accounts[2]


@pytest.fixture(scope="session")
def random_guy(accounts):
    return accounts[3]


@pytest.fixture(scope="session", params=["manager", "recipient", "random_guy"])
def not_owner(manager, recipient, random_guy, request):
    if request.param == "manager":
        return manager
    if request.param == "recipient":
        return recipient
    if request.param == "random_guy":
        return random_guy


@pytest.fixture(scope="session", params=["manager", "owner", "random_guy"])
def not_recipient(manager, owner, random_guy, request):
    if request.param == "manager":
        return manager
    if request.param == "owner":
        return owner
    if request.param == "random_guy":
        return random_guy


@pytest.fixture(scope="session")
def duration():
    return int(3 * YEAR)


@pytest.fixture(scope="module")
def token(ERC20, accounts):
    return ERC20.deploy("Lido Token", "LFI", 18, {"from": accounts[0]})


@pytest.fixture(scope="module")
def voting(Voting, token, owner):
    return Voting.deploy(token, {"from": owner})


@pytest.fixture(scope="module")
def delegate(Delegate, owner):
    return Delegate.deploy({"from": owner})


@pytest.fixture(scope="module")
def voting_adapter(VotingAdapter, owner):
    return VotingAdapter.deploy({"from": owner})


@pytest.fixture(scope="module")
def voting_adapter_for_update(VotingAdapter, owner):
    return VotingAdapter.deploy({"from": owner})


@pytest.fixture(scope="module")
def start_time(chain):
    return chain.time() + 1000 + 86400 * 365


@pytest.fixture(scope="module")
def end_time(start_time, duration):
    return int(start_time + duration)


@pytest.fixture(scope="module")
def vesting_target_simple(VestingEscrow, owner, voting, delegate):
    return VestingEscrow.deploy(voting, delegate, {"from": owner})


@pytest.fixture(scope="module")
def vesting_target_fully_revokable(
    VestingEscrowFullyRevokable, owner, voting, delegate
):
    return VestingEscrowFullyRevokable.deploy(voting, delegate, {"from": owner})


@pytest.fixture(scope="module")
def vesting_factory(
    VestingEscrowFactory,
    owner,
    vesting_target_simple,
    vesting_target_fully_revokable,
    voting_adapter,
):
    return VestingEscrowFactory.deploy(
        vesting_target_simple,
        vesting_target_fully_revokable,
        voting_adapter,
        {"from": owner},
    )


@pytest.fixture(
    scope="module",
    params=[pytest.param(0, id="simple"), pytest.param(1, id="fully_revocable")],
)
def deployed_vesting(
    VestingEscrow,
    VestingEscrowFullyRevokable,
    recipient,
    vesting_factory,
    token,
    start_time,
    duration,
    owner,
    manager,
    request,
    balance,
):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        balance,
        recipient,
        owner,
        duration,  # duration
        start_time,
        0,  # cliff
        request.param,
        manager,
        {"from": recipient},
    )
    if request.param == 1:
        return VestingEscrowFullyRevokable.at(tx.new_contracts[0])
    else:
        return VestingEscrow.at(tx.new_contracts[0])


@pytest.fixture(scope="module")
def funded_vesting(
    deployed_vesting,
    owner,
    balance,
    token,
):
    token._mint_for_testing(balance, {"from": owner})
    token.transfer(deployed_vesting, balance, {"from": owner})
    return deployed_vesting


@pytest.fixture(scope="module")
def activated_vesting(
    funded_vesting,
    recipient,
):
    funded_vesting.activate({"from": recipient})
    return funded_vesting


@pytest.fixture(
    scope="module",
    params=[pytest.param(0, id="simple"), pytest.param(1, id="fully_revocable")],
)
def ya_deployed_vesting(
    VestingEscrow,
    VestingEscrowFullyRevokable,
    recipient,
    vesting_factory,
    token,
    start_time,
    duration,
    owner,
    balance,
    manager,
    request,
):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        balance,
        recipient,
        owner,
        duration,  # duration
        start_time,
        0,  # cliff
        request.param,
        manager,
        {"from": recipient},
    )

    if request.param == 1:
        return VestingEscrowFullyRevokable.at(tx.new_contracts[0])
    else:
        return VestingEscrow.at(tx.new_contracts[0])


@pytest.fixture(scope="module")
def ya_funded_vesting(
    ya_deployed_vesting,
    owner,
    balance,
    token,
):
    token._mint_for_testing(balance, {"from": owner})
    token.transfer(ya_deployed_vesting, balance, {"from": owner})
    return ya_deployed_vesting
