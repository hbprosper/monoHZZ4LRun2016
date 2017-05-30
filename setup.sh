export PATH=$PWD/bin:$PATH

if [ -d $HOME/external/fbm.2004-11-10 ]; then
    echo
    echo "==> FBM package available"
    export BNNPATH=$HOME/external/fbm.2004-11-10
    export PATH=$BNNPATH/bin:$PATH
else
    echo "** warning ** fbm.2004-11-10 package not found! **"
fi

if [ -d $HOME/external/histutil ]; then
    echo
    echo "==> histutil package available"
    source $HOME/external/histutil/setup.sh
else
    echo "** WARNING ** histutil package not found, but is needed **"
    echo "** by this analysis code                                **"
fi

if [ -d $HOME/external/pgammafit ]; then
    echo
    echo "==> pgammafit package available"
    source $HOME/external/pgammafit/setup.sh
else
    echo "** WARNING ** pgammafit package not found, so you won't **"
    echo "** be able to do a Bayesian fit!                        **"
fi


if [ -d $HOME/external/limits ]; then
    echo
    echo "==> limits package available"
    source $HOME/external/limits/setup.sh
else
    echo "** WARNING ** limits package not found **"
fi
echo
