import subprocess

# -*- coding: utf-8 -*-
"""
Created on Wed May  6 17:10:04 2020

@author: jacqu

CbAS iterative procedure 

"""
import os
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_dir, '..', '..'))

import torch
import numpy as np
import argparse

from selfies import decoder
from rdkit import Chem

from utils import *
from dgl_utils import *
from model import model_from_json
from cbas.oracles import qed, deterministic_cdf_oracle, normal_cdf_oracle
from cbas.gen_train import GenTrain
from cbas.gen_prob import GenProb
from docking.docking import dock, set_path

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--prior_name', type=str, default='inference_default')  # the prior VAE (pretrained)
    parser.add_argument('--search_name', type=str, default='search_vae')  # the prior VAE (pretrained)

    parser.add_argument('--oracle', type=str, default='qed')  # qed for toy oracle, 'aff' for docking
    parser.add_argument('--computer', type=str, default='rup')  # Computer to use for docking

    parser.add_argument('--procs', type=int, default=0)  # Number of processes for VAE dataloading

    parser.add_argument('--iters', type=int, default=25)  # Number of iterations
    parser.add_argument('--Q', type=float, default=0.6)  # quantile of scores accepted

    parser.add_argument('--M', type=int, default=1000)  # Nbr of samples at each iter

    # Params of the search-model finetuning (seems sensitive)
    parser.add_argument('--epochs', type=int, default=5)  # Number of iterations
    parser.add_argument('--learning_rate', type=float, default=1e-4)  # Number of iterations
    parser.add_argument('--beta', type=float, default=0.2)  # KL weight in loss function
    parser.add_argument('--clip_grad_norm', type=float, default=5.0)  # quantile of scores accepted

    # =======

    args, _ = parser.parse_known_args()

    device = 'cpu'  # 'cuda' if torch.cuda.is_available() else 'cpu'

    # Initialize search vae q
    save_dir = os.path.join(script_dir, 'results/models')
    savepath = os.path.join(save_dir, args.search_name)

    params = {'savepath': savepath,
              'epochs': args.epochs,
              'device': device,
              'lr': args.learning_rate,
              'clip_grad': args.clip_grad_norm,
              'beta': args.beta,
              'processes': args.procs,
              'DEBUG': True}
    dumper = Dumper(dumping_path=os.path.join(save_dir, 'params.json'), default_model=False)
    dumper.dic.update(params)
    dumper.dump()

    prior_model_init = model_from_json(args.prior_name)
    torch.save(prior_model_init.state_dict(), os.path.join(savepath, "weights.pth"))

    id_train = None

    for t in range(1, args.iters + 1):

        slurm_sampler_path = os.path.join(script_dir, 'slurm_sampler.sh')
        if id_train is not None:
            cmd = f'sbatch {slurm_sampler_path}'
        else:
            cmd = f'sbatch --depend=afterany:{id_train} {slurm_sampler_path}'
        a = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
        id_sample = a.split()[3]

        # SIMULATE DOCKING
        slurm_docker_path = os.path.join(script_dir, 'slurm_docker.sh')
        cmd = f'sbatch --depend=afterany:{id_sample} {slurm_docker_path}'
        a = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
        id_dock = a.split()[3]
        # print(f'launched docking run with id {id_run}')

        slurm_trainer_path = os.path.join(script_dir, 'slurm_trainer.sh')
        cmd = f'sbatch --depend=afterany:{id_dock} {slurm_trainer_path}'
        a = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
        id_train = a.split()[3]