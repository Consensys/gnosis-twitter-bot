touch /tmp/trader.log
chmod 777 /tmp/trader.log

####################
# Startup command
####################
cd bots
python start_trader.py&
pid=$!

while true; do
  if  ps -p $pid > /dev/null; then
    echo "Twitter Bot - PID $pid - is alive"
  else
    echo "Twitter Bot - PID $pid - is dead, restarting..."
    python start_trader.py&
    pid=$!
  fi

  sleep 10;

done
