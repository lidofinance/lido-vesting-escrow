"""
Usage:
    brownie run --network mainnet-fork build_multisig_tx main input.csv [test]
"""
import csv
import os
from hashlib import sha256
from typing import NamedTuple, TypedDict

from ape_safe import ApeSafe, Safe
from brownie import Contract, VestingEscrow, VestingEscrowFactory, VotingAdapter  # type: ignore
from brownie.network.transaction import TransactionReceipt
from eth_utils.conversions import to_bytes, to_hex
from gnosis.safe import SafeTx
from utils import log
from web3 import Web3


def main(csv_filename: str, non_empty_for_testing=None):
    """Build vesting contracts deployment tx by parameters defined in CSV file"""
    if non_empty_for_testing:
        log.warn("Using fake factory")

    config = read_envs()
    safe = ApeSafe(config["SAFE_ADDRESS"])

    factory_address = _test_factory_address(safe) if non_empty_for_testing else config["FACTORY_ADDRESS"]
    factory = VestingEscrowFactory.at(
        address=factory_address,
        owner=safe.address,
    )

    log.info("Deploy vestings on forked network")
    deployments = []
    raw_params_list = read_checksumed_csv(csv_filename)
    for raw_params in raw_params_list:
        params = VestingParams.from_tuple(raw_params)
        tx = factory.deploy_vesting_contract(
            params.amount,
            params.recipient,
            params.vesting_duration,
            params.vesting_start,
            params.cliff_length,
            params.is_fully_revokable,
            {"from": safe.address},
        )
        deployments.append((params, tx))

    log.info("Validate deployed vestings")
    params: VestingParams
    tx: TransactionReceipt
    for params, tx in deployments:
        log.info(f"Checking {tx.return_value} vesting for recipient {params.recipient}")
        if not tx.return_value:
            raise ValueError(f"Unable to find created contract address in {tx=}")
        contract = VestingEscrow.at(tx.return_value)
        check_deployed_vesting(contract, params)

    log.info("Constructing multisend transaction")
    safe_tx = safe.multisend_from_receipts()
    safe.preview(safe_tx)  # does not too much

    if log.prompt_yes_no("sign with frame?"):
        safe.sign_with_frame(safe_tx)
    else:  # sign with browine account
        safe.sign_transaction(safe_tx)

    if log.prompt_yes_no("propose transaction?"):
        if non_empty_for_testing:
            if not log.prompt_yes_no("testing mode is enabled, are you sure to continue?"):
                return
        safe.post_transaction(safe_tx)


class Config(TypedDict):
    """Configuration of the script"""

    FACTORY_ADDRESS: str
    SAFE_ADDRESS: str


def read_envs() -> Config:
    """Read environment variables to Config object"""
    config = os.environ.copy()

    for k in config.copy():
        if k not in Config.__annotations__:
            del config[k]

    for k in Config.__required_keys__:  # type: ignore
        if k not in config:
            raise RuntimeError(f"Required variable={k} not found")

    return Config(**config)


# def read_factory_address() -> str:
#     """Read address of VestingEscrowFactory from deployment json"""
#     try:
#         return read_or_update_state()["factoryAddress"]
#     except KeyError as e:
#         raise RuntimeError("Unable to found fatory address in json file") from e


def read_checksumed_csv(filename: str) -> list[tuple]:
    """Read checksum-protected CSV file"""
    validate_file_sha256(filename)

    with open(filename, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        return [tuple(row) for row in reader]


def validate_file_sha256(filename: str) -> None:
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


def check_deployed_vesting(contract: Contract, params: VestingParams) -> None:
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
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0xffffffffffffffffffffffffffffffffffffffff",
        "0x0000000000000000000000000000000000000000",
        adapter,
        {"from": "0x1111111111111111111111111111111111111111"},
    )
    ldo.transferFrom(lido_treasury, safe.address, 100_500, {"from": lido_treasury})
    ldo.approve(factory_address, 100_500, {"from": safe.address})
    history.clear()  # to avoid these transactions to occur in multisend

    return factory_address
