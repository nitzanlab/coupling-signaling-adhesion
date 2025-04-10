from scipy.sparse.csgraph import connected_components

import pickle
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from time import time

import os
print(os.getcwd())

dist_tol = 0.1;#0.10 # distance tolerance percentage
BFP_threshold = 300
GFP_threshold = 1000
# volume_threshold = 0 # added to account for large clusters identified as a single cell with a small mean BFP/GFP value

s_time = time()
filename = 'data_parsed'

with open(f'{filename}.pkl','rb') as f:
    loaded = pickle.load(f)
df_tot = loaded['df']

bfp_filter = (df_tot.experiment == 'constitutive') & (df_tot.cell_type == 'B') & (df_tot.BFP<BFP_threshold)
df_tot = df_tot[~bfp_filter]

gfp_filter = (df_tot.experiment == 'induced') & (df_tot.cell_type == 'B') & (df_tot.GFP<GFP_threshold)
df_tot = df_tot[~gfp_filter]

def compute_clusters_at_timepoint(time_df):
    time_df.reset_index(drop=True,inplace=True)
    coords = time_df[['x', 'y', 'z']].values
    dist_matrix = squareform(pdist(coords))
    
    adj_matrix = np.zeros(dist_matrix.shape)
    
    for i in range(len(time_df)):
        for j in range(i + 1, len(time_df)):
            if dist_matrix[i, j] < (time_df.at[i, 'radius'] + time_df.at[j, 'radius'])*(1+dist_tol):
                adj_matrix[i, j] = adj_matrix[j, i] = 1
    
    _, labels = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)
    time_df['cluster'] = labels
        
    # Calculate the volume for each cluster
    cluster_volumes = time_df.groupby('cluster')['v'].sum().reset_index()
    cluster_volumes = cluster_volumes.rename(columns={'v': 'cluster_volume'})
    time_df = time_df.merge(cluster_volumes, on='cluster', how='left')

    # Calculate relative cluster volume
    total_volume = time_df['v'].sum()
    time_df['relative_cluster_volume'] = time_df['cluster_volume'] / total_volume
    
    return time_df

# Filter to keep only B cells and iterate over all combinations of ratio, rep, n_cells, and experiment

df = df_tot 

df_tot_b = df[df['cell_type'] == 'B']

unique_combinations = df_tot_b[['n_cells', 'ratio', 'rep', 'experiment', 't']].drop_duplicates()

all_processed_dfs = []
for _, comb in unique_combinations.iterrows():
    print(f'{time()-s_time}: {comb}')
    
    n_cells, ratio, rep, exp, timepoint = comb
    df_slice = df_tot_b[(df_tot_b['n_cells'] == n_cells) & (df_tot_b['ratio'] == ratio) & (df_tot_b['rep'] == rep) & 
                        (df_tot_b['experiment'] == exp) & (df_tot_b['t'] == timepoint)].copy()
    processed_df = compute_clusters_at_timepoint(df_slice)
    all_processed_dfs.append(processed_df)

# Concatenate all the processed dataframes
df_b_processed = pd.concat(all_processed_dfs, ignore_index=True)

# Merge processed B cells back with the original dataframe
df_tot = df_tot.merge(df_b_processed, how='left', on=df_tot.columns.intersection(df_b_processed.columns).tolist(), suffixes=('', '_new'))
final_df = df_tot.dropna(subset=['x'])

# final_df = final_df[~((final_df['cell_type'] == 'B') & (final_df['cluster'].isna()))]

print('Cluster computation completed for all slices.')

filename = 'data_clustered'
with open(f'{filename}.pkl','wb') as f:
    pickle.dump({'df':final_df},f)



