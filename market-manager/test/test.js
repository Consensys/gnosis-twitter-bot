const expect = require('chai').expect;
const childProcess = require('child_process');

describe('get markets', function () {
  this.timeout(20000);
  it ('all markets', (done) => {

    childProcess.exec('node getMarkets.js', function(e, out) {
      expect(e).to.be.null;
      const markets = JSON.parse(out);
      expect(markets).to.be.a('array');
      //expect(markets).to.have.length.above(1);

      markets.map( (market) => {
        expect(market).to.contain.all.keys(['marketHash', 'investor', 'shares', 'description', 'marketAddress', 'prices']);
        expect(market.marketHash).to.be.a('string');
        expect(market.shares).to.be.a('array');
        expect(market.investor).to.be.a('string');
        expect(market.description).to.be.a('object');
        expect(market.marketHash).to.be.a('string');
        expect(market.prices).to.be.a('array');
        expect(market.description.title).to.be.a('string');
        expect(market.description.tags).to.be.a('array');
        expect(market.description.tags.map(function(item){ return item.toLowerCase();})).to.contain('twitter');
        expect(market.description.description).to.be.a('string');
        expect(market.description.sourceURL).to.be.a('string');
        expect(market.description.resolutionDate).to.be.a('string');
      });

      done();
    });
  });
});

describe('get QR', function () {
  this.timeout(20000);
  it('get QR ok', (done) => {
    childProcess.exec('node getQR.js 0xff5251b689c63a71ed6b4718d86bd1ea332293a80f526608dc334d29af1743e2 1 0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199 1', function(e, out) {
      expect(e).to.be.null;
      const response = JSON.parse(out);
      expect(response).to.be.a('object');
      expect(response).to.contain.all.keys(['imageString', 'numberOfShares', 'priceBeforeBuying', 'priceAfterBuying']);
      expect(response.imageString).to.be.a('string');
      expect(response.numberOfShares).to.be.a('number');
      expect(parseFloat(response.priceBeforeBuying)).to.be.a('number');
      expect(parseFloat(response.priceBeforeBuying)).to.be.within(0, 1);
      expect(parseFloat(response.priceAfterBuying)).to.be.a('number');
      expect(parseFloat(response.priceAfterBuying)).to.be.within(0, 1);
      done();
    });
  });

  it('get QR fail', (done) => {
    childProcess.exec('node getQR.js 0xff5251b689c63a71ed6b4718d86bd1ea332293a80f526608dc334d29af1743e1 1 0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199 1', function(e, out, eInfo) {
      expect(e).to.be.an('error');
      expect(e.code).to.be.eql(1);
      done();
    });
  });
});
