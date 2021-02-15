import os, sys
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import yaml


country = 'btn'
national_level = False

def crop_grouping(df):
    crop_group = pd.read_csv('crop_groups.csv').fillna('')
    crop_dict = dict((k,v) 
                     for k, v in
                     zip(crop_group.crop, 
                         crop_group.group)
                     )
    for each_crop in crop_dict.keys():
        if crop_dict[each_crop] == '':
            crop_dict[each_crop] = each_crop
    
    df['crop'].replace(crop_dict, 
                       inplace=True)
    
    return df


lc_codes = pd.read_csv(r'lc_codes.csv')
lc_dict = dict((k,v) for k, v in zip(lc_codes['code'],
                                 lc_codes['name']))

def df_reformat(path, country, national_level):
    path_in = os.path.join(r'.\\GIS analysis results\\',
                           country,
                           country + path + '.csv')
    
    df = pd.read_csv(path_in)    
    
    if national_level:
        df.columns.values[0] = 'stats'
        df = df.loc[~df['stats'].isin(['min','max'])]
        df.drop('stats', axis=1, inplace=True)
        df['region_code'] = country.upper()
        
    else:
        df = df.loc[~df['cluster'].isin(['None'])]    
        df['region_code'] = (df['cluster'].str[:2].str.upper() + 
                             df['cluster'].str[-1:].str.upper())
        df.drop('cluster', axis=1, inplace=True)
        
    return df


if national_level:
    df_lc = df_reformat('_LandCover_National_summary', 
                        country, 
                        national_level)

else:
    df_lc = df_reformat('_LandCover_byCluster_summary', 
                        country, 
                        national_level)
    df_lc.drop('sqkm', axis=1, inplace=True)


df_lc = pd.melt(df_lc,
                id_vars= ['region_code'],
                value_vars = [x 
                              for x 
                              in df_lc 
                              if x 
                              not in ['region_code']],
                var_name = 'lc',
                value_name = 'value')

df_lc['lc'] = 'LC' + df_lc['lc'].str[6:]
df_lc['lc_category'] = df_lc['lc'].map(lc_dict)
#df_lc.drop('lc', axis=1, inplace=True)

df_lc = df_lc.groupby(['region_code', 
                       'lc_category'],
                      as_index=False)['value'].sum()
df_lc['value'] = df_lc['value'].div(1000)

df_lc = df_lc.pivot_table(index='region_code',
                          columns='lc_category',
                          values='value',
                          aggfunc='sum').reset_index()

path_lc_out = os.path.join(r'.\\GIS analysis results\\',
                           country,
                           'gis_to_clewsy_results')

if not os.path.exists(path_lc_out):
    os.makedirs(path_lc_out)


if national_level:
    df_param = df_reformat('_Parameter_National_summary', 
                        country, 
                        national_level)

else:
    df_param = df_reformat('_Parameter_ByCluster_summary', 
                        country, 
                        national_level)

# df_param = df_reformat('_Parameter_byCluster_summary', country)

df_param = pd.melt(df_param,
                   id_vars= ['region_code'],
                   value_vars = [x 
                                 for x 
                                 in df_param 
                                 if x 
                                 not in ['region_code']],
                   var_name = 'id',
                   value_name = 'value')


## Create column with param: 'yld', 'cwd', 'evt', 'prc'
df_param['param'] = df_param['id'].str.split('_').str[1]

## Create separate DataFrame for param 'prc'
df_prc = df_param.loc[df_param['param'].isin(['prc'])]
df_prc = df_prc[['region_code','value']]
df_prc['value'] = df_prc['value'].div(1000)
df_prc.rename(columns={'value':'precipitation'}, 
              inplace=True)

df_param = df_param.loc[~(df_param['param'].isin(['prc']))]

## Create columns for crops, water supply, and input levels
df_param['crop'] = df_param['id'].str.split('_').str[2]
df_param['water_supply'] = df_param['id'].str.split('_').str[3]
df_param['input_level'] = df_param['id'].str.split('_').str[4]

param_df = pd.read_csv(r'naming_convention.csv', 
                       encoding='latin')
param_df['code'] = param_df['code'].str.split().str.join(' ')
param_df['name'] = param_df['name'].str.split().str.join(' ')

param_dict = dict((k,v) for k, v in zip(param_df['code'],
                                        param_df['name']))

for each_param in ['water_supply', 'input_level']:
    df_param[each_param].replace(param_dict, 
                                 inplace=True)

## Group crops base on user-defined crop grouping
df_param['crop'] = df_param['crop'].str.upper()
df_param = crop_grouping(df_param)
df_param = df_param.groupby(['region_code',
                             'param',
                             'crop',
                             'water_supply',
                             'input_level'],
                            as_index=False)['value'].mean()

## Create column with crop combo e.g. WHE Irrigated High
df_param['crop_ws_input'] = (df_param['crop'] + 
                             ' ' +
                             df_param['water_supply'] + 
                             ' ' +
                             df_param['input_level'])


for each_param in df_param['param'].unique():
    if each_param == 'yld':
        df_param.loc[df_param['param'].isin([each_param]),
                     'value'] = df_param.loc[df_param['param'].isin([each_param]),
                                             'value'].div(10)
    else:
        df_param.loc[df_param['param'].isin([each_param]),
                     'value'] = df_param.loc[df_param['param'].isin([each_param]),
                                             'value'].div(1000)

df_param = pd.pivot_table(df_param,
                          index=['region_code',
                                 'param'],
                          columns='crop_ws_input',
                          values='value').reset_index()


df_yld = df_param.loc[df_param['param'].isin(['yld'])]
df_yld.drop('param', axis=1, inplace=True)
df_yld = pd.merge(df_lc,
                  df_yld,
                  on=['region_code'],
                  how='outer')

for each_region in df_yld['region_code'].unique():
        
    df_yld_out = df_yld.loc[df_yld['region_code'].isin([each_region])]
    path_lc_out_region = os.path.join(path_lc_out,
                                      'clustering_results_' + each_region + '.csv')
    df_yld_out.rename(columns={'region_code':'cluster'}, 
                      inplace=True)
    df_yld_out.drop([col 
                     for col in df_yld_out.columns 
                     if df_yld_out[col].isnull().all()],
                    axis=1,
                    inplace=True)
    for each_col in ['Land cover example', 'land_area', 'count']:
        df_yld_out.insert(1, column=each_col, value=0)
        
    df_yld_out['cluster'] = np.arange(len(df_yld_out)) + 1
    df_yld_out.to_csv(path_lc_out_region,
                      index=None)
    
for each_region in df_yld['region_code'].unique():
        
    df_prc_out = df_prc.loc[df_prc['region_code'].isin([each_region])]
    
    path_lc_out_region = os.path.join(path_lc_out,
                                      'clustering_results_prc_' + each_region + '.csv')
    df_prc_out.rename(columns={'region_code':'cluster'}, 
                      inplace=True)
    df_prc_out['cluster'] = np.arange(len(df_prc_out)) + 1
    df_prc_out.to_csv(path_lc_out_region,
                      index=None)
    
for each_region in df_yld['region_code'].unique():
    for each_water in ['cwd', 'evt']:
        df_water = df_param.loc[df_param['param'].isin([each_water])]
        df_water.drop('param', axis=1, inplace=True)
        df_water = df_water.loc[df_water['region_code'].isin([each_region])]
        path_lc_out_region = os.path.join(path_lc_out,
                                          'clustering_results_' + 
                                          each_water +
                                          '_' +  
                                          each_region + 
                                          '.csv')
        df_water.rename(columns={'region_code':'cluster'}, 
                        inplace=True)
        df_water.drop([col 
                       for col in df_water.columns 
                       if df_water[col].isnull().all()],
                      axis=1,
                      inplace=True)
        df_water['cluster'] = np.arange(len(df_water)) + 1
        df_water.to_csv(path_lc_out_region,
                          index=None)