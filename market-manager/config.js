module.exports = {
  addresses: {
    defaultMarketFactory: '0x6ca7f214ab2ddbb9a8e1a1e2c8550e3164e9dba5',
    defaultMarketMaker: '0x8695e5e79dab06fbbb05f445316fa4edb0da30f0',
    etherToken: '0x92f1dbea03ce08225e31e95cc926ddbe0198e6f2',
    eventFactory: '0x5aae5c59d642e5fd45b427df6ed478b49d55fefd',
    ultimateOracle: '0x529c4cb814029b8bb32acb516ea3a4b07fdae350',
    lmsrMarketMaker: '0x8695e5e79dab06fbbb05f445316fa4edb0da30f0'
  },
  addressFilters: {
    oracle: '0x529c4cb814029b8bb32acb516ea3a4b07fdae350'
  },
  eventDescriptionFilters: {
    oracleAddresses: '0x7b2e78d4dfaaba045a167a70da285e30e8fca196',
    includeWhitelistedOracles: false,
    pageSize: 50
  },
  addressFiltersPostLoad: {
    marketMakers: ['0x8695e5e79dab06fbbb05f445316fa4edb0da30f0'],
    oracles: ['0x529c4cb814029b8bb32acb516ea3a4b07fdae350'],
    tokens: ['0x92f1dbea03ce08225e31e95cc926ddbe0198e6f2'],
  },
  gnosisServiceURL: 'https://admin.gnosis.pm/api/',
  ethereumNodeURL: 'https://mainnet.infura.io/gnosis-twitter-bot'
};
