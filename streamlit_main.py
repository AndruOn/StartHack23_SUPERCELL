import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title('Grooming detection in Clash Royale chats')



import base64
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('background/sober_blue.jpg')   




@st.cache_data
def load_data_messages():
    #Index(['account_id', 'alliance_id', 'timestamp', 'raw_message', 'filtered_message', 'CHILD_GROOMING', 'hour_bucket'],
    messages_df = pd.read_csv('csv_frontEnd/messages_df.csv',low_memory=False)
    
    return messages_df

@st.cache_data
#SORTED DATA
def load_data_convs():
    #Index(['Unnamed: 0', 'account_id', 'alliance_id', 'scores', 'conv_str_list'], dtype='object')
    alliances_account_scores_df = pd.read_csv('csv_frontEnd/alliance_account_score_conv.csv',low_memory=False)
    #SORTED DATA
    return alliances_account_scores_df


# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load all data into the dataframe.
messages_df = load_data_messages()
alliances_account_scores_df = load_data_convs()
# Notify the reader that the data was successfully loaded.
data_load_state.text("Data Loaded! (using st.cache_data)")




st.header('Move the slide to see the outputs of our model for the messages sent at a certain hour')


hour_to_filter = st.slider('Hour', 1, 24, 17)  # min: 0h, max: 23h, default: 17h


#prepare data for certain hour--------------------------------------



#show top 5
top_n = 5

hour_filtered_messages =  messages_df[messages_df['hour_bucket']==hour_to_filter]

hour_filtered_alliances_account_scores_df = alliances_account_scores_df[
    (alliances_account_scores_df['alliance_id'].isin(hour_filtered_messages['alliance_id']) ) &
    (alliances_account_scores_df['account_id'].isin(hour_filtered_messages['account_id']) )
]


#if less than top_n different convs from triggered messages
if len(hour_filtered_alliances_account_scores_df) < top_n:
    top_n = len(hour_filtered_alliances_account_scores_df)


worst_alliances_account_score = hour_filtered_alliances_account_scores_df.iloc[:top_n]

worst_trigger_msg_df = hour_filtered_messages[
    (hour_filtered_messages['alliance_id'].isin(worst_alliances_account_score['alliance_id']) ) &
    (hour_filtered_messages['account_id'].isin(worst_alliances_account_score['account_id']) )
]

if st.checkbox('Show raw data'):
    st.subheader('raw trigger data')
    st.write(hour_filtered_messages)
    st.subheader('raw hour_filtered_alliances_account_scores_df')
    st.write(hour_filtered_alliances_account_scores_df)
    st.subheader('raw worst_alliances_account_score')
    st.write(worst_alliances_account_score)
    st.subheader('raw worst_trigger_msg_df')
    st.write(worst_trigger_msg_df)



st.header(f"Messages sent from from {hour_to_filter}:00 to {hour_to_filter+1}:00 showing the {top_n} best")


st.subheader(f'Triggered messages with SUPERCELL risk values from -1 to 7 (CHILD_GROOMING top, RELATIONSHIP_SEXUAL_CONTENT bottom) ')
#st.write('CHILD_GROOMING risk')
#st.write('RELATIONSHIP_SEXUAL_CONTENT risk')

columns = st.columns(top_n)
for i in range(len(columns)):
    with columns[i]:
        message_line = worst_trigger_msg_df.iloc[i]
        st.write(message_line['filtered_message'])
        results_SUPERCELL='CHILD_GROOMING:' + str(message_line['CHILD_GROOMING']) + '  ' + 'RELATIONSHIP_SEXUAL_CONTENT' + str(message_line['CHILD_GROOMING'])
        #st.write(results_SUPERCELL)
        st.write(message_line['CHILD_GROOMING'])
        st.write(message_line['RELATIONSHIP_SEXUAL_CONTENT'])

#st.write(worst_trigger_msg_df[['filtered_message','CHILD_GROOMING']].values)


st.subheader(f'Most problematic conversation: our token charge value from 0=not at all to ????= definitely groomer')

def str_list_to_paragraph(str_list):
    paragraph = ''
    for str in str_list:
        paragraph = paragraph+ ' ' + str
    return paragraph

columns = st.columns(top_n)
for i in range(len(columns)):
    with columns[i]:
        conv_line = worst_alliances_account_score.iloc[i]
        st.write(conv_line['scores'])
        st.text(conv_line['paragraph'])
        #with st.expander("See conversation"):
        #    st.text(conv_line['paragraph'])
    