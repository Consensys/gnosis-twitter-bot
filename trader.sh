#
# TODO
# Check whether the Socket process is working or not
#

touch /tmp/trader.log
chmod 777 /tmp/trader.log
cd bots
python start_trader.py
