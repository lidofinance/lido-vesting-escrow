import pytest
from brownie import ZERO_ADDRESS

WEEK = 7 * 24 * 60 * 60  # seconds
YEAR = 365.25 * 24 * 60 * 60  # seconds


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


@pytest.fixture(scope="session")
def balance():
    return 10**20


@pytest.fixture(scope="session")
def one_eth():
    return 10**18


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


@pytest.fixture(scope="session", params=["owner", "manager", "recipient", "random_guy"])
def anyone(owner, manager, recipient, random_guy, request):
    if request.param == "manager":
        return manager
    if request.param == "recipient":
        return recipient
    if request.param == "owner":
        return owner
    if request.param == "random_guy":
        return random_guy


@pytest.fixture(scope="session")
def duration():
    return int(3 * YEAR)


@pytest.fixture(scope="session")
def cliff():
    return int(1 * YEAR)


@pytest.fixture(scope="module")
def token(ERC20, accounts):
    return ERC20.deploy("Lido Token", "LFI", 18, {"from": accounts[0]})


@pytest.fixture(scope="module")
def voting(Voting, token, owner):
    return Voting.deploy(token, {"from": owner})


@pytest.fixture(scope="module")
def snapshot_delegate(Delegate, owner):
    return Delegate.deploy({"from": owner})


@pytest.fixture(scope="module")
def voting_adapter(VotingAdapter, owner, voting, snapshot_delegate):
    return VotingAdapter.deploy(voting, snapshot_delegate, ZERO_ADDRESS, owner, {"from": owner})


@pytest.fixture(scope="module")
def voting_adapter_for_update(VotingAdapter, owner, voting, snapshot_delegate):
    return VotingAdapter.deploy(voting, snapshot_delegate, ZERO_ADDRESS, owner, {"from": owner})


@pytest.fixture(scope="module")
def destructible(SelfDestructible, owner):
    return SelfDestructible.deploy({"from": owner})


@pytest.fixture(scope="module")
def start_time(chain):
    return chain.time() + 1000 + 86400 * 365


@pytest.fixture(scope="module")
def end_time(start_time, duration):
    return int(start_time + duration)


@pytest.fixture(scope="module")
def vesting_target(VestingEscrow, owner):
    return VestingEscrow.deploy({"from": owner})


@pytest.fixture(scope="module")
def vesting_factory(
    VestingEscrowFactory,
    owner,
    vesting_target,
    manager,
    token,
    voting_adapter,
):
    return VestingEscrowFactory.deploy(
        vesting_target,
        token,
        owner,
        manager,
        voting_adapter,
        {"from": owner},
    )


@pytest.fixture(
    scope="module",
    params=[pytest.param(0, id="simple")],
)
def deployed_vesting(
    VestingEscrow,
    recipient,
    vesting_factory,
    token,
    start_time,
    duration,
    owner,
    request,
    balance,
):
    token._mint_for_testing(balance, {"from": owner})
    token.approve(vesting_factory, balance, {"from": owner})
    tx = vesting_factory.deploy_vesting_contract(
        balance,
        recipient,
        duration,
        start_time,
        0,  # cliff
        request.param,
        {"from": owner},
    )
    return VestingEscrow.at(tx.new_contracts[0])


@pytest.fixture(
    scope="module",
    params=[pytest.param(0, id="simple")],
)
def deployed_vesting_with_cliff(
    VestingEscrow,
    recipient,
    vesting_factory,
    token,
    start_time,
    duration,
    cliff,
    owner,
    request,
    balance,
):
    token._mint_for_testing(balance, {"from": owner})
    token.approve(vesting_factory, balance, {"from": owner})
    tx = vesting_factory.deploy_vesting_contract(
        balance,
        recipient,
        duration,
        start_time,
        cliff,
        request.param,
        {"from": owner},
    )
    return VestingEscrow.at(tx.new_contracts[0])
