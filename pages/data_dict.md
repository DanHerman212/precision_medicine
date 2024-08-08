# Data Dictionary

<font size='4'>
The data dictionary provides a description of the 61 features in the dataset.
<br>
<br>
The features are grouped into numeric, categorical, and binary types.<br>

</font>

## Binary Features
| Feature | Description | Type | Range | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Numeric Features
| Feature | Description | Type | Range | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
`cows_postdose`|Clinical Opiate Withdrawal Scale (COWS) score after the dose|numeric|0-36| 1321 |12.2  |4.7  |0  | 10 |12 |15  |32  |
 `cows_predose`|Clinical Opiate Withdrawal Scale (COWS) score before the dose|numeric|0-36| 1321 |4.94 | 4.3 | 0 | 2 | 4 | 7 | 29 |
 |`meds_buprenorphine_0`|Buprenorphine dose pre-treatment|numeric|0 - 216| 1321 | 12.05 | 24.32 | 0 | 0 | 8 | 12 | 216 |
 |`meds_buprenorphine_1`|Buprenorphine dose Week 1|numeric|0 - 448| 1321 | 55.94 | 73.08 | 0 | 0 | 4 | 108 | 448 |
 |`meds_buprenorphine_2`|Buprenorphine dose Week 2|numeric|0 - 408| 1321 | 57.58 | 79..7 | 0 | 0 | 4 | 112 | 408 |
 |`meds_buprenorphine_3`|Buprenorphine dose Week 3|numeric|0 - 336| 1321 | 51.46 | 74.41 | 0 | 0 | 0 | 100 | 336 |
 |`meds_buprenorphine_4`|Buprenorphine dose Week 4|numeric|0 - 902| 1321 | 55.63 | 88.04 | 0 | 0 | 0 | 108 | 902 |
 |`meds_methadone_0`|Methodone dose pre-treatment|numeric|0 - 500| 1321 | 28.74 | 64.01 | 0 | 0 | 0 | 30 | 500 | 
 |`meds_methadone_1`|Methodone dose Week 1|numeric|0 - 960| 1321 | 124.70 | 184.17 | 0 | 0 | 0 | 260 | 960 |
 |`meds_methadone_2`|Methodone dose Week 2|numeric|0 - 1460| 1321 | 156.17 | 234.98 | 0 | 0 | 0 | 330 | 1460 |
 |`meds_methadone_3`|Methodone dose Week 3|numeric|0 - 1120| 1321 | 156.91 | 239.35 | 0 | 0 | 0 | 325 | 1120 |
 |`meds_methadone_4`|Methodone dose Week 4|numeric|0 - 1780| 1321 | 176.91 | 281.37 | 0 | 0 | 0 | 350 | 1780 |
 |`rbs_amphetamines`|Risk Survey - Amphetamine Use|numeric |0-70| 1321 | 1.41 | 5.67 | 0 | 0 | 0 | 0 | 70 |
 |`rbs_cocaine`|Risk Survey - Cocaine Use|numeric |0-90| 1321 | 5.73 | 11.92 | 0 | 0 | 1 | 4 | 90 |
 |`rbs_heroine`|Risk Survey - Heroin Use|numeric |0-90| 1321 | 25.6 | 15.53 | 0 | 18 | 30 | 31 | 90 |
 |`rbs_other_opiates`|Risk Survey - Other Opiate Use|numeric |0-77| 1321 |6.63 | 11.62 | 0 | 0 | 0 | 6 | 77 |
 |`rbs_sexual_activity`|Risk Survey - Sexual Activity|numeric |0-288| 1321 | 5.2 | 19.22 | 0 | 1 | 3 | 3 | 288 |
 |`survey_opiates_0`|Self Reported Opiate Use - Pre-treatment|numeric |0-32| 1321 | 24.32 |9.82 | 0 | 23| 30 | 30 | 32 | 
 |`survey_opiates_4`|Self Reported Opiate Use - Week 4|numeric |0-52| 1321 |4.55 |7.88 | 0 | 0| 0 | 6 | 24 |

 <br>

 ## Categorical Features

| Feature | Description | Type | Count | Unique Values | Top Value | Freqency |
| --- | --- | --- | --- | :---: | --- | --- | 
|`dsm_alcohol`|Alcohol use disorder diagnosis|categorical|1321|5|`no_diagnosis`| 1291 |
|`dsm_amphetamine`|Amphetamine use disorder diagnosis|categorical|1321|5|`no_diagnosis`| 1004|
| `dsm_cannabis`|Cannabis use disorder diagnosis|categorical|1321|5|`no_diagnosis`| 898|
|`dsm_cocaine`|Cocaine use disorder diagnosis|categorical|1321|5|`no_diagnosis`| 757|
|`dsm_opiates`|Opiate use disorder diagnosis|categorical|1321|5|`dependence`| 1128|
|`dsm_sedative`|Sedative use disorder diagnosis|categorical|1321|5|`no_diagnosis`| 966|
|`mdh_alc_withdrawal`|Alcohol withdrawal history|categorical|1321|4|`no_history`| 1209|
| `mdh_allergies`|Allergies|categorical|1321|4|`no_history`| 942|
| `mdh_anxiety_disorder`|Anxiety disorder|categorical|1321|4|`no_history`| 912|
| `mdh_asthma`|Asthma|categorical|1321|4|`no_history`| 1120|
| `mdh_bipolar_disorder`|Bipolar disorder|categorical|1321|4|`no_history`| 1159|
| `mdh_epilepsy`|Epilepsy|categorical|1321|4|`no_history`| 1266|
| `mdh_gi_problems`|GI problems|categorical|1321|4|`no_history`| 1012|
| `mdh_head_injury`|Head injury|categorical|1321|4|`no_history`| 969|
| `mdh_heart_condition`|Heart condition|categorical|1321|4|`no_history`| 1213|
 |`mdh_hypertension`|Hypertension|categorical|1321|4|`no_history`| 1151|
 |`mdh_kidney_problems`|Kidney problems|categorical|1321|4|`no_history`| 1231|
 |`mdh_liver_problems`|Liver problems|categorical|1321|4|`no_history`| 888|
 |`mdh_major_depressive_disorder`|Major depressive disorder|categorical|1321|4|`no_history`| 948|
 |`mdh_opi_withdrawal`|Opiate withdrawal history|categorical|1321|4|`yes_history`| 1096|
 |`mdh_schizophrenia`|Schizophrenia|categorical|1321|4|`no_history`| 1274|
 |`mdh_sig_neurological_damage`|Significant neurological damage|categorical|1321|4|`no_history`| 1184|
 |`mdh_skin_disease`|Skin disease|categorical|1321|4|`no_history`| 1078|
 |`mdh_thyroid_problems`|Thyroid problems|categorical|1321|4|`no_history`| 1271|
 |`pex_cardio`|Cardiovascular|categorical|1321|5|`normal`| 1231|
 |`pex_ears_nose_throat`|Ears, nose, throat|categorical|1321|5|`normal`| 861|
 |`pex_extremeties`| Extremeties|categorical|1321|5|`normal`| 1146|
 |`pex_gen_appearance`|General appearance|categorical|1321|5|`normal`| 1073|
 |`pex_gi_system`|GI system|categorical|1321|5|`normal`| 1033|
 |`pex_head_neck`|Head, neck|categorical|1321|5|`normal`| 1228|
 |`pex_lymph_nodes`|Lymph nodes|categorical|1321|5|`normal`| 1252|
 |`pex_musculoskeletal`|Musculoskeletal|categorical|1321|5|`normal`| 1212|
 |`pex_neurological`|Neurological|categorical|1321|5|`normal`| 1253| 
 |`pex_other`|Other|categorical|1321|5|`not_present`| 1252|719|
 |`pex_respiratory`|Respiratory|categorical|1321|5|`normal`| 1203|
 |`pex_skin`|Skin|categorical|1321|5|`abnormal`| 683|