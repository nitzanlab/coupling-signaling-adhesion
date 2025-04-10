import pickle
import pandas as pd

def load_workspace(filename='variables'):
    with open(f'{filename}.pkl', 'rb') as f:
        workspace = pickle.load(f)
    globals().update(workspace)

def parse(rows,col,n_cells,ratio,df):
    mask = df['c'].isin(list(range(col,col+4))) & df['r'].isin(rows)
    df.loc[mask,['n_cells','ratio']]= [n_cells,ratio]
    return df

mod1 = lambda x,n: (x-1)%n+1


load_workspace('induced')

df_orig = df.copy()

A_col_dict = {'Row':'r',
              "Column":'c',
              'Nuclei_BFP - BFPpos_position Centroid X in Image [Âµm]':'x',
              'Nuclei_BFP - BFPpos_position Centroid Y in Image [Âµm]':'y',
              'Nuclei_BFP - BFPpos_position Centroid Z in Image [Âµm]':'z',
              'Timepoint':'t',
              'Nuclei_BFP - Nucleus Resized Volume [ÂµmÂ³]':'v',
              'Nuclei_BFP - Intensity Nucleus Resized DAPI Mean':'BFP'
              }
df_a = df_orig['bfp'][list(A_col_dict.keys())].rename(columns = A_col_dict)
df_a['cell_type'] = 'A'


B_col_dict = {'Row':'r',
              "Column":'c',
              'Nuclei_IFP - IFPpos_position Centroid X in Image [Âµm]':'x',
              'Nuclei_IFP - IFPpos_position Centroid Y in Image [Âµm]':'y',
              'Nuclei_IFP - IFPpos_position Centroid Z in Image [Âµm]':'z',
              'Timepoint':'t',
              'Nuclei_IFP - Nucleus Resized Volume [ÂµmÂ³]':'v',
              'Nuclei_IFP - Intensity Nucleus Resized EGFP Mean':'GFP',
              'Nuclei_IFP - Intensity Nucleus Resized DRAQ5 Mean':'IFP'              
              }
df_b = df_orig['ifp'][list(B_col_dict.keys())].rename(columns = B_col_dict)
df_b['cell_type'] = 'B'

df_induced = pd.concat([df_a,df_b],axis=0)

parse([4,5],3,300,'1:9',df_induced)
parse([4,5],7,300,'1:1',df_induced)
parse([4,5],11,300,'9:1',df_induced)
parse([4,5],15,900,'3:7',df_induced)
parse([4,5],19,900,'7:3',df_induced)

parse([10,11],3,300,'3:7',df_induced)
parse([10,11],7,300,'7:3',df_induced)
parse([10,11],11,900,'1:9',df_induced)
parse([10,11],15,900,'1:1',df_induced)
parse([10,11],19,900,'9:1',df_induced)

df_induced['rep'] = mod1(df_induced['c']-2,4)
df_induced['experiment'] = 'induced'



load_workspace('constitutive')
df_orig = df.copy()

A_col_dict = {'Row':'r',
              "Column":'c',
              'Nuclei_IFP - IFPpos_position Centroid X in Image [Âµm]':'x',
              'Nuclei_IFP - IFPpos_position Centroid Y in Image [Âµm]':'y',
              'Nuclei_IFP - IFPpos_position Centroid Z in Image [Âµm]':'z',
              'Timepoint':'t',
              'Nuclei_IFP - Nucleus Resized Volume [ÂµmÂ³]':'v',
              'Nuclei_IFP - Intensity Nucleus Resized DRAQ5 Mean':'IFP'
              }
df_a = df_orig['ifp'][list(A_col_dict.keys())].rename(columns = A_col_dict)
df_a['cell_type'] = 'A'

B_col_dict = {'Row':'r',
              "Column":'c',
              'Nuclei_BFP - BFPpos_position Centroid X in Image [Âµm]':'x',
              'Nuclei_BFP - BFPpos_position Centroid Y in Image [Âµm]':'y',
              'Nuclei_BFP - BFPpos_position Centroid Z in Image [Âµm]':'z',
              'Timepoint':'t',
              'Nuclei_BFP - Nucleus Resized Volume [ÂµmÂ³]':'v',
              'Nuclei_BFP - Intensity Nucleus Resized DAPI Mean':'BFP'            
              }
df_b = df_orig['bfp'][list(B_col_dict.keys())].rename(columns = B_col_dict)
df_b['cell_type'] = 'B'

df_const = pd.concat([df_a,df_b],axis=0)

parse([4,5],3,300,'1:9',df_const)
parse([4,5],7,300,'1:1',df_const)
parse([4,5],11,300,'9:1',df_const)
parse([4,5],15,900,'3:7',df_const)
parse([4,5],19,900,'7:3',df_const)

parse([10,11],3,300,'3:7',df_const)
parse([10,11],7,300,'7:3',df_const)
parse([10,11],11,900,'1:9',df_const)
parse([10,11],15,900,'1:1',df_const)
parse([10,11],19,900,'9:1',df_const)

df_const['rep'] = mod1(df_const['c']-2,4)
df_const['experiment'] = 'constitutive'


df_combined = pd.concat([df_induced,df_const],axis=0).dropna(subset=['x'])
df_combined['radius'] = df_combined['v']**(1/3)

filename = 'data_parsed'
with open(f'{filename}.pkl','wb') as f:
    pickle.dump({'df':df_combined},f)

with open(f'{filename}.pkl','rb') as f:
    loaded = pickle.load(f)

print(loaded['df'])

print('here')