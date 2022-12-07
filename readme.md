# Lido Vesting Escrow (WIP)

A deeply modified version of [Yearn Vesting Escrow](https://github.com/banteg/yearn-vesting-escrow) contracts with added functionality:
- `rug_pull` method is renamed to `revoke_unvested`
- `admin` role is renamed to `manager`
- Added new role `owner`
- Added new escrow type [`VestingEscrowFullyRevokable`](contracts/VestingEscrowFullyRevokable.vy) with `revoke_all` method that allows `owner` to revoke ALL tokens form escrow. This is required for legal optimization (in terms of legal token ownership) 
- Added methods:
    - `aragon_vote` method for Aragon voting participation
    - `snapshot_set_delegate` method for Snapshot voting delegation,
    - `delegate` method for further voting power delegation 
    
- Voting methods operate over upgradable middleware to encounter possible changes in voting interfaces
- Added `recover_erc20` and `recover_ether` methods
- Existing methods and events refined

## Contracts

- [`VestingEscrowFactory`](contracts/VestingEscrowFactory.vy): Factory to deploy many simplified vesting contracts
- [`VestingEscrowSimple`](contracts/VestingEscrowSimple.vy): Simplified vesting contract that holds tokens for a single beneficiary
- [`VestingEscrowFullyRevokable`](contracts/VestingEscrowFullyRevokable.vy): Fully revocable vesting contract that holds tokens for a single beneficiary
- [`VotingAdapter`](contracts/VotingAdapter.vy): Middleware for voting with tokens under vesting

## Usage

```python
$ brownie console --network mainnet
funder = accounts.load(name)
factory = VestingEscrowFactory.at('address_of_the_deployed_VestingEscrowFactory', owner=funder)
factory.deploy_vesting_contract(token, recipient, amount, vesting_duration, vesting_start, cliff_length)
```

## Ethereum mainnet deployment

TBD

## Ethereum Goerly testnet deployment

TBD
