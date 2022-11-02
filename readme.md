# Lido Vesting Escrow (WIP)

A modified version of [Yearn Vesting Escrow](https://github.com/banteg/yearn-vesting-escrow) contracts with added functionality:
- `rug_pull` method is renamed to `suspend_and_revoke_unvested`
- `admin` role is renamed to `manager`
- Added new escrow type [`VestingEscrowOptimized`](contracts/VestingEscrowOptimized.vy) with `suspend_and_revoke_all` method and `admin` role that allows `admin` to revoke ALL tokens form escrow. This is required for legal optimization (in terms of legal token ownership) 

## Contracts

- [`VestingEscrowFactory`](contracts/VestingEscrowFactory.vy): Factory to deploy many simplified vesting contracts
- [`VestingEscrowSimple`](contracts/VestingEscrowSimple.vy): Simplified vesting contract that holds tokens for a single beneficiary
- [`VestingEscrowOptimized`](contracts/VestingEscrowOptimized.vy): Optimized vesting contract that holds tokens for a single beneficiary

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
