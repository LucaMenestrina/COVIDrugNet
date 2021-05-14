#!/bin/sh

# launch with: bash update.sh >& ../update.log &

date
echo "Starting Update ..."
if test -f "../send_message.py"; then
  python ../send_message.py -m "Starting Update ..."
fi
cd ..
if test -f "wget-log"; then
  rm wget-log
fi
wget https://github.com/LucaMenestrina/COVIDrugNet/archive/refs/heads/master.zip
unzip master.zip
rm master.zip
if test -d "COVIDrugNet.bkp"; then
  rm -r COVIDrugNet.bkp
fi
mv COVIDrugNet COVIDrugNet.bkp
mv COVIDrugNet-master COVIDrugNet
cd COVIDrugNet
start_time="$(date -u +%s)"
python collector.py
end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
date
echo "Database Updated"
if test -f "../send_message.py"; then
  python ../send_message.py -m "Database Updated"
fi
if [ "$elapsed" -gt 60 ] # it is assumed that if the database takes less than 60 seconds to update there are not any new drugs/proteins
then
  echo "Download time: $elapsed"
  echo "Starting Analyses ..."
  if test -f "../send_message.py"; then
    python ../send_message.py -m "Starting Analyses ..."
  fi
  cd analysis
  python fitting.py
  date
  echo "Fitting Analysis Done"
  if test -f "../../send_message.py"; then
    python ../../send_message.py -m "Fitting Analysis Done"
  fi
  python robustness.py
  date
  echo "Robustness Analysis Done"
  if test -f "../../send_message.py"; then
    python ../../send_message.py -m "Robustness Analysis Done"
  fi
  cd ..
else
  echo "Nothing to Update"
  if test -f "../send_message.py"; then
    python ../send_message.py -m "Nothing to Update"
  fi
fi
date
echo "Update Completed!"
if test -f "../send_message.py"; then
  python ../send_message.py -m "Update Completed!"
fi
