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

if (process.argv.length != 5) {
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

// get QR transaction string
gnosis.contracts.marketFactory.buyShares(
  process.argv[2], // marketHash
  new BigNumber(process.argv[3]), // outcomeIndex
  new BigNumber("1e18"),
  new BigNumber("1e23"),
  configObject,
  process.argv[4] // marketAddress
).then(
  (tx) => {
    let uportTx = tx.txhash;
    pngBuffer = qrImage.imageSync(uportTx, {type: 'png'});
    console.log('data:image/png;charset=utf-8;base64, ' + pngBuffer.toString('base64'));
  }
);
