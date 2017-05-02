#------------------------------------------------------------------------------
# Description: This file contains the commands to run the BNN training.
#              Note: the data-spec format assumes that all inputs in the
#                    training file are used and the last column is the
#                    target.
# Created: Mon May  1 10:54:38 2017 by mktrain.py
#------------------------------------------------------------------------------
#	1	f_mass4l
#	2	f_D_bkg_kin
#------------------------------------------------------------------------------
echo "File: m4lmela"

net-spec	m4lmela.bin 2 10 1 / - 0.05:0.5 0.05:0.5 - x0.05:0.5 - 100

model-spec	m4lmela.bin binary

data-spec	m4lmela.bin 2 1 2 / m4lmela.dat@2:5001 . m4lmela.dat@2:5001 .

net-gen		m4lmela.bin fix 0.5

mc-spec		m4lmela.bin repeat 20 heatbath hybrid 100:10 0.2

net-mc		m4lmela.bin 1

mc-spec m4lmela.bin repeat 20 sample-sigmas heatbath 0.95 hybrid 100:10 0.2

echo "Start chain"
echo "Use"
echo "   net-display -h m4lmela.bin"
echo "periodically to check the progress of the chain"

time net-mc	m4lmela.bin 250

echo ""
echo "Use"
echo "   netwrite.py -n 100 m4lmela.bin"
echo "to create the BNN function m4lmela.cpp using the last 100 points"
