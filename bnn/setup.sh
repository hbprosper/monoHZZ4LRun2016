# ---------------------------------------------
# Set up path to BNN software
# ---------------------------------------------
# change to location of your fbm installation
export BNNPATH=$HOME/external/fbm.2004-11-10

export PATH=`pwd`/bin:$BNNPATH/bin:$PATH

if [ $PYTHONPATH ]; then
    export PYTHONPATH=`pwd`/python:$PYTHONPATH
else
    export PYTHONPATH=`pwd`/python
fi
