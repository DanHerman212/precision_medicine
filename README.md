# Precision Medicine: Improving Treatment for Opioid Use Disorder with Machine Learning


<div align="center">
    <img src="images/cover.jpg" alt="Opioid Use Disorder Treatment Study">
</div>

<br><br>


# Project Introduction 
<font size='4'>There is a public health crisis in the US where 6 million people are suffering from opioid use disorder (OUD).<br><br>
There is effective treatment available in the form of medication treatment for OUD (MOUD).<br>
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
|:--------:|----------|:--------:|----------|
|Project Article   |A detailed article was written on Medium, providing a detailed analysis of the project.            |[Medium Article](https://medium.com/@danherman64/precision-medicine-improving-treatment-for-opioid-use-disorder-with-machine-learning-1da08ca8e960)   |          |
|Data Wrangling    |A high quality dataset was built capturing features through an end-to-end ETL pipeline.  There were a total of 7 tables that were added to the dataset with 5 transformations that were coded through reusable functions.          |    [Jupyter Notebook](code/1_Data_Transformation.ipynb)      | Reusable functions are stored in [helper.py](code/helper.py)<br>  Notebook includes extensive documentation       |
| Data Modeling  |A jupyter notebook was created to cherry pick features to create a bespoke dataset with some lightweight pipelines to test for accuracy.          | [Jupyter Notebook](code/2_Data_Modeling.ipynb)         |Notebook is straight forward, does not come with extensive documentation          |
| Exploratory Analysis   |Provides distributions for all variables in the project dataset.  For  a detailed analysis, it's best to reference the article for the project on Medium.          | [Jupyter Notebook](code/3_Exploratory_Analysis.ipynb)         |          |
|ML Pipelines   |Reusable functions are chained together using pipelines to test different classifiers with different hyperparameter configurations.  The pipelines are free from any hard coded dependency, providing simple and fast run times to run lots of experimments.          |        [Jupyter Notebook](code/4_ML_Piplines.ipynb)  |There is some bonus code to plot metrics, extract feature importance and decision boundaries, good for presentation          |
|Explainable AI |This is an implemenation for the SHAP library.  If you are familiar, there are are the standard plots for classification, including summary and waterfall plots.  There are some custom plots, including a 2 column feature interaction plot, as well as scatter plot.          |  [Jupyter Notebook](code/5_Explainable_AI.ipynb)        |I did not use the implementation for the project, so there is no documentation in the notebook, if you are interested in learning more about SHAP, I recommend getting [this book](https://christophmolnar.com/books/shap/).          |
|Project Dataset   |Datset created for the project, includes 42 features.  Stored in the data directory, labeled as '42_features.csv'           |      [CSV file](data/42_features.csv)    |          |
|Complete Dataset | Complete Dataset with 400+ features extracted from original public dataset [CTN-0027](https://datashare.nida.nih.gov/study/nida-ctn-0027)          |      [CSV File](data/final_merged_data.csv)    |          |
|Reusable Functions   | There are a number of reusable functions used through out the project.  They can all be found in the `helper.py` file, located in the code directory.         |[helper.py](code/helper.py)          |          |
|Project Documentation   | All documentation from the public dataset and other documents gathered in reseaerching this project| [Documentation Folder](documentation/)
<br>


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
