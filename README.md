# Precision Medicine: Applying State of the Art Machine Learning to Opioid Use Disorder Treatment


<div align="center">
    <img src="images/cover.jpg" alt="Opioid Use Disorder Treatment Study">
</div>

<br>


# Project Introduction 
<font size='4'>There is a public health crisis in the US where 6 million people are suffering from opioid use disorder (OUD).<br><br>
There is a effective treatment available in the form of medication treatment for OUD (MOUD).<br>
However, there are problems with patient dropout, where treatment is not personalized and 50% of patients relapse and don't complete treatment.<br>
<br>
A prognostic model that can predict risk for relapse early in treatment would be clinically useful.<br>
<br>
For this project, I built a prognostic model that can detect risk for relapse at week 4 of a 32 week treatment period with 72% accuracy, using the Random Forest, Ensemble Learning Model.  
<br>
A high quality dataset was built, using public dataset [CTN-0027](https://datashare.nida.nih.gov/study/nida-ctn-0027).  The dataset included treatment data for 1,269 patients, receiving treatment during a 32 week period.<br>
<br>
To evaluate model accuracy I will use the concordance index.  A common metric used to measure the ability of a risk model to properly assign risk to patients with health outcomes.<br>
<br>

# Key Implementations
Below is a table listing critical components for the project and appropriate code, listed as follows:<br>
| Implementation | Description | Resource | Comments|
|----------|----------|----------|----------|
|Data Wrangling    |A high quality dataset was built capturing features through an end-to-end ETL pipeline.  There were a total of 7 tables that were added to the dataset with 5 transformations that were coded through reusable functions.          |    Jupyter Notebook      | Reusable functions are stored in helper.py file          |
| Row 2    |          |          |          |
| Row 3    |          |          |          |
| Row 4    |          |          |          |
| Row 5    |          |          |          |
| Row 6    |          |          |          |
| Row 7    |          |          |          |
| Row 8    |          |          |          |
| Row 9    |          |          |          |
| Row 10   |          |          |          |


# Python Libraries
The following libraries are required to run this project:
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- xgboost
- shap


# File Directory
<font size='4'>

Please refer to the [file directory](pages/tree.md) below for the complete project structure.

</font>
</font>




# Python Libraries
The following libraries are required to run this project:
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- xgboost
- shap


# File Directory
<font size='4'>

Please refer to the [file directory](pages/tree.md) below for the complete project structure.

</font>