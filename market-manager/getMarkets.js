const gnosis = require("gnosisjs");
const configObject = require("./config.js");
const BigNumber = require('bignumber.js');
const filters = {
  tags: "twitter",
  include_whitelisted_oracles: true,
  oracle_addresses: "0x0"
};

gnosis.config.initialize(
  configObject
)
.then(
  (config) => {
    gnosis.api.getContracts({}, config)
    .then(
      (addresses) => {
        let offChainOracles = addresses.data.offChainOracles.map(oracle => oracle.address);
        gnosis.state.updateEventDescriptions(config, filters)
        .then(
          (descriptions) => {
            return gnosis.state.updateEvents(config, offChainOracles)
            .then(
              (eventHashes) => {
                let marketAddresses = addresses.data.markets.map(market => market.address);
                let marketsPromises = marketAddresses.map(
                  (marketAddress) => {
                    return gnosis.state.updateMarkets(config, offChainOracles, marketAddress)
                  }
                );

                Promise
                .all(marketsPromises)
                .then(
                  (markets) => {
                    let result = markets.map(
                      (marketCollection) => {
                        return Object.keys(marketCollection).map(
                          (marketHash) => {
                            let market = marketCollection[marketHash];
                            let eventObj = market.getEvent();
                            let description = eventObj.getEventDescription();
                            let prices = [];

                            if (description.descriptionJSON.outcomes) {
                              for (let i=0; i<description.descriptionJSON.outcomes.length; i++) {
                                prices.push(
                                  gnosis.marketMaker.calcPrice(
                                    market.shares,
                                    new BigNumber(0),
                                    market.initialFunding
                                  )
                                );
                              }
                            }
                            else {
                              let domain = [
                                eventObj.lowerBound.div('1e' + description.descriptionJSON.decimals).toNumber(),
                                eventObj.upperBound.div('1e' + description.descriptionJSON.decimals).toNumber()
                              ];

                              let boundOffset = eventObj.upperBound.minus(eventObj.lowerBound).div('1e' + description.descriptionJSON.decimals);

                              // Current price
                              prices.push(
                                gnosis.marketMaker.calcPrice(
                                  market.shares,
                                  new BigNumber(1),
                                  market.initialFunding
                                ).mul(boundOffset).plus(eventObj.lowerBound.div('1e' + description.descriptionJSON.decimals))
                              );
                            }

                            return {
                              marketHash: market.marketHash,
                              investor: market.investorAddress,
                              shares: market.shares,
                              description: description.descriptionJSON,
                              marketAddress: market.marketAddress,
                              prices: prices,
                              descriptionHash: description.descriptionHash
                            }
                          }
                        )
                      }
                    );

                    let resultFlattened = [].concat.apply([], result);
                    console.log(JSON.stringify(resultFlattened));
                  }
                );

              },
              process.exit
            );
          },
          process.exit
        );
      }
    );
  },
  process.exit
);
