def process_dataset(df):
    df['location_new'] = df.locations 
    df['location_new'] = df.location_new.map(lambda x: x.strip('[]')) #Remove brackets
    
    # Define function to convert strings into Dict
    def string_to_dict(dict_string):
        # Convert to proper json format
        dict_string = dict_string.replace("'", '"')
        return json.loads(dict_string)

    # Apply the function to the whole column & convert strings to Dict
    df.location_new = df.location_new.apply(string_to_dict)
    
    # Create new lat & longitude columns
    df['latitude'] = df.location_new.map(lambda x: x['lat'])
    df['longitude'] = df.location_new.map(lambda x: x['lon'])
    
    # Split text to columns we do this because there are several "dicts" inside the string
    df[['1','2','3','4','5','6','7','8','9']] = df['parameters'].str.split('(?<=},)\s', expand=True)
    
    # Rename columns
    df = df.rename(columns={"locations_resolved.ADMIN_LEVEL_3_name":"City","1": "Tipo", "2": "Bedrooms", 
                            "3":"Bathrooms", "4":"Surface"})
    df = df.drop(['5','6','7','8','9'], axis=1)
    
    # Drop rows with missing values
    df = df.dropna(subset=["Bedrooms","Bathrooms","Surface"])
    
    #Remove brackets and comma at the end
    df.Tipo = df.Tipo.map(lambda x: x.strip('[],')) 
    df.Bedrooms = df.Bedrooms.map(lambda x: x.strip('[],')) 
    df.Bathrooms = df.Bathrooms.map(lambda x: x.strip('[],'))
    df.Surface = df.Surface.map(lambda x: x.strip('[],'))
    
    # Apply the function to the whole column & convert strings to Dict
    df.Tipo = df.Tipo.apply(string_to_dict)
    df.Bedrooms = df.Bedrooms.apply(string_to_dict)
    df.Bathrooms = df.Bathrooms.apply(string_to_dict)
    df.Surface = df.Surface.apply(string_to_dict)
    
    # Assign only the values to the columns (values from the dict)
    df['Tipo'] = [d.get('value') for d in df["Tipo"]]
    df['Bedrooms'] = [d.get('value') for d in df["Bedrooms"]]
    df['Bathrooms'] = [d.get('value') for d in df["Bathrooms"]]
    df['Surface'] = [d.get('value') for d in df["Surface"]]
    
    # Define list of variables to be converted from str to int
    var_obs = ['Bedrooms','Bathrooms']

    # Loop through the list to change the variable type
    for var in var_obs:
        df[var] = df[var].astype('int64')
    
    # Create a new column with the zone, which is the same as the one we already have (it might be useful to have a copy later)
    df['Zone'] = df['locations_resolved.SUBLOCALITY_LEVEL_1_name']
    # Drop rows in which the Zone value is missing
    df = df.dropna(subset=['Zone'])
    # Create a new column with only the int value of each Zone
    df['Zone_Val'] = df['Zone'].str.extract('(\d+)').astype(int)
    
    # Create a new column price, which is exactly the same as the one we have already but we'll use this one to
    #transform values in Q to USD, so we have a single column with all of the prices in USD.
    df['Price_USD'] = df['price.value.raw']

    # Select all of the rows that have the price in Q and then we apply a transformation to have everything in USD
    df.loc[df['price.value.currency.pre'] == 'Q', 'Price_USD'] = df['Price_USD']/7.65
    df['Price_USD'] = round(df['Price_USD'],2) #Round to only two digits
    
    # Exclude the rows in which "Surface" contains "hasta"
    df = df[~df.Surface.str.contains("hasta")]
    
    # Create a new column for price per square meter
    df['Surface'] = df['Surface'].astype('float64') # Convert surface from str to int
    df['Price_m2_USD'] = round(df['Price_USD']/df['Surface'],2)
    
    # Drop duplicates based on specific columns
    df = df.drop_duplicates(subset=['latitude','longitude','Price_USD'])
    
    # REMOVE OUTLIERS
    # set up the capper (right) 
    capper_right = outr.OutlierTrimmer(distribution='skewed', tail='right', fold=2, variables=['Surface','Price_m2_USD'])
    # fit the capper (right)
    capper_right.fit(df)
    # transform the data
    df2 = capper_right.transform(df)
    
    # set up the capper (left) 
    capper_left = outr.OutlierTrimmer(distribution='quantiles', tail='left', fold=0.02, variables=['Surface','Price_m2_USD'])
    # fit the capper (left)
    capper_left.fit(df)
    # transform the data
    df3 = capper_left.transform(df2)
    
    # Pre-2021 set
    '''columns = ['id','republish_date','created_at','title','valid_to','images','revision','display_date','user_id',
           'created_at_first','City','latitude', 'longitude', 'Tipo', 'Bedrooms','Bathrooms', 'Surface', 
           'Zone', 'Zone_Val','Price_USD', 'Price_m2_USD']'''
    # Post-2021 set
    columns = ['id','created_at','title','images','display_date','user_id',
           'created_at_first','City','latitude', 'longitude', 'Tipo', 'Bedrooms','Bathrooms', 'Surface', 
           'Zone', 'Zone_Val','Price_USD', 'Price_m2_USD']
    df3 = df3[columns]
    return df3