{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "357393d8-5b21-4d91-84a2-b9546f5f3046",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "from fpdf import FPDF\n",
    "import tempfile\n",
    "from pathlib import Path\n",
    "import os\n",
    "import glob"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "897f8001",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[]\n"
     ]
    }
   ],
   "source": [
    "#Tijdelijke oplossing totdat ik andere manier heb gevonden om input te krijgen\n",
    "folder_path = r'c:\\Users\\hans_\\Documents\\GitHub\\Stakeholder_analysis\\Testdingen'\n",
    "pattern = os.path.join(folder_path, '*.csv')\n",
    "csv_files = glob.glob(pattern)\n",
    "\n",
    "\n",
    "print(csv_files)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "178f0380",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Create function to synthesize assesment input\n",
    "def synthesize_assessment_input(file_path):\n",
    "    pattern = os.path.join(file_path, '*.csv')\n",
    "    csv_files = glob.glob(pattern)\n",
    "\n",
    "    all_data = []\n",
    "\n",
    "    if not csv_files:\n",
    "        return FileNotFoundError(f\"No CSV files found in the folder: {folder_path}\") \n",
    "    #Doorloop alle csv bestanden en voeg ze samen in een dataframe\n",
    "    for file in csv_files:\n",
    "        temp_df = pd.read_csv(file, sep=';')\n",
    "        all_data.append(temp_df)\n",
    "\n",
    "    #Combineer alle dataframes in één dataframe\n",
    "    combined_df = pd.concat(all_data, ignore_index=True)\n",
    "\n",
    "    #Logica om de gecombineerde dataframe te verwerken en te synthetiseren\n",
    "    aggregated_logic = {\n",
    "        'formeel': 'mean',\n",
    "        'informatie': 'mean',\n",
    "        'informeel': 'mean',\n",
    "        'legitimiteit': 'mean',\n",
    "        'betrokkenheid': 'mean',\n",
    "        'waarom': lambda x: ' | '.join(set(x))\n",
    "    }\n",
    "\n",
    "    synthesis = combined_df.groupby('stakeholder').agg(aggregated_logic).reset_index()\n",
    "    #Mogelijk later toevoegen om af te ronden\n",
    "    return synthesis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "876e8c8d",
   "metadata": {},
   "outputs": [],
   "source": [
    "df = synthesize_assessment_input(r'c:\\Users\\hans_\\Documents\\GitHub\\Stakeholder_analysis\\Testdingen')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "09063951",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "cwd= /Users/HGielen/Coding/GitHub/Stakeholder_analysis/files\n",
      "False\n"
     ]
    }
   ],
   "source": [
    "#Check for Apple/WINDOWS path issues\n",
    "print('cwd=', os.getcwd())\n",
    "print(os.path.exists(r'c:\\Users\\hans_\\Documents\\GitHub\\Stakeholder_analysis\\Testdingen\\.ipynb_checkpoints\\input_stakeholders-checkpoint.csv'))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "9730c8ea-1562-4c5f-b4a3-bf54d3e402ce",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_data(file_path):\n",
    "    try:\n",
    "        return pd.read_csv(file_path, sep=';')\n",
    "    except FileNotFoundError:\n",
    "        return pd.DataFrame({\"StakeHolder\": ['Project']}) #temp \n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "ee3efaa7-6b6f-4d85-84c0-e54b7fdaa5b6",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Structureren van data:\n",
    "def data_structure(df):\n",
    "    columns = df.columns.tolist()\n",
    "    for col in columns:\n",
    "        try:\n",
    "            all_counts = df[col].value_counts()\n",
    "            return all_counts\n",
    "        except ValueError:\n",
    "            print('wrong values')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "e8973d48-c849-41f2-acd1-0746df78deaa",
   "metadata": {},
   "outputs": [],
   "source": [
    "def get_strategy(power, interest): #nodig: power en interest score op basis van input)\n",
    "    if power >= 4 and interest >= 4: return \"Manage closely\"\n",
    "    if power >= 4 and interest < 4: return \"keep satisfied\"\n",
    "    if power < 4 and interest >= 4: return \"keep informed\"\n",
    "    return \"Monitor only\"\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "6162ec2d-91e8-4796-9f80-d476d320dc25",
   "metadata": {},
   "outputs": [],
   "source": [
    "def create_power_interest_columns(dataFrame):\n",
    "    power_columns = ['formeel', 'informatie', 'informeel','legitimiteit']\n",
    "    dataFrame['power_scores'] = dataFrame[power_columns].mean(axis=1)\n",
    "    dataFrame['interest'] = dataFrame['betrokkenheid']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "05b4650b",
   "metadata": {},
   "outputs": [],
   "source": [
    "def create_matrix_plot(df):\n",
    "    fig, ax = plt.subplots(figsize=(6,4))\n",
    "    ax.scatter(df['power_scores'], df['interest'], c='blue')\n",
    "\n",
    "    #Kwadranten indelen\n",
    "    plt.axhline(3, color='black', linewidth=1)\n",
    "    plt.axvline(3, color='black', linewidth=1)\n",
    "    plt.xlim(1,5)\n",
    "    plt.ylim(1,5)\n",
    "\n",
    "    plt.xlabel('power (1-5)')\n",
    "    plt.ylabel('interest (1-5)')\n",
    "    plt.title('Stakeholder map')\n",
    "\n",
    "    for i, txt in enumerate(df['stakeholder']):\n",
    "        ax.annotate(txt, (df['power_scores'].iat[i], df['interest'].iat[i])) #.iat werkt als iloc, maar dan voor specifieke cellen, niet hele rijen of kolommen\n",
    "\n",
    "    plt.tight_layout()\n",
    "    plt.show()\n",
    "    plot_path = tempfile.NamedTemporaryFile(delete=False, suffix=\".png\").name\n",
    "    plt.savefig(plot_path)\n",
    "    print(f\"File location: {plot_path}\")\n",
    "    return plot_path"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "72881252",
   "metadata": {},
   "outputs": [
    {
     "ename": "TypeError",
     "evalue": "'FileNotFoundError' object is not subscriptable",
     "output_type": "error",
     "traceback": [
      "\u001b[31m---------------------------------------------------------------------------\u001b[39m",
      "\u001b[31mTypeError\u001b[39m                                 Traceback (most recent call last)",
      "\u001b[36mCell\u001b[39m\u001b[36m \u001b[39m\u001b[32mIn[12]\u001b[39m\u001b[32m, line 1\u001b[39m\n\u001b[32m----> \u001b[39m\u001b[32m1\u001b[39m create_power_interest_columns(df)\n\u001b[32m      2\u001b[39m df[\u001b[33m'\u001b[39m\u001b[33mstrategy\u001b[39m\u001b[33m'\u001b[39m] = df.apply(\u001b[38;5;28;01mlambda\u001b[39;00m row: get_strategy(row[\u001b[33m'\u001b[39m\u001b[33mpower_scores\u001b[39m\u001b[33m'\u001b[39m], row[\u001b[33m'\u001b[39m\u001b[33minterest\u001b[39m\u001b[33m'\u001b[39m]), axis=\u001b[32m1\u001b[39m)\n\u001b[32m      5\u001b[39m \u001b[38;5;28;01mfor\u001b[39;00m i, row \u001b[38;5;129;01min\u001b[39;00m df.iterrows():\n",
      "\u001b[36mCell\u001b[39m\u001b[36m \u001b[39m\u001b[32mIn[10]\u001b[39m\u001b[32m, line 3\u001b[39m, in \u001b[36mcreate_power_interest_columns\u001b[39m\u001b[34m(dataFrame)\u001b[39m\n\u001b[32m      1\u001b[39m \u001b[38;5;28;01mdef\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[34mcreate_power_interest_columns\u001b[39m(dataFrame):\n\u001b[32m      2\u001b[39m     power_columns = [\u001b[33m'\u001b[39m\u001b[33mformeel\u001b[39m\u001b[33m'\u001b[39m, \u001b[33m'\u001b[39m\u001b[33minformatie\u001b[39m\u001b[33m'\u001b[39m, \u001b[33m'\u001b[39m\u001b[33minformeel\u001b[39m\u001b[33m'\u001b[39m,\u001b[33m'\u001b[39m\u001b[33mlegitimiteit\u001b[39m\u001b[33m'\u001b[39m]\n\u001b[32m----> \u001b[39m\u001b[32m3\u001b[39m     dataFrame[\u001b[33m'\u001b[39m\u001b[33mpower_scores\u001b[39m\u001b[33m'\u001b[39m] = dataFrame[power_columns].mean(axis=\u001b[32m1\u001b[39m)\n\u001b[32m      4\u001b[39m     dataFrame[\u001b[33m'\u001b[39m\u001b[33minterest\u001b[39m\u001b[33m'\u001b[39m] = dataFrame[\u001b[33m'\u001b[39m\u001b[33mbetrokkenheid\u001b[39m\u001b[33m'\u001b[39m]\n",
      "\u001b[31mTypeError\u001b[39m: 'FileNotFoundError' object is not subscriptable"
     ]
    }
   ],
   "source": [
    "create_power_interest_columns(df)\n",
    "df['strategy'] = df.apply(lambda row: get_strategy(row['power_scores'], row['interest']), axis=1)\n",
    "\n",
    "\n",
    "for i, row in df.iterrows():\n",
    "    print(f\"Stakeholder: {row['stakeholder']}, power: {row['power_scores']}, interest: {row['interest']}, Strategy: {row['strategy']}\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b10ddf44-f965-4de1-825d-226509964e2f",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Plot stakeholders op kaart\n",
    "create_matrix_plot(df)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0a60b617-1557-4c8a-8e38-3790dd729f30",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
