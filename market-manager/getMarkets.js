const gnosis = require("gnosisjs");
const configObject = require("./config.js");
const Decimal = require('decimal.js');

const ProviderEngine = require('web3-provider-engine');
const RpcSubprovider = require('web3-provider-engine/subproviders/rpc.js')
const Web3 = require('web3');
const engine = new ProviderEngine();
const web3 = new Web3(engine);

const filters = {
  include_whitelisted_oracles: true,
  oracle_addresses: "0x0"
};

// Set web3
web3.eth.defaultAccount = '0xB42E70a3c6dd57003f4bFe7B06E370d21CDA8087'
engine.addProvider(new RpcSubprovider({
 rpcUrl: configObject.ethereumNodeURL,
}));
configObject.web3 = web3;
engine.start();

gnosis.config.initialize(
  configObject
)
.then(
  (config) => {
    gnosis.api.getContracts({}, config)
    .then(
      (addresses) => {
        gnosis.state.updateEventDescriptions(config, filters)
        .then(
          (descriptions) => {
            return gnosis.state.updateEvents(config)
            .then(
              (events) => {
                let marketAddresses = addresses.data.markets.map(market => market.address);
                let marketsPromises = marketAddresses.map(
                  (marketAddress) => {
                    return gnosis.state.updateMarkets(config, marketAddress, "0x7b2e78d4dfaaba045a167a70da285e30e8fca196")
                  }
                );

                Promise
                .all(marketsPromises)
                .then(
                  (markets) => {
                    let result = [];

                    function callbackResponse (obj, lastitem) {
                      result.push(obj);
                      if (lastitem == true) {
                        let resultFlattened = [].concat.apply([], result);
                        console.log(JSON.stringify(resultFlattened));                        
                        process.exit();
                      }
                    }

                    markets.map(
                      (marketCollection) => {

                        let count = 0;

                        return Object.keys(marketCollection).map(
                          (marketHash) => {
                            let market = marketCollection[marketHash];
                            let eventObj = market.getEvent();
                            let description = eventObj.getEventDescription();
                            let prices = [];

                            if (description.descriptionJSON.outcomes) {
                              for (let i=0; i<description.descriptionJSON.outcomes.length; i++) {
                                let price = gnosis.marketMaker.calcPrice(
                                  market.shares,
                                  new Decimal(0),
                                  market.initialFunding
                                );
                                price = price.toFixed(2);

                                prices.push(
                                  price
                                );
                              }
                            }
                            else {
                              let domain = [
                                eventObj.lowerBound.div('1e' + description.descriptionJSON.decimals).toNumber(),
                                eventObj.upperBound.div('1e' + description.descriptionJSON.decimals).toNumber()
                              ];

                              let boundOffset = eventObj.upperBound.minus(eventObj.lowerBound).div('1e' + description.descriptionJSON.decimals);

                              let price = gnosis.marketMaker.calcPrice(
                                market.shares,
                                new Decimal(1),
                                market.initialFunding
                              ).mul(boundOffset).plus(eventObj.lowerBound.div('1e' + description.descriptionJSON.decimals));

                              // Current price
                              prices.push(
                                price.toPrecision(Math.ceil(Math.log(boundOffset.toNumber())/Math.log(10))+2)
                              );
                            }

                            web3.eth.getBlock(parseInt(market.createdAtBlock), function (error, result) {
                                if (!error) {
                                    let createdAt = new Date(result.timestamp*1000).toISOString();
                                    let returnObject = {
                                      marketHash: market.marketHash,
                                      investor: market.investorAddress,
                                      shares: market.shares,
                                      description: description.descriptionJSON,
                                      marketAddress: market.marketAddress,
                                      prices: prices,
                                      descriptionHash: description.descriptionHash,
                                      initialFunding: market.initialFunding,
                                      createdAt : createdAt
                                    }

                                    if (count == Object.keys(marketCollection).length-1) {
                                      callbackResponse(returnObject, true);
                                    } else {
                                      callbackResponse(returnObject, false);
                                    }

                                    count++;

                                }
                                else {
                                    console.error(error);
                                }
                            });
                          }
                        )
                      }
                    );
                  }
                );

              },
              process.exit
              //console.log
            );
          },
          process.exit
          //console.log
        );
      },
      //console.log
      process.exit
    );
  },
  process.exit
  //console.log
);
