#------------------------------------------------------------------------------
# Description: This file contains the commands to run the BNN training.
#              Note: the data-spec format assumes that all inputs in the
#                    training file are used and the last column is the
#                    target.
# Created: Tue May  2 10:32:09 2017 by mktrain.py
#------------------------------------------------------------------------------
#	1	f_mass4l
#	2	f_D_bkg_kin
#	3	f_pfmet
#------------------------------------------------------------------------------
echo "File: m4lmelamet"

net-spec	m4lmelamet.bin 3 10 1 / - 0.05:0.5 0.05:0.5 - x0.05:0.5 - 100

model-spec	m4lmelamet.bin binary

data-spec	m4lmelamet.bin 3 1 2 / m4lmelamet.dat@2:5001 . m4lmelamet.dat@2:5001 .

net-gen		m4lmelamet.bin fix 0.5

mc-spec		m4lmelamet.bin repeat 20 heatbath hybrid 100:10 0.2

net-mc		m4lmelamet.bin 1

mc-spec m4lmelamet.bin repeat 20 sample-sigmas heatbath 0.95 hybrid 100:10 0.2

echo "Start chain"
echo "Use"
echo "   net-display -h m4lmelamet.bin"
echo "periodically to check the progress of the chain"

time net-mc	m4lmelamet.bin 250

echo ""
echo "Use"
echo "   netwrite.py -n 100 m4lmelamet.bin"
echo "to create the BNN function m4lmelamet.cpp using the last 100 points"
