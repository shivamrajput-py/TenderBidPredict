import numpy as np
import streamlit as st
import joblib  # To load saved models
import warnings
import locale
warnings.filterwarnings('ignore')

def currenc(currency, grouping=True):

    locale.setlocale( locale.LC_ALL, locale.getlocale())
    return locale.currency(currency, symbol=True, grouping= grouping)


# Custom CSS for styling the page
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# You can also include inline CSS for small customizations
def set_custom_css():
    st.markdown("""
    <style>
        /* Center the title */
        .title h1 {
            text-align: center;
            color: #0078D7;
            font-size: 3em;
        }
    

        /* Style the input field */
        .stNumberInput input {
            border-radius: 12px;
            border: 2px solid #0078D7;
        }

        /* Customize the subheaders */
        .subheader {
            font-weight: bold;
            color: #0078D7;
            text-align: center;
            margin-bottom: 20px;
        }

        /* Make the columns content more appealing */
        .pred-container {
            background-color: #526272;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        /* Prediction text styling */
        .pred-container h3 {
            color: #e5f9ff;  /* Set prediction text color to black */
        }

        /* Overall page styling */
        body {
            background-color: #F0F2F6;
        }
    </style>
    """, unsafe_allow_html=True)

# Load pre-trained models
@st.cache_resource
def load_models():
    rfr = joblib.load('rfr_model.pkl')
    lr = joblib.load('lr_model.pkl')
    return rfr, lr

def main():
    # Apply custom CSS
    set_custom_css()

    # Page title
    st.markdown("<div class='title'><h1>Bid Prediction Model By Vyvsai</h1></div>", unsafe_allow_html=True)

    # Load models
    rfr_model, lr_model = load_models()

    # User input section
    st.markdown("<div class='title2'><h3>Enter the Government Estimated Price</h3></div>", unsafe_allow_html=True)

    try:
        INPUT_GOV_PRICE = int(st.text_input("Gov Estimated Price: ", value='0'))
        NOERROR =  True
    except:
        st.error("ENTER INTEGER OR DECIMAL VALUES! NEEDS VALID INPUT TO PREDICT!")
        NOERROR = False

    if NOERROR and (INPUT_GOV_PRICE!=0):

        # Prepare input data
        input_data = np.array([[INPUT_GOV_PRICE, 0.0]])

        # Predictions
        rfr_prediction = rfr_model.predict(input_data)
        percentage_rfr = round(((rfr_prediction[0] - INPUT_GOV_PRICE)/INPUT_GOV_PRICE)*100 , 2)
        lr_prediction = lr_model.predict(input_data)
        percentage_lrp = round(((lr_prediction[0] - INPUT_GOV_PRICE)/INPUT_GOV_PRICE)*100 , 2)

        st.write(f'#### For Gov Estimated Price: {str(currenc(INPUT_GOV_PRICE))}')

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='subheader'> 1st Recommendation [RFR MODEL]</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='pred-container'><h3>Price: {currenc(rfr_prediction[0])}<br>Bid% : {str(percentage_rfr) + '%'}</h3></div>", unsafe_allow_html=True)


        with col2:
            st.markdown("<div class='subheader'>2nd Recommendation [LRP MODEL]</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='pred-container'><h3>Price: {currenc((lr_prediction[0]))}<br>Bid% : {str(percentage_lrp) + '%'}</h3></div>", unsafe_allow_html=True)


        # Add footer or additional info
        st.markdown("""
            <br><hr>
            <p style='text-align: center; font-size: 0.8em; color: grey;'>
            Vyvsai Private Limited
            </p>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
