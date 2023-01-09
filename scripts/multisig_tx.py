"""
Usage:
    brownie run multisig_tx build input.csv [prod!]
    brownie run multisig_tx check 0xsafeTxHash input.csv
"""
import csv
import os
from hashlib import sha256
from typing import NamedTuple, Sequence, TypedDict

from ape_safe import ApeSafe, SafeTx
from brownie import ERC20  # type: ignore
from brownie import VestingEscrow  # type: ignore
from brownie import VestingEscrowFactory  # type: ignore
from brownie import VotingAdapter  # type: ignore
from brownie import Contract, chain, network
from brownie.network.transaction import TransactionReceipt

from utils import log
from utils.helpers import chain_snapshot

LDO_ADDRESS = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"


def build(csv_filename: str, non_empty_for_prod=None):
    """Build vesting contracts deployment tx by parameters defined in CSV file"""
    is_prod = bool(non_empty_for_prod)
    if is_prod:
        log.warn("SCRIPT RUNNED IN PRODUCTION ENV")
        if not log.prompt_yes_no("ARE YOU SURE TO CONTINUE?"):
            log.warn("Script aborted")
            return

    _assert_mainnet_fork()
    config = _read_envs()

    log.info("Reading input file")
    raw_params_list = _read_csv(csv_filename)
    params_list = tuple(VestingParams.from_tuple(p) for p in raw_params_list)

    safe = ApeSafe(config["SAFE_ADDRESS"])

    factory_address = config["FACTORY_ADDRESS"]
    factory = VestingEscrowFactory.at(
        address=factory_address,
        owner=safe.address,
    )

    log.info("Checking multisig balance")
    starting_balance = _ldo_balance(safe.address)
    vestings_sum = sum(p.amount for p in params_list)
    assert starting_balance >= vestings_sum, f"Not enough LDOs for vesting, need at least {vestings_sum / 10 ** 18}"

    log.info("Constructing multisend transaction")
    with chain_snapshot():
        for params in params_list:
            factory.deploy_vesting_contract(
                params.amount,
                params.recipient,
                params.vesting_duration,
                params.vesting_start,
                params.cliff_length,
                params.is_fully_revokable,
                {"from": safe.address},
            )
        safe_tx = safe.multisend_from_receipts()

    _preview_and_check_tx(safe, safe_tx, params_list, is_prod)

    if log.prompt_yes_no("Sign with frame?"):
        safe.sign_with_frame(safe_tx)
        log.info("Transaction signed")
    elif is_prod:
        log.error("Signature required")
        return

    if not is_prod:
        log.warn("Testing flow is finished")
        return

    if log.prompt_yes_no("Post transaction?"):
        safe.post_transaction(safe_tx)
        log.okay("Done")


def check(safe_tx_hash: str, csv_filename: str) -> None:
    """Check the given safeTxHash against the given CSV"""
    _assert_mainnet_fork()
    config = _read_envs()

    log.info("Reading input file")
    raw_params_list = _read_csv(csv_filename)
    params_list = [VestingParams.from_tuple(p) for p in raw_params_list]

    safe = ApeSafe(config["SAFE_ADDRESS"])

    log.info("Retrieving transaction from Gnosis Safe")
    safe_tx = safe.get_safe_tx_by_safe_tx_hash(safe_tx_hash)
    _preview_and_check_tx(safe, safe_tx, params_list, is_prod=True)


def sign(safe_tx_hash: str) -> None:
    """Sign the given transaction"""
    config = _read_envs()
    safe = ApeSafe(config["SAFE_ADDRESS"])

    log.info("Retrieving transaction from Gnosis Safe")
    safe_tx = safe.get_safe_tx_by_safe_tx_hash(safe_tx_hash)

    if log.prompt_yes_no("Sign transaction?"):
        signature = safe.sign_with_frame(safe_tx)
        if log.prompt_yes_no("Post signature?"):
            safe.post_signature(safe_tx, signature)


def fake_factory() -> None:
    """Use to deploy factory for testing purpose"""
    from brownie import history

    config = _read_envs()
    safe = ApeSafe(config["SAFE_ADDRESS"])

    lido_treasury = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c"  # some address with LDOs
    ldo = Contract.from_explorer("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")
    vesting = VestingEscrow.deploy({"from": safe.address})
    adapter = VotingAdapter.deploy(
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0xffffffffffffffffffffffffffffffffffffffff",
        {"from": "0x1111111111111111111111111111111111111111"},
    )
    factory = VestingEscrowFactory.deploy(
        vesting,
        LDO_ADDRESS,
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0x0000000000000000000000000000000000000000",
        adapter,
        {"from": "0x1111111111111111111111111111111111111111"},
    )
    ldo.transfer(safe.address, 100_000 * 10**18, {"from": lido_treasury})
    ldo.approve(factory, 100_000 * 10**18, {"from": safe.address})
    history.clear()  # to avoid these transactions to occur in multisend

    log.info(f"{factory.address=}")
    input("Press ENTER to exit...")


def _preview_and_check_tx(safe: ApeSafe, safe_tx: SafeTx, params_list: Sequence["VestingParams"], is_prod=False):
    vestings_sum = sum(p.amount for p in params_list)
    starting_balance = _ldo_balance(safe.address)

    log.info("Preview transaction")
    # do not reset chain in testing to keep the fake factory and other contracts intact
    tx = safe.preview(safe_tx, reset=is_prod)

    log.info("Check LDO balance change")
    ending_balance = _ldo_balance(safe.address)
    assert starting_balance - ending_balance == vestings_sum, "LDOs difference after deploy mismatch"

    # give some time to inspect the output before to continue
    if not log.prompt_yes_no("Continue?"):
        return log.warn("Script aborted")

    log.info("Check individual vestings")
    _check_tx(tx, params_list)


class Config(TypedDict):
    """Configuration of the script"""

    FACTORY_ADDRESS: str
    SAFE_ADDRESS: str


def _read_envs() -> Config:
    """Read environment variables to Config object"""
    config = os.environ.copy()

    for k in config.copy():
        if k not in Config.__annotations__:
            del config[k]

    for k in Config.__required_keys__:  # type: ignore
        if k not in config:
            raise RuntimeError(f"Required variable={k} not found")

    return Config(**config)


def _read_csv(filename: str) -> list[tuple]:
    """Read checksum-protected CSV file"""
    chksum = _get_file_sha256(filename)
    if not log.prompt_yes_no(f"File's checksum: {chksum}, is it correct?"):
        log.warn("Aborted!")
        exit(1)

    with open(filename, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        return [tuple(row) for row in reader]


def _get_file_sha256(filename: str) -> str:
    """Read filename checksum from filename.sum file and compare with the actual one"""
    assert os.path.exists(filename), f"{filename} does not exist"

    with open(filename, mode="rb") as f:
        return sha256(f.read()).hexdigest()


class VestingParams(NamedTuple):
    """Tuple of parameters to read from CSV line"""

    amount: int
    recipient: str
    vesting_duration: int
    vesting_start: int
    cliff_length: int
    is_fully_revokable: bool

    @classmethod
    def from_tuple(cls, tupl: tuple) -> "VestingParams":
        """Construct new VestingParams from tuple of strings"""
        if len(tupl) != len(cls._fields):
            raise ValueError("Fields length mismatch to construct VestingParams")
        return cls(
            int(tupl[0]),
            tupl[1],
            int(tupl[2]),
            int(tupl[3]),
            int(tupl[4]),
            tupl[5] == "1",
        )

def _assert_mainnet_fork():
    """Check that scripts is running on mainnet-fork network"""
    if network.show_active() != "mainnet-fork":
        log.error("Script requires mainnet-fork network")
        exit(1)

def _ldo_balance(account) -> int:
    """Get balance of account in LDOs"""
    ldo = ERC20.at(LDO_ADDRESS)
    return ldo.balanceOf(account)


def _check_tx(tx: TransactionReceipt, params_list: Sequence[VestingParams]) -> None:
    """Check contracts created by the transaction against the parsed vesting parameters"""
    log.info("Validate contracts from multisend transaction")

    new_contracts_count = len(tx.new_contracts) if tx.new_contracts else 0
    if len(params_list) != new_contracts_count:
        raise RuntimeError("Deployed contracts count mismatch")

    address: str
    for address in tx.new_contracts:
        contract = VestingEscrow.at(address)
        recipient = contract.recipient()
        try:
            [params] = [p for p in params_list if p.recipient == recipient]
        except ValueError as e:
            raise ValueError(f"Recipient {recipient} not found in source") from e
        _check_deployed_vesting(contract, params)
        log.okay(f"{recipient=} vesting at {address=} checked")


def _check_deployed_vesting(contract: VestingEscrow, params: VestingParams) -> None:
    """Compare the values returned by contract view functions with the values of VestingParams argument"""

    def assert_field_value(field: str, expected):
        actual = getattr(contract, field)()
        assert actual == expected, f"{contract}.{field} = {actual}, expected: {expected}"

    assert_field_value("total_locked", params.amount)
    assert_field_value("recipient", params.recipient)
    assert_field_value("start_time", params.vesting_start)
    assert_field_value("end_time", params.vesting_start + params.vesting_duration)
    assert_field_value("is_fully_revokable", params.is_fully_revokable)
    assert_field_value("is_fully_revoked", False)
    assert_field_value("initialized", True)

    assert _ldo_balance(contract) == params.amount, "Vesting's LDO balance mismatch"
    _test_claim(contract, params)


def _test_claim(vesting: VestingEscrow, params: VestingParams) -> None:
    def assert_claimable(step: str):
        assert vesting.unclaimed() > 0, f"Nothing to claim after {step}"
        recipient = params.recipient
        s = _ldo_balance(recipient)
        assert vesting.claim({"from": recipient})
        e = _ldo_balance(recipient)
        assert e > s, f"No balance change on claim() after {step}"

    with chain_snapshot():
        # 1. before start
        if params.vesting_start > chain.time():
            assert vesting.unclaimed() == 0, "Unexpected claimable before start"

    with chain_snapshot():
        cliff_end = params.vesting_start + params.cliff_length
        if cliff_end >= chain.time():
            # 2. before cliff
            assert vesting.unclaimed() == 0, "Unexpected claimable before cliff"
            chain.sleep(cliff_end - chain.time() + 1)
            chain.mine()
        # 3. after cliff
        assert_claimable(step="cliff")

    with chain_snapshot():
        # 4. after end
        vesting_end = params.vesting_start + params.vesting_duration
        if vesting_end >= chain.time():
            chain.sleep(vesting_end - chain.time() + 1)
            chain.mine()
        assert_claimable(step="end")
