# graph2smiles

Molecular graph to SELFIES VAE. 

Required : 
- pytorch
- dgl 
- pandas 
- moses to get the data (pip install molsets)
- selfies (pip install selfies)
- rdkit
- tqdm
 -ordered-sets ( pip install ordered-set )
 
 ymls are available for cpu or cuda10 usage
 ```
conda env create -f ymls/cpu.yml 
```
 

### Data loading

We use Molecular Sets data to train our model : https://github.com/molecularsets/moses 

As a one step command, one can run 

```
python data_processing/setup.py 
```

Otherwise and as a step by step process, one can follow these steps :

After installing the moses python library, the data can be reached by running 

```
python data_processing/download_moses.py 
```
To train a graph2selfies model, selfies need to be precomputed for the train set by running 
```
python data_processing/get_selfies.py 
```
To compute selfies for another dataset stored in csv, with smiles in column entitled 'smiles', run : 
```
python data_processing/get_selfies.py -i [path_to_my_csv_dataset]
```

Chemical properties (QED, logP, molWt) can be computed for a csv dataset by running 
```
python data_processing/add_properties.py -i [path_to_csv_file]
```
Docking scores for DRD3 (DUDE target, Autodock Vina used) for 130k moses train molecules and 10k moses test molecules are stored in data/drd3_scores.zip. 
First unzip to data/drd3_scores.pickle, then add as a new column to dataframes by running 
```
python data_processing/add_scores.py
```


### Model training 

To retrain the model on the moses train set, with default settings, run
```
python train.py
```

To train the model on your own dataset (csv file), run 
```
python train.py --train [my_dataset.csv]
```

### Embedding molecules 

To compute embeddings for molecules in csv file:
```
python embed_mols.py -i [my_dataset.csv] -v [output_type]
```
The column containing the smiles should be labeled 'smiles'. 

Arguments : 
- -i : path to dataset of molecules to embed
- -v : 'smiles' or 'selfies', the type of output the model was trained for 
- -m : path to .pth file containing trained model weights (default is 'saved_model_w/baseline.pth')
- -d : Optional argument without input value, store true to decode the latent points into smiles



### Generating samples

To generate N samples from the trained model, run : 
```
python generate/sample_prior.py -n N
```
Arguments : 
- -n : number of molecules to sample 
- -m : path to .pth file containing trained model weights (default is 'saved_model_w/baseline.pth')
- -v : 'smiles' or 'selfies', the type of output the model was trained for 
- -o : path to write output text file. Default is './data/gen.txt'
- -b : Optional argument: store true to use beam search decoding for smiles (slow!)
 



