const gnosis = require("gnosisjs");
const configObject = require("./config.js");
const BigNumber = require('bignumber.js');
const QRProvider = require('./uportQRProvider.js');
const ProviderEngine = require('web3-provider-engine');
const RpcSubprovider = require('web3-provider-engine/subproviders/rpc.js')
const Web3 = require('web3');
const engine = new ProviderEngine();
const web3 = new Web3(engine);
const qrImage = require('qr-image');

if (process.argv.length != 6) {
  process.exit();
}

// Set web3
web3.eth.defaultAccount = '0xB42E70a3c6dd57003f4bFe7B06E370d21CDA8087'
engine.addProvider(new QRProvider());
engine.addProvider(new RpcSubprovider({
 rpcUrl: configObject.ethereumNodeURL,
}));
configObject.web3 = web3;
engine.start();

let marketAddress = process.argv[4];
let marketHash = process.argv[2];
let outcomeIndex = new BigNumber(process.argv[3]);
let userPrice = new BigNumber(process.argv[5]).mul(new BigNumber('1e18'));

gnosis.contracts.marketFactory.getMarketsProcessed(
  [marketHash],
  configObject,
  marketAddress
).then((response) => {
  let globalResponse = {};
  let market = response[marketHash];
  let shares = market.shares;
  let initialFunding = market.initialFunding;
  let shareDistributionCopy = market.shares.slice(0);

  // gnosis.contracts.eventFactory.getEventsProcessed([market.eventHash], null, null, configObject)
  // .then(
  //   (r) => {
  //     console.log(r);
  //   }
  // );
  // gnosis.contracts.marketFactory.getMarket(
  //   marketHash,
  //   configObject,
  //   marketAddress,
  //   function(e, r){
  //     console.log("Market");
  //     console.log(r);
  //     console.log(r.getEvent());
  //   }
  // ).call();

  let numberOfShares = gnosis.marketMaker.calcShares(
    userPrice, // n tokens
    outcomeIndex,
    shareDistributionCopy,
    initialFunding
  );

  // get QR transaction string
  gnosis.contracts.marketFactory.buyShares(
    marketHash,
    outcomeIndex,
    numberOfShares,
    userPrice,
    configObject,
    marketAddress
  ).then(
    (tx) => {

      // But in order to calculate 66%, you have to calculate first how many shares
      // the user gets for 2 ETH To change `shares` accordingly before calling calcPrice for the changed price

      let uportTx = tx.txhash;
      let pngBuffer = qrImage.imageSync(uportTx, {type: 'png'});
      globalResponse.imageString = pngBuffer.toString('base64');
      globalResponse.numberOfShares = numberOfShares.div('1e18').toNumber();
      // Calculate price before buying
      var priceBeforeBuying = gnosis.marketMaker.calcPrice(shareDistributionCopy, outcomeIndex, initialFunding).toNumber();
      // Calculate price after buying
      shareDistributionCopy[outcomeIndex] = shareDistributionCopy[outcomeIndex].minus(userPrice);
      var priceAfterBuying = gnosis.marketMaker.calcPrice(shareDistributionCopy, outcomeIndex, initialFunding).toNumber();

      globalResponse.priceBeforeBuying = priceBeforeBuying.toPrecision(Math.ceil(Math.log(priceBeforeBuying)/Math.log(10))+3)
      globalResponse.priceAfterBuying = priceAfterBuying.toPrecision(Math.ceil(Math.log(priceAfterBuying)/Math.log(10))+3)

      console.log(JSON.stringify(globalResponse));
    }
  );


});
