from AI_talk import chat_with_gemini, Check_Connection
import streamlit as st


#"""
#This App is designed to allow the user to interact with Google's Gemini to look through a Ne04j database.
# This database stores information about the WV Housing Market. This allows the user to ask questions about the data. 
#"""

#This is used to check to see if the Neo4j Server is up. If it isn't it asks the user to contact the developer.
Check = Check_Connection()

if Check == False:
    st.write("The connection to the database seems to be down. Please contact the developer to see the status of the database.")

#This displays the title for the application. 
st.title("WV Housing Market")

#This displays a little introduction to the website and describes what it's job is.
st.write("Welcome to the WV Housing Market Application. Please input any questions you have about the Housing Market and our AI will help you.")

#This creates a session state to store what the user and AI have said and keeps it displayed on the website, so the user can look back through their conversation.
if "conversation" not in st.session_state:
    st.session_state.conversation = []

#Here is where the application stores the conversation between the user and AI into the session state.
for conversation in st.session_state.conversation:
    with st.chat_message(conversation["role"]):
        st.markdown(conversation["content"])

#This is where the user will interact with the AI. The user will type their question in the text box and hit enter to send thier question to the AI.
if userInput := st.chat_input("You: ", key="input"):

    #This will imedietly display what the user typed on the screen so they can see it.
    st.session_state.conversation.append({"role" : "user", "content" : userInput})
    with st.chat_message("user"):
        st.markdown(userInput)

    #This calls the function from the AI_talk python application to take what the user typed and try and answer their question.
    response = chat_with_gemini(userInput)

    #This takes what the AI responded with and displays it immedietly on the screen for the user to look through.
    st.session_state.conversation.append({"role" : "assistant", "content" : response})
    with st.chat_message("assistant"):
        st.markdown(response)
    