import streamlit as st
from core.fuzzy import FuzzyEngine

# Initialize the fuzzy engine (same as before)
client = None  # You can set your MongoDB client connection here
engine = FuzzyEngine(client)

# Streamlit app
st.title("Fuzzy Query on Football Videos")

# User input for query
query = st.text_input('Enter your query (e.g., "Find referees moving at moderate speed and near distance")')
st.text('Distance: near | medium | large \nSpeed: slow | moderate | fast')

# Process the query
if query:
    subject, action, attribute, fuzzy_value = engine.parse_natural_language_query(query)
    print(fuzzy_value,attribute,subject)
    fuzzy_sets = {
        'entity_type':subject
    }
    fuzzy_sets = engine.attach(fuzzy_sets,attribute,fuzzy_value)
    print(fuzzy_sets)
    results = engine.execute_fuzzy_query(fuzzy_sets)
    
    # Display results
    if results:
        st.write(f'Top {len(results)} results for the query "{query}":')
        
        # Create a pandas DataFrame for easy tabular display
        import pandas as pd
        df = pd.DataFrame(results)
        st.dataframe(df)  # Displaying the table
    else:
        st.write("No results found for the query.")
