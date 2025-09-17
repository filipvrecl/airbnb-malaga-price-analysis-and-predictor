***** MAIN QUESTIONS/GOALS/WHY? *****

OBJECTIVE:
- How do Airbnb prices vary across Málaga, and what patterns can we uncover in 
relation to  date, location, room type, availability, and host characteristics?

- Can we accurately predict the nightly price of a new listing, 
and which features are the most influential in setting that price?

WHY?
Setting the right price is one of the hardest challenges for Airbnb hosts.
    - Price too high → risk of low occupancy.
    - Price too low → lost revenue.
By analyzing real-world data and building a machine learning model, 
this project provides data-driven pricing guidance.

Read more in Analysis file.


*** PROJECT STEPS ***

1. Data cleaning/transforming (cleaning -> data_cleaning.py)
2. In-depth data analysis (documentation -> Malaga Analysis)
3. Modeling/Machine learning + Deployment (documentation -> Malaga Machine Learning)


*** INSTRUCTIONS ON HOW TO READ DOCUMENTATION ***

For easy view, feel free to read the PDFs.
If you want to test/see code for yourself, make sure you can open jupyter notebooks, as well as have all required packages installed.


*** FINISHED PROJECT SUMMARY ***
Read summary at the bottom of documentation -> Analysis.



*** INSTRUCTIONS ON HOW USE PRICE PREDICTION MODEL ***
(screenshot/demo of app is in -> visuals)

1. Make sure you have all required packages installed (listed in requirements.txt)

2. Locate and copy the directory of the 'models' folder (right click 'models', click Properties, and look for General -> Location). 
    EXAMPLE: C:\Users\myusername\Desktop\PROJECT_Malaga\models

3. Press Windows+R, and type in 'cmd', press ENTER (if using mac/linux, open command terminal).
3.1. Run the following commands:

    1. -> cd *paste directory from earlier*
        EXAMPLE: cd C:\Users\myusername\Desktop\PROJECT_Malaga\models

    2. -> streamlit run app.py

If you entered both commands correctly, the app window will pop up in the browser.