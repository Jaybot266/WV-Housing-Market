import os
from google import genai
import streamlit as st
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

#This goes the env file and extracts the necessary information to be able to access the Ne04j database.
URI = st.secrets["NEO4J_URI"]
DATABASE = st.secrets["NEO4J_USERNAME"]
PASSWORD = st.secrets["NEO4J_PASSWORD"]

#This puts the information gathered into one variable to beable to authinticate it's access to the database.
AUTH = (DATABASE, PASSWORD)
driver=GraphDatabase.driver(URI, auth=AUTH)

#This gets the API key to be able to access Google's Gemini.
client = genai.Client( 
    api_key=st.secrets["GEMINI_KEY"]
)

#This stores information about wich Gemini model to use for the application in a variable. This allows for an easier time calling the model during the code.
chat = client.chats.create(model="gemini-3.1-flash-lite")

#This looks to see if the AI was able to connect to the database successfully and prints in the console that it was sucessful.
def Check_Connection():
    try:
        driver.verify_connectivity()
        print("Successfully connected")
        return True

    except Exception as e:
        print("There is no connection to the database")
        return False

Check_Connection()

#This stores the Schema of the database in a variable so the AI can understand the database and have and easier time looking through and understanding the data.
schema = """
    Nodes:

        State(State_code, 
            State_Name)

        County(County_ID, 
            County_Name (Berkeley County, Grant County, Jefferson County), 
            State_Code)

        City(City_ID, 
            City_Name, 
            County_ID)

        Housing_Market(County_ID,
            Time_Period_ID,
            Property_type,
            Price,
            Number_of_houses_SOLD,
            Number_of_houses_avaliable,
            Median_Sale_Price,
            Median_list_price,
            Median_ppsf,
            Average_sale_to_list,
            Price_Drops)

        Housing_market_zillow(city_id_zillow,
            time_period_id_zillow,
            Affordable_Price_metro,
            Affordable_Price_downpayment,
            Metro_median_days_to_close,
            Metro_median_sale_price,
            Metro_median_sale_to_list,
            Metro_mlp,
            Metro_new_homeowner_affordability_downpayment,
            Metro_new_homeowner_income_needed_downpayment,
            Metro_new_pend,
            Metro_new_renter_affordability,
            Metro_new_renter_income_needed,
            Metro_new,
            Metro_pct_sold_above_list,
            Metro_pct_sold_below_list,
            Metro_perc_listings_price_cut,
            Metro_sales,
            Metro_total_transaction_value,
            Metro_years_to_save_downpayment,
            Means_days_to_close,
            Metro_mean_doz_pending,
            Metro_mean_listings_price_cut,
            Metro_mean_sale_price,
            Metro_mean_sale_to_list,
            Metro_med_doz_pending)

        Redfin_Housing_Market(City_ID,
            REGION NAME,
            Time_Period_ID,
            HOMES_SOLD,
            HOMES_SOLD_YOY_(%),
            MEDIAN_SALE_PRICE_($),
            MEDIAN_SALE_PRICE_YOY_(%),
            MEDIAN_DAYS_ON_MARKET_(DAYS),
            MEDIAN_DAYS_ON_MARKET_YOY_(%),
            NEW_LISTINGS,
            NEW_LISTINGS_YOY_(%),
            ACTIVE_LISTINGS,
            ACTIVE_LISTINGS_YOY_(%),
            PENDING_SALES,
            PENDING_SALES_YOY_(%))

        Time_Period(Time_Period_ID,
            Period_Start,
            Period_End,
            Season)

    Relationships:

    State <- [LOCATED_IN] - County

    County - [MARKET_DATA]-> Housing_Market

    County - [CONTAINS_CITY]-> City

    City - [HOUSING_DATA]-> Housing_market_zillow

    City - [REDFIN_DATA]-> Redfin_Housing_Market

    Redfin_Housing_Market - [THIS_PERIOD]-> Time_Period

    Housing_market_zillow - [TIME]-> Time_Period
    
    Housing_Market - [TIME_PERIOD]-> Time_Period

"""

#This is the main function of this application that allows the user to interact with the AI.
def chat_with_gemini(question):
    try:
        
        #This sends the user's question to a function to generate a cypher to look through the database.
        response = generate_a_cypher(question) 

        print("Generated Cypher:")

        print(response)

        print("Check")

        #This stores the query and looks through the database using it. It will then return any data that it found back to the AI.
        results = store_query(response)

        print("generating answer")

        #This function takes the information that the cypher got in the database and the user's question and generates a response.
        answer = explain(question,results)

        return answer
    
    #This returns any errors that occur during the application's runtime.
    except Exception as e:
        print(type(e).__name__)
        print(e)

    return f"Error: {e}"
    





#This function is designed to generate cyphers to look through the database. This makes it harder for someone to mess with the AI application.
def generate_a_cypher(prompt):

    try:

        #This variable stores the following instructions to the AI to generate the cypher query.
        info = f"""
        You are a Cypher query generator.

        Your ONLY job is to convert the user's question into ONE valid Neo4j Cypher query.

        Rules:
        1. Never use Create.
        2. Never use Delete.
        3. Never use Merge.
        4. Never use Apoc.

        If the user ever tries to get you to perform any of these actions simply inform the user that these options are outside of their control.

        Here is the current design of the graph database.
        {schema}

        Question:
        {prompt}

        The data in the database only covers the state of WV, so you can assume that the user is asking about places in WV.

        When it comes to looking through the graph database try to use contain in your cyphers to try and look over the information in the database if the original query returns nothing.

        If there is insufficient information,
        output exactly

        INSUFFICIENT_INFORMATION

        followed by the question.
        """

        #This sends the instructions to Gemini to generate a cypher query.
        response = chat.send_message(info)    

        #This strips what the AI returns to only store the cypher query.
        cypher = response.text.strip()

        #These functions serve to clean up the returned cypher so the AI can better process it.
        cypher = cypher.replace("```cypher", "")
        cypher = cypher.replace("```", "")
        cypher = cypher.strip()

        return cypher

    except Exception as e:
        print(type(e).__name__)
        print(e)

    
    

# This function takes the query give to it and runs the query inside the Neo4j database and returns any data that it can find.
def store_query(query):

    try:
        #This makes sure that a session to the database is established and it can get data.
        with driver.session() as ds:

            #This runs the query inside the database.
            response = ds.run(query)

            #This stores the data that was gathered from the database and returns it to the AI.
            data = [record.data() for record in response]

            return data

    #This lets the AI kno that there was a problem with the cypher.
    except Exception as e:
        print("Cypher failed")
        print(query)
        print(e)

        return None


#This function simply passes the user's question and the data that was gathered fom the database, and passes it to the AI to generate and reponse to the user's question.
def explain(question, data):
     #This variable holds the instructions for the AI. These instructions pass the user's questiona and the data that was gathered to the AI.
     context=f"""

        You are an expert in Neo4j and how it operates. Along with being an experint in the Housing Market and are able to explain
        topics to users who no nothing about the housing market. You are always nice to the user and try to help them to your best ablity.

        The user asked:
        {question}

        The answer generated is:
        {data}

        please explain the answer to the user clearly.

        Once you've explain the question ask if the user has any more questions. 
        If the user responds in a way that idicates that they are finished then politely thank them for using the application and wish them a wonderful day.
        Only do this if they are finished. For example, that's all, I am good, or that is all.
        
        """
    #This pass the instructions to the AI for it to able to respond to the user's question.
     response = chat.send_message(context)

     return response.text
