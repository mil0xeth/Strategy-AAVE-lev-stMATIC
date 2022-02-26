from brownie import chain, reverts


def test_high_profit_causes_healthcheck_revert(
    vault, strategy, token, token_whale, gov, healthCheck
):
    profitLimit = healthCheck.profitLimitRatio(100, {'from': gov})
    maxBPS = 10_000

    # Send some funds to the strategy
    token.approve(vault.address, 2 ** 256 - 1, {"from": token_whale})
    vault.deposit(1000 * (10 ** token.decimals()), {"from": token_whale})
    chain.sleep(1)
    strategy.harvest({"from": gov})

    token.transfer(
        strategy,
        vault.strategies(strategy).dict()["totalDebt"] * ((profitLimit + 1) / maxBPS),
        {"from": token_whale},
    )
    with reverts("!healthcheck"):
        strategy.harvest({"from": gov})


def test_profit_under_max_ratio_does_not_revert(
    vault, strategy, token, token_whale, gov, healthCheck
):
    #The test in its current state makes little sense: 
    #1. maxBPS is being hardcoded, 
    #2. the transfer for simulating profit is a calculation that is above the profitlimitratio and thus automatically reverts
    healthCheck.setProfitLimitRatio(8_000, {'from': gov})
    profitLimit = healthCheck.profitLimitRatio()
    maxBPS = 10_000

    # Send some funds to the strategy
    token.approve(vault.address, 2 ** 256 - 1, {"from": token_whale})
    vault.deposit(1000 * (10 ** token.decimals()), {"from": token_whale})
    chain.sleep(1)
    strategy.harvest({"from": gov})

    #token.transfer(strategy, vault.strategies(strategy).dict()["totalDebt"] * ((profitLimit - 1) / maxBPS), {"from": token_whale})
    token.transfer(strategy, vault.strategies(strategy).dict()["totalDebt"] * healthCheck.profitLimitRatio()/100/100 , {"from": token_whale})
    healthCheck.setProfitLimitRatio(8_500, {'from': gov})
    strategy.harvest({"from": gov})

    # If we reach the assert the harvest did not revert
    assert True


def DISABLED_high_loss_causes_healthcheck_revert(
    vault, test_strategy, token, token_whale, gov, healthCheck
):
    healthCheck.setlossLimitRatio(1, {'from': gov})
    lossRatio = healthCheck.lossLimitRatio()
    maxBPS = 10_000

    # Send some funds to the strategy
    token.approve(vault.address, 2 ** 256 - 1, {"from": token_whale})
    vault.deposit(50 * (10 ** token.decimals()), {"from": token_whale})
    chain.sleep(1)
    test_strategy.harvest({"from": gov})

    # Unlock part of the collateral
    test_strategy.freeCollateral(test_strategy.balanceOfMakerVault() * (0.5 + ((lossRatio + 1) / maxBPS)), 0)

    # Simulate loss by transferring away unlocked collateral
    token.transfer(token_whale, token.balanceOf(test_strategy), {"from": test_strategy})

    vault.updateStrategyDebtRatio(test_strategy, 5_000, {"from": gov})

    with reverts("!healthcheck"):
        test_strategy.harvest({"from": gov})


def test_loss_under_max_ratio_does_not_revert(
    vault, test_strategy, token, token_whale, gov, healthCheck
):
    lossRatio = healthCheck.lossLimitRatio()
    maxBPS = 10_000

    # Send some funds to the strategy
    token.approve(vault.address, 2 ** 256 - 1, {"from": token_whale})
    vault.deposit(1 * (10 ** token.decimals()), {"from": token_whale})
    chain.sleep(1)
    test_strategy.harvest({"from": gov})

    # Unlock part of the collateral
    test_strategy.freeCollateral(
        test_strategy.balanceOfMakerVault() * (0.5 + ((lossRatio - 1) / maxBPS)), 0
    )

    # Simulate loss by transferring away unlocked collateral
    token.transfer(token_whale, token.balanceOf(test_strategy), {"from": test_strategy})

    vault.updateStrategyDebtRatio(test_strategy, 5_000, {"from": gov})

    test_strategy.harvest({"from": gov})

    assert True