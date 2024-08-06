#!/usr/bin/env python
# coding: utf-8

# # Data Cleaning Strategy
# For this project, we will use the CTN0027 Dataset from the clinical trial network.<br>
# The dataset and all it's documentation are avaialble at the following website:<br>
# https://datashare.nida.nih.gov/study/nida-ctn-0027<br>
# 
# There are a few challenges to highlight that should be considered in the cleaning approach:
# - Large de-identified dataset must be manually labeled, very time consuming and prone to errors
# - High dimension data - Requires bespoke transformations to fit into machine learning models
# 

# ## Data Cleaning Process
# We will try to keep things simple and employ a process driven by reusable functions<br>
# to **improve data quality**, **reduce time to market** and **reducing human error**.<br>

# For each table we will follow the following steps:<br>
# 1. Load the data
# 2. Identify columns that require labels
# 3. Apply labels to columns
# 4. Drop columns that are not needed
# 5. Create imputation strategy for missing values
# 5. Apply transformations to values where required
# 3. Feature Engineering (if necessary)
# 4. Flatten Dataframes (encode week of treatment into columns, where applicable)
# 4. Merge with other tables
 

# ### Import Required Libraries

# In[ ]:


import pandas as pd # data manipulation library
import numpy as np # numerical computing library
import matplotlib.pyplot as plt # data visualization library
import seaborn as sns # advanced data visualization library
import helper # custom fuctions I created to clean and plot data

import warnings
warnings.filterwarnings('ignore')


# ### Load the Data
# We will load 10 files from the de-identified dataset

# In[ ]:


# define parameters to load data

# define the path to the data
data_path = '../unlabeled_data/'

# define the names of the files to load
file_names = ['T_FRRSA.csv', 'T_FRUDSAB.csv', 'T_FRDSM.csv',
              'T_FRMDH.csv', 'T_FRPEX.csv',   'T_FRTFB.csv',
              'T_FRDOS.csv', 'T_FRCOWS.csv',  'T_FRCOWS2.csv',
              'T_FRRBS0A.csv', 'T_FRDEM.csv']

# define the names of the variables for the dataframes
variables = ['rsa', 'uds', 'dsm', 'mdh', 'pex', 
             'tfb', 'dos', 'cw1', 'cw2', 'rbs','dem']

# create a loop to iterate through the files and load them into the notebook
for file_name, variable in zip(file_names, variables):
        globals()[variable] = pd.read_csv(data_path + file_name)
        print(f"{variable} shape: {globals()[variable].shape}") # print the shape of the dataframes


# ### Transform Attendence Table
# - This table establishes the patient population and will serve as the primary table
# - All subsequent tables will use a LEFT JOIN to add clinical data as columns to each patient ID
# - This table requires feature engineering for `attendance` and `dropout` variables

# In[ ]:


# we will define the columns and labels that we need for each df and then transform the data

# set parameters for transformation
rsa_cols = ['patdeid','VISIT','RSA001']
rsa_labels = {'RSA001':'rsa_week'}

# the helper function will transform the data
rsa = helper.clean_df(rsa, rsa_cols, rsa_labels)

# remove the followup visits from the main clinical data weeks 0 - 24
# rsa = rsa[~rsa['VISIT'].isin([28, 32])]

# remove duplicate rows
rsa = rsa.drop_duplicates(subset=['patdeid', 'VISIT'], keep='first')

# observe shape and sample 5 observations
print(rsa.shape)
display(rsa)


# ### Feature Engineering
# Capture weeks completed

# In[ ]:


# create df with count of attendance for each patient
attendence = rsa.groupby('patdeid')['rsa_week'].size().to_frame('weeks_attended').reset_index()

attendence


# In[ ]:


# set parameters to flatten the df
start = 0 # include data starting from week 0
end = 32 # finish at week 24
step = 1 # include data for every week

# call function to flatten dataframe
rsa_flat = helper.flatten_dataframe(rsa, start, end, step)

# fill nulls with 0 for no attendance
rsa_flat = rsa_flat.fillna(0)

# there are follow up visits for week 28 and 32
# the flatten_dataframes() function will complete a sequence
# there are erroneous columns created in the sequence
# remove columns rsa_week_25, rsa_week_26, rsa_week_27, rsa_week_29, rsa_week_30, rsa_week_31
columns_to_drop = ['rsa_week_25', 'rsa_week_26', 'rsa_week_27', 'rsa_week_29', 'rsa_week_30', 'rsa_week_31']
rsa_flat = rsa_flat.drop(columns=columns_to_drop)

# visually inspect the data
rsa_flat


# ### Feature Engineering
# - Week 32 is a followup week to measure paitent dropout.
# - If patients do not attend week 32, they are considered to have dropped out of the program
# - We will rename rsa_week_32 to `dropout` 

# In[ ]:


# rename rsa_week_28 to dropout
rsa_flat = rsa_flat.rename(columns={'rsa_week_32':'dropout'})

# reverse the values, 0 to 1, reflecting no attendence indicates dropout
rsa_flat['dropout'] = rsa_flat['dropout'].replace({0:1, 1:0})

rsa_flat


# ### Transform Urine Drug Screen Table
# This table contains the data for most of the outcome metrics<br>
# Stay tuned for feature engineering section towards the end of this table transformation<br>

# In[ ]:


# set parameters for transformation
uds_cols = ['patdeid','VISIT', 'UDS005', 'UDS006', 'UDS007', 'UDS008', 'UDS009', 'UDS010', 'UDS011', 'UDS012', 
            'UDS013']
uds_labels = {'UDS005':'test_Amphetamines', 'UDS006':'test_Benzodiazepines','UDS007':'test_MMethadone', 
              'UDS008':'test_Oxycodone', 'UDS009':'test_Cocaine', 'UDS010':'test_Methamphetamine', 'UDS011':'test_Opiate300', 'UDS012':'test_Cannabinoids', 'UDS013':'test_Propoxyphene'}

# the helper function will clean and transform the data
uds = helper.clean_df(uds, uds_cols, uds_labels)

# for values -5 which indicate unclear, replace with 1 indicating positive
uds = uds.replace(-5.0, 0)

print('Dataframe uds with shape of', uds.shape, 'has been cleaned')
display(uds)


# In[ ]:


# dataframe is ready to be flattened

# set params for flattening
start = 0 # include data starting from week 0
end = 24 # finish at week 24
step = 1 # include data for every week

# call function to flatten dataframe
uds_flat = helper.flatten_dataframe(uds, start, end, step)

# fill missing values with 1, which is a binary value for positive test
uds_flat.fillna(1, inplace=True)

# visually inspect the data
print('The clinical data was added in the form of',uds_flat.shape[1],'features')
print('Which includes tests for 8 different drug classes over 24 weeks')
display(uds_flat)


# ### Feature Engineering
# The following metrics will be created to assess treatment success:<br>
# - `TNT` - (numeric) - total negative tests, a measure of clinical benefit, count of negative tests over 24 weeks
# - `NTR` - (float) - negative test rate, a measure of clinical benefit, percentage of negative tests over 24 weeks
# - `CNT` - (numeric) - concsecutive negative tests, a measure of clinical benefit, count of consecutive negative tests over 24 weeks
# - `responder` - (binary) - indicating if the patient responds to treatment, by testing negative for opiates for the final 4 weeks of treatment
# 

# In[ ]:


# call the helper function to create the UDS features
uds_features = helper.uds_features(uds_flat)

# isolate the features df for merge with the clinical data
uds_features = uds_features[['patdeid','TNT','NTR','CNT','responder']]

print('The UDS features have been created with shape of', uds_features.shape)
display(uds_features)


# ### Transform DSM-IV Diagnosis Table
# The values for these features are mapped as follows:<br>
# <br>
# 1 = Dependence<br>
# 2 = Abuse<br>
# 3 = No Diagnosis<br>
# <br>
# This will require one hot encoding in the datapipelines later on.<br>
# We will label the values as text strings, so that they can appear<br>
# on columns in the final dataset. The text strings will also help<br>
# with analysis<br>
# 

# In[ ]:


# set params for transformation
dsm_cols = ['patdeid','DSMOPI','DSMAL','DSMAM','DSMCA','DSMCO','DSMSE']
dsm_labels = {'DSMOPI':'dsm_opiates','DSMAL':'dsm_alcohol','DSMAM':'dsm_amphetamine',
              'DSMCA':'dsm_cannabis','DSMCO':'dsm_cocaine','DSMSE':'dsm_sedative'}

# call the helper function to clean the data
dsm = helper.clean_df(dsm, dsm_cols, dsm_labels)

# convert cols to numeric
dsm = dsm.apply(pd.to_numeric, errors='coerce')

# convert values to text strings as follows after the first column
# 1 - dependence, 2 - abuse, 3 - no diagnosis, 0 - not present
for col in dsm.columns[1:]:
    dsm[col] = dsm[col].replace({1:'dependence',2:'abuse',3:'no_diagnosis',0:'not_present'})


# fill nulls with 0, where patient does not confirm diagnosis
dsm.fillna('not_present', inplace=True)

print('Dataframe dsm with shape of', dsm.shape, 'has been cleaned')
display(dsm[:5])


# ### Transform Medical and Psychiatric History Table
# We will track 18 different medical conditions

# In[ ]:


# set parameters for transformation
mdh_cols = ['patdeid','MDH001','MDH002','MDH003','MDH004','MDH005','MDH006','MDH007','MDH008','MDH009',
            'MDH010','MDH011A','MDH011B','MDH012','MDH013','MDH014','MDH015','MDH016','MDH017']
mdh_labels = {'MDH001':'mdh_head_injury','MDH002':'mdh_allergies','MDH003':'mdh_liver_problems',
                'MDH004':'mdh_kidney_problems','MDH005':'mdh_gi_problems','MDH006':'mdh_thyroid_problems',
                'MDH007':'mdh_heart_condition','MDH008':'mdh_asthma','MDH009':'mdh_hypertension',
                'MDH010':'mdh_skin_disease','MDH011A':'mdh_opi_withdrawal','MDH011B':'mdh_alc_withdrawal',
                'MDH012':'mdh_schizophrenia','MDH013':'mdh_major_depressive_disorder',
                'MDH014':'mdh_bipolar_disorder','MDH015':'mdh_anxiety_disorder','MDH016':'mdh_sig_neurological_damage','MDH017':'mdh_epilepsy'}

# call the helper function to clean the data
mdh = helper.clean_df(mdh, mdh_cols, mdh_labels)

# map values to txt strings, 0 = no_history, 1 = yes_history, 9 = not_evaluated, skip the first column
for col in mdh.columns[1:]:
    mdh[col] = mdh[col].map({0:'no_history', 1:'yes_history', 9:'not_evaluated'})

# fill in the nulls, but skip the patdeid column
mdh = mdh.fillna('not_evaluated')

# visually inspect the data
print('Dataframe mdh with shape of', mdh.shape, 'has been cleaned')
display(mdh[:5])


# ### Transform the PEX (Physical Exam) Table

# In[ ]:


# set params to clean cols
pex_cols = ['patdeid','PEX001A','PEX002A','PEX003A','PEX004A','PEX005A','PEX006A','PEX007A',
            'PEX008A','PEX009A','PEX010A','PEX011A','PEX012A','VISIT']
pex_labels = {'PEX001A':'pex_gen_appearance','PEX002A':'pex_head_neck','PEX003A':'pex_ears_nose_throat',
              'PEX004A':'pex_cardio','PEX005A':'pex_lymph_nodes','PEX006A':'pex_respiratory',
              'PEX007A':'pex_musculoskeletal','PEX008A':'pex_gi_system','PEX009A':'pex_extremeties',
              'PEX010A':'pex_neurological','PEX011A':'pex_skin','PEX012A':'pex_other'}

# this dataset includes data from visit BASELINE and 24, we are only interested in BASELINE
pex = pex.loc[pex.VISIT=='BASELINE']
              
# call the helper function to clean the data
pex = helper.clean_df(pex, pex_cols, pex_labels)

# map values to strings, 0 = normal, 1 = abnormal, 9 = not_evaluated
for col in pex.columns[2:]:
    pex[col] = pex[col].map({1:'normal', 2:'abnormal', 9:'not_evaluated'})

# imputation strategy: 9 indicates no diagnosis
pex.fillna('not_present', inplace=True)

# drop the visit column
pex.drop(columns='VISIT', inplace=True)

# visually inspect the data
print('Dataframe pex with shape of', pex.shape, 'has been cleaned')
display(pex)


# ### Transform the TFB (Timeline Follow Back Survey) Table
# - This table has an issue with multiple rows per patient
# - Each report of drug use is recorded in a new row
# - We will aggregate the data to a single row per patient
# - After the aggregation, the table will be flattened, to encode the survey, drug class and week collected, in each column
# - Surveys are collected once a month and reflect the previous 30 days of drug use

# In[ ]:


# define parameters for cleaning
tfb_cols = ['patdeid','VISIT','TFB001A','TFB002A','TFB003A','TFB004A','TFB005A','TFB006A','TFB007A',
            'TFB008A','TFB009A','TFB010A']
tfb_labels = {'TFB001A':'survey_alcohol','TFB002A':'survey_cannabis','TFB003A':'survey_cocaine',    
              'TFB010A':'survey_oxycodone','TFB009A':'survey_mmethadone','TFB004A':'survey_amphetamine','TFB005A':'survey_methamphetamine','TFB006A':'survey_opiates','TFB007A':'survey_benzodiazepines','TFB008A':'survey_propoxyphene'}

# call the helper function to clean the data
tfb = helper.clean_df(tfb, tfb_cols, tfb_labels)

# visually inspect the data
print('Shape of cleaned tfb dataframe is', tfb.shape)
display(tfb[:5])


# In[ ]:


# aggregate rows by patient and visit, sum all records of drug use

# create index
index = ['patdeid','VISIT']

# create aggregation dictionary, omit the first two columns, they do not require aggregation
agg_dict = {col:'sum' for col in tfb.columns[2:]}

# aggregate the data, we will apply sum to all instances of reported us to give the total use for the period
tfb_agg = tfb.groupby(index).agg(agg_dict).reset_index()

# visually inspect the data
print('Aggregated tfb dataframe contains', tfb_agg.shape[0],'rows, coming from', tfb.shape[0],'rows')
display(tfb_agg[:5])


# In[ ]:


# flatten the dataframe

# set parameters to flatten survey data
start = 0 # include data starting from week 0
end = 24 # finish at week 24
step = 4 # include data for every 4 weeks

# call function to flatten dataframe
tfb_flat = helper.flatten_dataframe(tfb_agg, start, end, step)

# imputation strategy: fill missing values with 0, indicates no drug use
tfb_flat.fillna(0, inplace=True)

# visualize the data
print('Flattended dataframe contains', tfb_flat.shape[1]-1,'features')
display(tfb_flat)


# ### Transform the Medication Dose Table
# - This table has an issue with multiple rows per patient
# - Each dose of medication is recorded as a row
# - This means that if a patient received 7 doses of medication, there will be 7 rows for that patient
# - This needs to be consolidated into a single row per patient
# - For total_dose with null values, we will treat that as a no show or 0 dose

# In[ ]:


# set parameters for cleaning the dataframe
dos_cols = ['patdeid','VISIT','DOS002','DOS005']   
dos_labels = {'DOS002':'medication','DOS005':'total_dose'}

# call the helper function to clean the data
dos = helper.clean_df(dos, dos_cols, dos_labels)

# Imputation strategy: backfill and forwardfill missing values from medication and total dose
dos['medication'] = dos['medication'].fillna(method='ffill').fillna(method='bfill')
dos['total_dose'] = dos['total_dose'].fillna(method='ffill').fillna(method='bfill')

# observe the data
print('The medication dataframe contains', dos.shape[0],'rows that must be aggregated')
display(dos)


# In[ ]:


# aggregate columns 

# create index
index = ['patdeid','VISIT','medication']
# create aggregation dictionary
agg_dict = {col:'sum' for col in dos.columns[3:]}

# aggregate the data, we will add daily dose to create weekly dose total, aggregating multiple columns per patient
dos_agg = dos.groupby(index).agg(agg_dict).reset_index()

# create df with patdeid and medication to merge later, this will help make analysis easier
medication = dos[['patdeid', 'medication']].drop_duplicates(subset=['patdeid'], keep='first').reset_index(drop=True)

# visualize the data
print('Total rows in the aggregated dataframe:', dos_agg.shape[0],'from', dos.shape[0],'rows')
dos_agg


# ### Feature Engineering
# Create separate columns for bupe and methadone, this improves data quality

# In[ ]:


# feature engineering

# call helper function to create features from the medication data
dos_agg = helper.med_features(dos_agg)

# visually inspect the data
print('The aggregated dataframe contains', dos_agg.shape[1]-2,'features')
display(dos_agg)


# In[ ]:


# flatten the dataframe

# set parameters to flatten the dataframe
start = 0 # include data starting from week 0
end = 24 # finish at week 24
step = 1 # include data for every week

# call function to flatten dataframe
dos_flat = helper.flatten_dataframe(dos_agg, start, end, step)

# imputation strategy: nulls come post merge, these were visits for patients who dropped out, fill with 0
dos_flat.fillna(0, inplace=True)

print('The flattened dataframe contains', dos_flat.shape[1]-1,'features')
display(dos_flat)


# ### Transform the Clinical Opiate Withdrawal Scale Table
# There are 2 files that represent predose and postdose observation for patient withdrawal symptoms<br>
# There is one column per file with the score, so this is the most simple transformation<br>

# In[ ]:


# set parameters for cleaning the dataframe
cw1_cols = ['patdeid','COWS012']
cw1_labels = {'COWS012':'cows_predose'}

# call helper function to clean columns
cw1 = helper.clean_df(cw1, cw1_cols, cw1_labels)

cw1


# In[ ]:


# set parameters for cleaning the dataframe
cw2_cols = ['patdeid','COWS012']
cw2_labels = {'COWS012':'cows_postdose'}

# call helper function to clean columns
cw2 = helper.clean_df(cw2, cw2_cols, cw2_labels)
cw2


# ## Clean the RBS table

# In[ ]:


# set parameters for cleaning the dataframe
rbs_cols = ['patdeid','RBS0A1B','RBS0A2B','RBS0A4B','RBS0A5B','RGRBS0C1']
rbs_labels = {'RBS0A1B':'rbs_cocaine','RBS0A2B':'rbs_heroine','RBS0A4B':'rbs_other_opiates',
              'RBS0A5B':'rbs_amphetamines','RGRBS0C1':'rbs_sexual_activity'}

# call helper function to clean columns
rbs = helper.clean_df(rbs, rbs_cols, rbs_labels)

# values for 7 = refused and 9 = unknown, we will convert to 0
rbs = rbs.replace({7:0, 9:0})

# fill nan with 0 no response to survey
rbs.fillna(0, inplace=True)

rbs.shape


# ### Aggregate Rows

# In[ ]:


# The survey responses were recorded through multiple rows per patient
# We will aggregate the data to create a single row per patient
rbs = rbs.groupby('patdeid').sum().reset_index()
print(f'The aggregated dataframe contains', rbs.shape[0],'rows and', rbs.shape[1],'columns')


# ## Merge the Demographics Column

# In[ ]:


dem = dem[['patdeid','DEM002']]

dem = dem.rename(columns={'DEM002':'gender'})

dem


# ### Now we will merge all the tables into a single dataset

# In[ ]:


# set parameters for merge

# Define the dataframes to merge
dfs = [rsa_flat, dos_flat, uds_flat, tfb_flat, 
       uds_features, dsm, mdh, pex, medication, 
       attendence, cw1, cw2, rbs, dem]

# Initialize merged_df with the first DataFrame in the list
merged_df = dfs[0]

# Merge the dfs above using left merge on 'patdeid'
for df in dfs[1:]:  # Start from the second item in the list
    merged_df = pd.merge(merged_df, df, on='patdeid', how='left')

# some rows were duplicated from one:many merge, they will be dropped
merged_df = merged_df.drop_duplicates(subset=['patdeid'], keep='first')

# Print the shape of the final dataframe
print('The final table includes', merged_df.shape[1]-1, 'features for', merged_df.shape[0], 'patients in treatment')

merged_df


# ### There are 666 patient instanes that dropped out week 1 that need further investigation
# - Of these instances, 67 patients attended week 1 of treatment and then dropped out
# - These instances will be preserved and added to the dataset
# - The remaining 599 patients did not record any clinical data, so these will be dropped
# 
# 
# 

# In[ ]:


# filter patient ids, by those that attended the first week and received medication, drop the remaining rows
# create a list with the indicies of rows to keep
nan_df = merged_df.loc[merged_df['weeks_attended']==1][['meds_methadone_0','meds_buprenorphine_0']].dropna()

# indices to keep
indices_to_keep = nan_df.index

# create new_df for patients who dropped out week 1
keep_rows = merged_df[merged_df['weeks_attended'] == 1]

# use the indices to keep to filter the merged_df
keep_rows = merged_df.loc[indices_to_keep]

keep_rows.shape


# ### Merge preserved patient instances

# In[ ]:


# remove rows where patients attended only one week from merged_df
new_df = merged_df.loc[merged_df['weeks_attended'] != 1]

# concat both dataframes
new_df = pd.concat([new_df, keep_rows])

# review the value counts to confirm transformation
print('new_df shape:', new_df.shape)
display(new_df)


# ## Evaluate Missing Data

# In[ ]:


# create heatmap for cows_predose and cows_postdose
plt.figure(figsize=(10, 6))
sns.heatmap(new_df[['cows_predose', 'cows_postdose']].isnull(), cbar=False)
plt.title('Missing values in the dataset')
plt.show()


# In[ ]:


new_df.loc[new_df.cows_postdose.isnull()][['cows_postdose','weeks_attended']].loc[new_df.weeks_attended == 1].shape


# ### Observations from Missing Data
# Given the healthcare context, the way in which missing data is handled is critical<br>
# Removing rows with missing data, would create too much bias in the dataset<br>
# We are also working with a small number of samples, it's important to preserve as much data as possible<br>
# <br>
# There are roughly 1,400 nan values that require strategy for imputation<br>
# There are a few columns that show concern, listed as follows:<br>
# - `medication` - there were 7 patient instances without data, we will inpute to 0 dose, for not attending<br>
# but we will preserve their records as the data for their treatment is still valuable<br>
# - `surveys` - there were 11 patient instances with missing surveys, 6 of these patient dropped out in week 1<br>
# We will inpute with the mean value for surveys of that week, as the asumption is that the patient did used
# drugs and did not submit a survey<br>
# - `pex` - physical exam - there was 1 patient missing exam, we will inpute as not present
# - `dsm` - addiction diagnosis - there were 4 patients missing addiction diagnosis, we will inpute as not evaluated
# -`rbs` - risk based survey, there were 3 patients missing this survey, we will inpute with mean value for the assessment
# 
# 
# The clinical opiate withdrawal scale has a high number of missing values<br>
# - `cows_predose` - 33
# - `cows_postdose` - 171 
# 

# ### Evaluate Patient Nulls for Surveys

# In[ ]:


# create survey df to evaluate nulls
survey = new_df[[col for col in new_df.columns if 'survey' in col]]


# show the nulls in the survey dataframe
index = survey[survey.isnull().any(axis=1)].index

# observe the patient instances with all the data
new_df.loc[index]['dropout'].value_counts()


# ### Evaluate Patient Nulls for Medication

# In[ ]:


# create meds DF to evaluate nulls
meds = new_df[[col for col in new_df.columns if 'meds' in col]]

# show the rows with nan values
meds[meds.isnull().any(axis=1)].index

# create index for reference on new_df
index = [202, 490, 761, 1132, 1259, 1554, 2022]


# observe the patient instances with all the data
new_df.loc[index]['dropout'].value_counts()


# ### Evaluate Patient Nulls for Medication

# In[ ]:


pex = new_df[[col for col in new_df.columns if 'pex' in col]]

index = pex[pex.isnull().any(axis=1)].index

new_df.loc[index]['dropout'].value_counts()


# ### Evaluate Patient Nulls for Physical Exam

# In[ ]:


mdh = new_df[[col for col in new_df.columns if 'mdh' in col]]

mdh[mdh.isnull().any(axis=1)]

new_df.loc[2022]


# ### Evaluate Patient Nulls for DSM Diagnosis  

# In[ ]:


dsm = new_df[[col for col in new_df.columns if 'dsm' in col]]

index = dsm[dsm.isnull().any(axis=1)].index

new_df.loc[index]['dropout'].value_counts() 


# ### Evaluate Patient Nulls for COWS Predose and Postdose

# In[ ]:


cows = new_df[[col for col in new_df.columns if 'cows' in col]]

# look at predose nulls
predose_index = cows[cows.cows_predose.isnull()].index

# look at postdose nulls
postdose_index = cows[cows.cows_postdose.isnull()].index

# look at the rows with nulls
new_df.loc[predose_index]['dropout'].value_counts() 

new_df.loc[postdose_index]['dropout'].value_counts()



# ### Evaluate RBS Nulls

# In[ ]:


rbs = new_df[[col for col in new_df.columns if 'rbs' in col]]

index  = rbs[rbs.isnull().any(axis=1)].index

new_df.loc[index]['dropout'].value_counts()


# ### Imputation Execution
# - `medication` - 7 instances inpute with 0 dose
# - `surveys` - 11 instances inpute with mean value for that week
# - `pex` Physical Exam - 1 instance inpute as not present
# - `dsm` Addiction diagnosis - 4 instances inpute as not evaluated
# - `cows_predose` - 33 instances, we will inpute with linear regression
# - `cows_postdose` - 171 instances, we will inpute with linear regression
# 
# 

# In[ ]:


# run a loop to fill nulls with simple replacement
for col in new_df.columns:
    if 'meds' in col:
        new_df[col] = new_df[col].fillna(0)
    elif 'medication':
        new_df[col] = new_df[col].fillna(0)
    elif 'survey' in col:
        new_df[col] = new_df[col].fillna(new_df[col].mean())
    elif 'pex' in col:
        new_df[col] = new_df[col].fillna('not_evaluated')
    elif 'mdh' in col:
        new_df[col] = new_df[col].fillna('not_evaluated')
    elif 'dsm' in col:
        new_df[col] = new_df[col].fillna('not_evaluated')
    elif 'cows' in col:
        new_df[col] = new_df[col].fillna(0)
    elif 'rbs' in col:
        new_df[col] = new_df[col].fillna(new_df[col].mean())
    elif 'cows_predose' in col:
        new_df[col] = new_df[col].fillna(0)
    elif 'cows_postdose' in col:
        new_df[col] = new_df[col].fillna(0)


# ### We will use linear regression to impute the missing values for COWS Predose and Postdose

# In[ ]:


# use iterative imputer for cows_predose 
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# create an instance of the imputer
imputer = IterativeImputer(max_iter=10, random_state=0)

# fit the imputer
imputer.fit(new_df[['cows_predose']])

# transform the data
new_df['cows_predose'] = imputer.transform(new_df[['cows_predose']])

# visually inspect the data
new_df['cows_predose'].hist()
plt.title('COWS Predose')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.show()


# In[ ]:


# create an instance of the imputer
imputer = IterativeImputer(max_iter=10, random_state=0)

# fit the imputer
imputer.fit(new_df[['cows_postdose']])

# transform the data
new_df['cows_postdose'] = imputer.transform(new_df[['cows_postdose']])

# visually inspect the data
new_df['cows_postdose'].hist()


# In[ ]:


pd.set_option('display.max_rows', None)
new_df.isnull().sum()


# In[ ]:


# save to data folder in csv
new_df.to_csv('../data/new_merged_data.csv', index=False)


# In[ ]:


benchmark_features = pd.read_csv('../data/benchmark_features.csv')

benchmark_features = benchmark_features.columns


# In[ ]:


new_df = new_df.loc[:, benchmark_features]

new_df


# In[ ]:


# plot heatmap of nulls
plt.figure(figsize=(14, 6))
sns.heatmap(new_df.isnull(), cbar=False)
plt.title('Missing values in the dataset')
plt.show()


# In[ ]:


fig, ax = plt.subplots(1, 2, figsize=(14, 6))
new_df.cows_predose.hist(alpha=0.5, ax=ax[0])
new_df.cows_postdose.hist(alpha=0.5, ax=ax[1])


# In[ ]:


pd.set_option('display.max_rows', None)
new_df.loc[new_df.cows_postdose.isnull()]['dropout'].value_counts()


# In[ ]:


# show heatmap for cows predose and postdose
plt.figure(figsize=(10, 6))
sns.heatmap(new_df[['cows_predose', 'cows_postdose']].isnull(), cbar=False)
plt.title('Missing values in the dataset')
plt.show()

