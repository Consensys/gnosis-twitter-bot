module.exports = {
  addresses: {
    defaultMarketFactory: '0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199',
    defaultMarketMaker: '0x9f866444e7b85005a593ac5c1aef29244a23a10e',
    etherToken: '0x99f3931d0e1285855ac3d37648d4bb3fc705743e',
    eventFactory: '0xae506b8af761ea320df139a8d2407ce13b9f8ecc',
    ultimateOracle: '0xf50869608ef145e4d9770f6d21410dd44e8ea0af',
    lmsrMarketMaker: '0x9f866444e7b85005a593ac5c1aef29244a23a10e',
    makerToken: '0xece9fa304cc965b00afc186f5d0281a00d3dbbfd'
  },
  addressFilters: {
    oracle: '0xf50869608ef145e4d9770f6d21410dd44e8ea0af'
  },
  eventDescriptionFilters: {
    oracleAddresses: null,
    includeWhitelistedOracles: true,
    pageSize: 50
  },
  addressFiltersPostLoad: {
    marketMakers: ['0x9f866444e7b85005a593ac5c1aef29244a23a10e'],
    oracles: ['0xf50869608ef145e4d9770f6d21410dd44e8ea0af'],
    tokens: [
      '0x99f3931d0e1285855ac3d37648d4bb3fc705743e',
      '0x6fd1cff94dbe0ba14f01f39bfc2f6ee396843bad',
      '0xece9fa304cc965b00afc186f5d0281a00d3dbbfd'],
  },
  gnosisServiceURL: 'https://beta.gnosis.pm/api/',
  ethereumNodeURL: 'https://ropsten.infura.io/gnosis-twitter-bot',
  transactionsLoop: false,
  callBeforeTransaction: false
};
