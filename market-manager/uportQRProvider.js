const Subprovider = require('web3-provider-engine/subproviders/subprovider');

class UportQRSubprovider extends Subprovider {
  constructor (opts) {
    super();
  }

  handleRequest (payload, next, end) {
    const self = this;
    switch (payload.method) {

      case 'eth_sendTransaction':
        let txParams = payload.params[0];

        self.txParamsToUri(txParams, (err, val) => {
          end(err, val);
        })

        return;

      default:
        next()
        return

    }
  }

  txParamsToUri (txParams, cb) {
    let uri = 'https://id.uport.me/' + txParams.to
    let symbol
    if (!txParams.to) {
      return cb(new Error('Contract creation is not supported by uportProvider'))
    }
    if (txParams.value) {
      uri += '?value=' + parseInt(txParams.value, 16)
    }
    if (txParams.data) {
      symbol = txParams.value ? '&' : '?'
      uri += symbol + 'bytecode=' + txParams.data
    }
    if (txParams.gas) {
      symbol = txParams.value || txParams.data ? '&' : '?'
      uri += symbol + 'gas=' + parseInt(txParams.gas, 16)
    }
    cb(null, uri)
  }
}

module.exports = UportQRSubprovider;
