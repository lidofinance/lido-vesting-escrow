import pytest

WEEK = 7 * 24 * 60 * 60  # seconds
YEAR = 365.25 * 24 * 60 * 60  # seconds


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


@pytest.fixture(scope="session")
def receiver(accounts):
    yield accounts.at("0x0000000000000000000000000000000000031337", True)

@pytest.fixture(scope="session")
def balance():
    return 10 ** 20

@pytest.fixture(scope="session")
def duration():
    yield int(3 * YEAR)


@pytest.fixture(scope="module")
def token(ERC20, accounts):
    yield ERC20.deploy("Lido Token", "LFI", 18, {"from": accounts[0]})


@pytest.fixture(scope="module")
def voting(Voting, accounts, token):
    yield Voting.deploy(token, {"from": accounts[0]})


@pytest.fixture(scope="module")
def delegate(Delegate, accounts):
    yield Delegate.deploy({"from": accounts[0]})


@pytest.fixture(scope="module")
def start_time(chain):
    yield chain.time() + 1000 + 86400 * 365


@pytest.fixture(scope="module")
def end_time(start_time, duration):
    yield int(start_time + duration)


@pytest.fixture(scope="module")
def vesting_target_simple(VestingEscrowSimple, accounts, voting, delegate):
    yield VestingEscrowSimple.deploy(voting, delegate, {"from": accounts[0]})


@pytest.fixture(scope="module")
def vesting_target_fully_revokable(VestingEscrowFullyRevokable, accounts, voting, delegate):
    yield VestingEscrowFullyRevokable.deploy(voting, delegate, {"from": accounts[0]})


@pytest.fixture(scope="module")
def vesting_factory(VestingEscrowFactory, accounts, vesting_target_simple, vesting_target_fully_revokable):
    yield VestingEscrowFactory.deploy(vesting_target_simple, vesting_target_fully_revokable, {"from": accounts[0]})


@pytest.fixture(scope="module", params=[0,1])
def vesting(VestingEscrowSimple, VestingEscrowFullyRevokable, accounts, vesting_factory, token, start_time, duration, request, balance):
    token._mint_for_testing(balance, {"from": accounts[0]})
    token.approve(vesting_factory, balance, {"from": accounts[0]})
    tx = vesting_factory.deploy_vesting_contract(
        token,
        accounts[1],
        balance,
        duration,  # duration
        start_time,
        0,  # cliff
        request.param,
        {"from": accounts[0]},
    )
    if request.param == 1:
        yield VestingEscrowFullyRevokable.at(tx.new_contracts[0])
    else:
        yield VestingEscrowSimple.at(tx.new_contracts[0])
