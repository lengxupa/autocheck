#!/bin/bash
#PBS -l walltime=4:00:00
#PBS -l nodes=1:ppn=16
#PBS -N subpan
#PBS -q standby

set echo

cd $PBS_O_WORKDIR
module load intel impi/5.1.2.150 lammps/15Feb16
module load python/anaconda
module load matlab
python check.py