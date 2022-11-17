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
    request,
):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        recipient,
        duration,  # duration
        start_time,
        0,  # cliff
        request.param,
        {"from": owner},
    )
    if request.param == 1:
        return VestingEscrowFullyRevokable.at(tx.new_contracts[0])
    else:
        return VestingEscrow.at(tx.new_contracts[0])


@pytest.fixture(scope="module")
def ya_deployed_vesting(
    VestingEscrow,
    recipient,
    vesting_factory,
    token,
    start_time,
    duration,
    owner,
):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        recipient,
        duration,  # duration
        start_time,
        0,  # cliff
        {"from": owner},
    )

    return VestingEscrow.at(tx.new_contracts[0])


@pytest.fixture(scope="module")
def hundred_deployed_vestings(
    VestingEscrow,
    recipient,
    vesting_factory,
    token,
    start_time,
    duration,
    owner,
):
    vestings = []
    for i in range(100):
        tx = vesting_factory.deploy_vesting_contract(
            token,
            recipient,
            duration,  # duration
            start_time,
            0,  # cliff
            {"from": owner},
        )

        vestings.append(VestingEscrow.at(tx.new_contracts[0]))

    return vestings


@pytest.fixture(scope="module")
def activated_vesting(
    deployed_vesting,
    vesting_factory,
    owner,
    manager,
    balance,
    token,
):
    token._mint_for_testing(balance, {"from": owner})
    token.approve(vesting_factory, balance, {"from": owner})
    vesting_factory.activate_vesting_contract(
        deployed_vesting.address,
        balance,
        manager,
        {"from": owner},
    )
    return deployed_vesting
