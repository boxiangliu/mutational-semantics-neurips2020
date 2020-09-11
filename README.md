# Learning the language of viral evolution and escape

This repository contains the analysis code, links to the data, and pretrained models for the paper "Learning the language of viral evolution and escape" by Brian Hie, Ellen Zhong, Bonnie Berger, and Bryan Bryson (2020).

### Data

You can download the [relevant datasets](http://cb.csail.mit.edu/cb/viral-mutation/data.tar.gz) (including training and validation data) using the commands
```bash
wget http://cb.csail.mit.edu/cb/viral-mutation/data.tar.gz
tar xvf data.tar.gz
```
within the same directory as this repository.

### Dependencies

The major Python package requirements and their tested versions are in [requirements.txt](requirements.txt).

Our experiments were run with Python version 3.7 on Ubuntu 18.04.

### Experiments

Key results from our experiments can be found in the [`results/`](results) directory and can be reproduced with the commands below. The [`models/`](models) directory contains key pretrained models used in our analyses.

To run the experiments below, download the data (instructions above). Our experiments require a maximum of 400 GB of CPU RAM and 32 GB of GPU RAM; _in silico_ fitness and escape model inference can take around 35 minutes for influenza HA, 90 minutes for HIV Env, and 10 hours for SARS-CoV-2 Spike.

#### Influenza HA

Influenza HA semantic embedding UMAPs and log files with statistics can be generated with the command
```bash
python bin/flu.py bilstm --checkpoint models/flu.hdf5 --embed \
    > flu_embed.log 2>&1
```

Single-residue escape prediction using validation data from [Doud et al. (2018)](https://github.com/jbloomlab/HA_antibody_ease_of_escape) and [Lee et al. (2019)](https://github.com/jbloomlab/map_flu_serum_Perth2009_H3_HA) can be done with the command
```bash
python bin/flu.py bilstm --checkpoint models/flu.hdf5 --semantics \
    > flu_semantics.log 2>&1
```

Combinatorial fitness experiments measuring correlation with grammaticality and semantic change using data from [Doud and Bloom (2016)](https://www.mdpi.com/1999-4915/8/6/155/htm) and from [Wu et al. (2020)](https://github.com/wchnicholas/site_B_landscape) can be done with the command
```bash
python bin/flu.py bilstm --checkpoint models/flu.hdf5 --combfit \
    > flu_combfit.log 2>&1
```

Training a new model on flu HA sequences can be done with the command
```bash
python bin/flu.py bilstm --train --test \
    > flu_train.log 2>&1
```

#### HIV Env

HIV Env semantic embedding UMAPs and log files with statistics can be generated with the command
```bash
python bin/hiv.py bilstm --checkpoint models/hiv.hdf5 --embed \
    > hiv_embed.log 2>&1
```

Single-residue escape prediction using validation data from [Dingens et al. (2019)](https://github.com/jbloomlab/EnvsAntigenicAtlas) can be done with the command
```bash
python bin/hiv.py bilstm --checkpoint models/hiv.hdf5 --semantics \
    > hiv_semantics.log 2>&1
```

Combinatorial fitness experiments measuring correlation with grammaticality and semantic change using data from [Haddox et al. (2018)](https://github.com/jbloomlab/EnvMutationalShiftsPaper) can be done with the command
```bash
python bin/hiv.py bilstm --checkpoint models/hiv.hdf5 --combfit \
    > hiv_combfit.log 2>&1
```

Training a new model on HIV Env sequences can be done with the command
```bash
python bin/hiv.py bilstm --train --test \
    > hiv_train.log 2>&1
```

#### SARS-CoV-2 Spike

Coronavirus spike semantic embedding UMAPs and log files with statistics can be generated with the command
```bash
python bin/cov.py bilstm --checkpoint models/cov.hdf5 --embed \
    > cov_embed.log 2>&1
```

Single-residue escape prediction using validation data from [Baum et al. (2020)](https://science.sciencemag.org/content/early/2020/06/15/science.abd0831) and DMS data from [Greaney et al. (2020)](https://www.biorxiv.org/content/10.1101/2020.09.10.292078v1.full.pdf) can be done with the command
```bash
python bin/cov.py bilstm --checkpoint models/cov.hdf5 --semantics \
    > cov_semantics.log 2>&1
```

Combinatorial fitness experiments measuring correlation with grammaticality and semantic change using data from [Starr et al. (2020)](https://jbloomlab.github.io/SARS-CoV-2-RBD_DMS) can be done with the command
```bash
python bin/cov.py bilstm --checkpoint models/cov.hdf5 --combfit \
    > cov_combfit.log 2>&1
```

Experiments measuring grammaticality and semantic change of a SARS-CoV-2 reinfection event documented by [To et al. (2020)](https://academic.oup.com/cid/advance-article/doi/10.1093/cid/ciaa1275/5897019) can be done with the command
```bash
python bin/cov.py bilstm --checkpoint models/cov.hdf5 --reinfection \
    > cov_reinfection.log 2>&1
```

Training a new model on coronavirus spike sequences can be done with the command
```bash
python bin/cov.py bilstm --train --test \
    > cov_train.log 2>&1
```

### Questions

For questions about the pipeline and code, contact brianhie@mit.edu. We will do our best to provide support, address any issues, and keep improving this software. And do not hesitate to submit a pull request and contribute!
