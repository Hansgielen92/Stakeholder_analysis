import os
import pandas as pd
import glob
import os
import numpy as np

from files.function import synthesize_assessment_input



df = synthesize_assessment_input(r'C:\Users\hans_\Documents\GitHub\Stakeholder_analysis\files\input_stakeholders_2.csv')
print(df.head())