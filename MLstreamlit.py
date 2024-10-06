import numpy as np
import streamlit as st
import joblib  # To load saved models
import warnings
import locale
import pandas as pd
warnings.filterwarnings('ignore')

def currenc(currency, grouping=True):

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
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


.css-15zrgzn {display: none}
.css-eczf16 {display: none}
.css-jn99sy {display: none}

/* FOR REMOVING THE SIDE BAR COMPLETELY */
[data-testid="collapsedControl"] {
        display: none
    }
/* */
#root > div:nth-child(1) > div.withScreencast > div > div > div > section:nth-child(2) {
                    height: 3rem !important;
                }
/* FOR ADJUSTING EXTRA SPACE AROUND THE WHOLE PAGE */
.block-container {
    padding-top: 23px;
    padding-bottom: 5rem;
    padding-left: 0rem;
    padding-right: 0rem;
}


#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stToolbar"] {visibility: hidden !important;}
footer {visibility: hidden !important;}

</style>
    """, unsafe_allow_html=True)

# Load pre-trained models
@st.cache_resource
def load_models():

    # FOR BRIDGE
    rfr = joblib.load('rfr_model.pkl')
    lr = joblib.load('lr_model.pkl')

    # FOR ELECTRICAL WORK
    ee_model = joblib.load('linearElectrical_model.pkl')
    return rfr, lr, ee_model

def main():

    set_custom_css()

    # Page title
    st.markdown("<div class='title'><h1>Bid Prediction Model By Vyvsai</h1></div>", unsafe_allow_html=True)

    chosedcat = st.selectbox("SELECT CATEGORY OF THE WORK:", ['Electrical Work', 'Bridges'])

    if chosedcat == 'Bridges':

        rfr_model, lr_model, _ = load_models()

        # st.markdown('---')
        left, right = st.columns(2)

        try:
            with left:
                st.markdown('###### ')
                INPUT_GOV_PRICE = int(st.text_input("GOV ESTIMATED TENDER PRICE:", value='0'))
            NOERROR = True
        except:
            st.error("ENTER INTEGER VALUED PRICE ONLY! NEEDS VALID INPUT TO PREDICT!")
            NOERROR = False

        with right:
            st.markdown('#### ')
            predict = st.button("Predict Bid Won Price")

        if NOERROR and (INPUT_GOV_PRICE != 0) and predict:

            # Prepare input data
            input_data = np.array([[INPUT_GOV_PRICE, 0.0]])

            # Predictions
            rfr_prediction = rfr_model.predict(input_data)
            percentage_rfr = round(((rfr_prediction[0] - INPUT_GOV_PRICE) / INPUT_GOV_PRICE) * 100, 2)
            lr_prediction = lr_model.predict(input_data)
            percentage_lrp = round(((lr_prediction[0] - INPUT_GOV_PRICE) / INPUT_GOV_PRICE) * 100, 2)

            st.write(f'#### For Gov Estimated Price: {str(currenc(INPUT_GOV_PRICE))}')

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<div class='subheader'> 1st Recommendation [RFR MODEL]</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='pred-container'><h3>Price: {currenc(rfr_prediction[0])}<br>Bid% : {str(percentage_rfr) + '%'}</h3></div>",
                    unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='subheader'>2nd Recommendation [LRP MODEL]</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='pred-container'><h3>Price: {currenc((lr_prediction[0]))}<br>Bid% : {str(percentage_lrp) + '%'}</h3></div>",
                    unsafe_allow_html=True)

            # Add footer or additional info
            st.markdown("""
                    <br><hr>
                    <p style='text-align: center; font-size: 0.8em; color: grey;'>
                    Vyvsai Private Limited
                    </p>
                """, unsafe_allow_html=True)

#-----------------------------------------------------------------------------------------------------------

    elif chosedcat == 'Electrical Work':
        _, _ , model = load_models()

        # st.markdown('---')
        left, right = st.columns(2)

        try:
            with left:
                st.markdown('###### ')
                INPUT_GOV_PRICE = int(st.text_input("GOV ESTIMATED TENDER PRICE:", value='0'))
            NOERROR = True
        except:
            st.error("ENTER INTEGER VALUED PRICE ONLY! NEEDS VALID INPUT TO PREDICT!")
            NOERROR = False

        with right:
            st.markdown('#### ')
            predict = st.button("Predict Bid Won Price")

        # Button to trigger prediction
        if NOERROR and (INPUT_GOV_PRICE != 0) and predict:

            custom_re_df = pd.DataFrame(data={'bid_won_price': [INPUT_GOV_PRICE]})

            # Make a prediction
            custom_pred = model.predict(custom_re_df)

            percentage_ee_model = round(((custom_pred[0] - INPUT_GOV_PRICE) / INPUT_GOV_PRICE) * 100, 2)

            st.write(f'#### For Gov Estimated Price: {str(currenc(INPUT_GOV_PRICE))}')

            st.markdown("---")

            _ , col1, _ = st.columns([0.75, 1.5, 0.75])

            with col1:
                st.markdown("<div class='subheader'>Model Recommendation Says:</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='pred-container'><h3>Price: {currenc(round(custom_pred[0], 0))}<br>Bid% : {str(percentage_ee_model) + '%'}</h3></div>",
                    unsafe_allow_html=True)


            # Add footer or additional info
            st.markdown("""
                                <br><hr>
                                <p style='text-align: center; font-size: 0.8em; color: grey;'>
                                Vyvsai Private Limited
                                </p>
                            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()





