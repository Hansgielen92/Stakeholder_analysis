#Create function to synthesize assesment input
def synthesize_assessment_input(file_path):
    pattern = os.path.join(file_path, '*.csv')
    csv_files = glob.glob(pattern)

    all_data = []

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in the folder: {file_path}")

    #Doorloop alle csv bestanden en voeg ze samen in een dataframe
    for file in csv_files:
        temp_df = pd.read_csv(file, sep=';')
        all_data.append(temp_df)

    #Combineer alle dataframes in één dataframe
    combined_df = pd.concat(all_data, ignore_index=True)

    #Logica om de gecombineerde dataframe te verwerken en te synthetiseren
    aggregated_logic = {
        'formeel': 'mean',
        'informatie': 'mean',
        'informeel': 'mean',
        'legitimiteit': 'mean',
        'betrokkenheid': 'mean',
        'waarom': lambda x: ' | '.join(set(x))
    }

    synthesis = combined_df.groupby('stakeholder').agg(aggregated_logic).reset_index()
    #Mogelijk later toevoegen om af te ronden
    return synthesis

#Logica om strategie te bepalen op basis van power en interest score
def get_strategy(power, interest): #nodig: power en interest score op basis van input)
    if power >= 4 and interest >= 4: return "Manage closely"
    if power >= 4 and interest < 4: return "keep satisfied"
    if power < 4 and interest >= 4: return "keep informed"
    return "Monitor only"