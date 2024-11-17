import streamlit as st

# Set up the Streamlit interface
st.title("Fuzzy Query Processing")

# Define the adjectives
distance_options = ['near', 'medium', 'far']
speed_options = ['slow', 'moderate', 'fast']

# Create a bordered box around Distance adjectives
st.markdown("""
    <style>
    .box {
        border: 2px solid black;
        padding: 10px;
        display: inline-block;
        margin-right: 10px;  /* Space between boxes */
    }
    .inline {
        display: flex;
        flex-wrap: wrap;
        justify-content: start;
    }
    </style>
    """, unsafe_allow_html=True)

# Display the adjectives inside the boxes on the same line
st.write('### Distance:')
st.markdown('<div class="inline">', unsafe_allow_html=True)
for option in distance_options:
    st.markdown(f'<div class="box">{option}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write('### Speed:')
st.markdown('<div class="inline">', unsafe_allow_html=True)
for option in speed_options:
    st.markdown(f'<div class="box">{option}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
