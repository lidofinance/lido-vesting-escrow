"""
Usage:
    brownie run --network mainnet-fork multisig_tx build input.csv [test!]
    brownie run --network mainnet-fork multisig_tx check 0xsafeTxHash input.csv
"""
import csv
import os
from hashlib import sha256
from typing import NamedTuple, TypedDict

from ape_safe import ApeSafe, Safe
from brownie import Contract, VestingEscrow, VestingEscrowFactory, VotingAdapter  # type: ignore
from brownie.network.transaction import TransactionReceipt
from utils import log


def build(csv_filename: str, non_empty_for_testing=None):
    """Build vesting contracts deployment tx by parameters defined in CSV file"""
    is_testing = bool(non_empty_for_testing)
    if is_testing:
        log.warn("Using fake factory")

    config = _read_envs()
    safe = ApeSafe(config["SAFE_ADDRESS"])

    factory_address = _test_factory_address(safe) if non_empty_for_testing else config["FACTORY_ADDRESS"]
    factory = VestingEscrowFactory.at(
        address=factory_address,
        owner=safe.address,
    )

    log.info("Constructing multisend transaction")
    raw_params_list = _read_checksumed_csv(csv_filename)
    params_list = []
    for raw_params in raw_params_list:
        params = VestingParams.from_tuple(raw_params)
        params_list.append(params)
        tx = factory.deploy_vesting_contract(
            params.amount,
            params.recipient,
            params.vesting_duration,
            params.vesting_start,
            params.cliff_length,
            params.is_fully_revokable,
            {"from": safe.address},
        )
    safe_tx = safe.multisend_from_receipts()
    # do not reset chain in testing to keep the fake factory and other contracts intact
    tx = safe.preview(safe_tx, reset=not is_testing)
    _check_tx(tx, params_list)

    if log.prompt_yes_no("sign with frame?"):
        safe.sign_with_frame(safe_tx)
    else:
        log.error("transaction signature required!")
        return

    if log.prompt_yes_no("propose transaction?"):
        if is_testing:
            if not log.prompt_yes_no("testing mode is enabled, are you sure to continue?"):
                return
        safe.post_transaction(safe_tx)


def check(safe_tx_hash: str, csv_filename: str) -> None:
    """Check the given safeTxHash against the given CSV"""
    config = _read_envs()
    safe = ApeSafe(config["SAFE_ADDRESS"])

    params_list = [VestingParams.from_tuple(p) for p in _read_checksumed_csv(csv_filename)]
    safe_tx = safe.get_safe_tx_by_safe_tx_hash(safe_tx_hash)
    tx = safe.preview(safe_tx)
    _check_tx(tx, params_list)

    if log.prompt_yes_no("sign transaction?"):
        safe.sign_with_frame(safe_tx)


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


def _read_checksumed_csv(filename: str) -> list[tuple]:
    """Read checksum-protected CSV file"""
    _validate_file_sha256(filename)

    with open(filename, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        return [tuple(row) for row in reader]


def _validate_file_sha256(filename: str) -> None:
    """Read filename checksum from filename.sum file and compare with the actual one"""
    if not os.path.exists(filename):
        raise AssertionError(f"{filename} does not exist")

    checksum_filename = filename + ".sum"
    if not os.path.exists(checksum_filename):
        raise AssertionError(f"{checksum_filename} does not exist")

    with open(checksum_filename, encoding="utf-8") as f:
        checksum = f.readline().split()[0].strip()

    with open(filename, mode="rb") as f:
        calculated_checksum = sha256(f.read()).hexdigest()

    if calculated_checksum != checksum:
        raise AssertionError(f"Checksum mismatch, read: {checksum}, actual: {calculated_checksum}")


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


def _check_tx(tx: TransactionReceipt, params_list: list[VestingParams]) -> None:
    """Check contracts created by the transaction against the parsed vesting parameters"""
    log.info("Validate contracts from multisend transaction")

    if not tx.new_contracts and len(params_list) or len(params_list) != len(tx.new_contracts):
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


def _check_deployed_vesting(contract: Contract, params: VestingParams) -> None:
    """Compare the values returned by contract view functions with the values of VestingParams argument"""

    def require(field: str, expected):
        result = getattr(contract, field)()
        if result != expected:
            raise AssertionError(f"{contract}.{field} = {result}, expected: {expected}")

    require("total_locked", params.amount)
    require("recipient", params.recipient)
    require("start_time", params.vesting_start)
    require("end_time", params.vesting_start + params.vesting_duration)
    require("is_fully_revokable", params.is_fully_revokable)
    require("is_fully_revoked", False)
    require("initialized", True)


def _test_factory_address(safe: Safe) -> str:
    from brownie import history

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
    factory_address = VestingEscrowFactory.deploy(
        vesting,
        "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",  # LDOs
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0x0000000000000000000000000000000000000000",
        adapter,
        {"from": "0x1111111111111111111111111111111111111111"},
    )
    ldo.transferFrom(lido_treasury, safe.address, 100_500, {"from": lido_treasury})
    ldo.approve(factory_address, 100_500, {"from": safe.address})
    history.clear()  # to avoid these transactions to occur in multisend

    return factory_address
