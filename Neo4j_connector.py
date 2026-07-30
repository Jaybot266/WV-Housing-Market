import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()



#This allows this application to connect to Neo4j aura
URI = os.getenv("NEO4J_URI")
DATABASE = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
AUTH = (DATABASE, PASSWORD)

Active = True

def connect_to_Neo4j(input):
#Here is where the application will try to set up a connectiong to Neo4j aura by using the preveous constaints
    try:
        #If successful the application will let the user know that it successful connected with Neo4j aura
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print("Successfully connected")

                        #The application will try to run the user's input. If successful the loop will break and their command will be executed.
            try:
                records, summary, keys = driver.execute_query(
                        input,
                        database_=DATABASE,
                        )
                

                            
            except:
                raise
                            

            print("\n Your query was successful \n")

            return records 

             
                
    #If there are any errors this will say that there was an error and say what kind of error it was
    except Exception as e:
        print(type(e).__name__)
        print(e)




