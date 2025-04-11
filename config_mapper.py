import camelot
import logging
import pandas as pd
import json
from pathlib import Path

# from pathlib import Path
from openai import OpenAI
import os
from modules.configuration import ConfigurationParameters

def open_json_schema(workdir):
  file_path = workdir+'/third/json_schema.json'  # Replace with the actual file path
    # Read and process the JSON data
  with open(file_path, 'r') as file:
    return json.load(file)
  
  print("No JSON schema found")


def process_pdf(pdf_file):

    # Read tables from the PDF using camelot
    try:
        tables = camelot.read_pdf(str(pdf_file), flavor='lattice', pages='all')
    except Exception as e:
        print(f"Failed to read PDF {pdf_file.name}: {e}")
        logging.error(f"Failed to read PDF {pdf_file.name}: {e}")
        return

    if len(tables) == 0:
        print(f"No tables detected in {pdf_file.name}")
        logging.warning(f"No tables detected in {pdf_file.name}")
        return

    combined_df = pd.DataFrame()
    first_table = True
    header = None

    for i, table in enumerate(tables):
        table_df = table.df.reset_index(drop=True)

        if first_table:
            header = table_df.iloc[0]  # Assume the first row of the first table is the header
            combined_df = pd.DataFrame(table_df.iloc[1:].values, columns=header)
            first_table = False
        else:
            # Try to identify and remove header rows from subsequent tables
            current_header = table_df.iloc[0]
            if header is not None and current_header.equals(header):
                # If the first row matches the header of the first table, skip it
                data_rows = table_df.iloc[1:].values
                if data_rows.size > 0:
                    temp_df = pd.DataFrame(data_rows, columns=header)
                    combined_df = pd.concat([combined_df, temp_df], ignore_index=True)
            else:
                # If the header doesn't match, assume the first row is data
                if header is not None and table_df.shape[1] == len(header):
                    combined_df = pd.concat([combined_df, pd.DataFrame(table_df.values, columns=header)], ignore_index=True)
                else:
                    print(f"Warning: Header mismatch in table {i+1} of {pdf_file.name}. Concatenating raw data.")
                    logging.warning(f"Header mismatch in table {i+1} of {pdf_file.name}. Concatenating raw data.")
                    combined_df = pd.concat([combined_df, table_df], ignore_index=True)

    # display(combined_df)
    print("--------------------")
    return combined_df
    # display(combined_df.dropna())

def inference_llm(content, json_schema):
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = ""
    )

    prompt = f"""You are a helpful assistant that transforms tabular data into JSON format based on a provided JSON schema.

    Here is the tabular data:
    {content}


    And here is the JSON schema:
    {json_schema}
    Instructions:
    1. Map the table keys stricly to the JSON schema properties.
    2. Only filled parameters in JSON schema that has context provided from tabular data. 
    3. Return the result as pure JSON. Do not include any additional text or explanations."""

    messages = [{"role": "user", "content": prompt}]

    # Print the messages array (including the prompt)
    # print("Messages Array (Sent to LLM):")
    # print(json.dumps(messages, indent=2))  # Pretty print the messages

    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=messages,
        temperature=0.1,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    full_response = ""  # Initialize an empty string to accumulate the chunks
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
        #   print(chunk.choices[0].delta.content, end="")
            full_response += chunk.choices[0].delta.content  # Append the chunk to the full response

    clean_str = full_response.strip().removeprefix("```json").removesuffix("```").strip()
    # print(clean_str)
    return json.loads(clean_str)  # Parse the accumulated JSON string

    
def rictest_format(config_params:ConfigurationParameters):
    format_dict = {
        "Cell_Config": [
            {
                "Cell Type Name": "",
                "Number of Cells": 0,
                "band5G": "n79",
                "cellsConfig": [
                    {
                        "Configured Tx Power": 0,
                        "Height": 0,
                        "Azimuth": 0,
                        "Tilt": 0,
                        "Advanced traffic model": ""
                    }
                ]
            }
        ]
    }
    
    format_dict["Cell_Config"][0]["Cell Type Name"] = config_params.deploymentScale
    format_dict["Cell_Config"][0]["Number of Cells"] = config_params.numberOfCells
    format_dict["Cell_Config"][0]["band5G"] = config_params.band5G
    format_dict["Cell_Config"][0]["cellsConfig"][0]["Configured Tx Power"] = config_params.totalTransmitPowerIntoAntenna
    format_dict["Cell_Config"][0]["cellsConfig"][0]["Configured Tx Power"] = config_params.totalTransmitPowerIntoAntenna
    format_dict["Cell_Config"][0]["cellsConfig"][0]["Height"] = config_params.height
    format_dict["Cell_Config"][0]["cellsConfig"][0]["Azimuth"] = config_params.azimuth
    format_dict["Cell_Config"][0]["cellsConfig"][0]["Tilt"] = config_params.tilt
    format_dict["Cell_Config"][0]["cellsConfig"][0]["Advanced traffic model"] = config_params.tddDlUlRatio
    
    print("success formatting")
    return format_dict

if __name__ == "__main__":
    cwd = os.getcwd()  # Get the current working directory
    print(f"Current working directory: {cwd}")

    input_dir = Path(cwd+"/docs/")
    # print(f"Input directory: {input_dir}")
    # List each PDF in the input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    # Load the JSON schema
    json_schema = open_json_schema(cwd)
    # Initiate an empty list to store columns to drop
    cols_to_drop = []

    df = pd.DataFrame()

    for each in pdf_files:
        # Process the PDF and get the combined DataFrame
        df = process_pdf(each)

        # Get columns with integer names or single-character string names to be removed
        cols_to_drop = [col for col in df.columns if isinstance(col, int) or (isinstance(col, str) and col.isdigit() and len(col) == 1)]
       
        # Drop the identified columns
        df = df.drop(axis=1,labels=cols_to_drop)
        
        # Drop rows with all NaN values
        df = df.dropna()

        # Convert dataframe into json string
        json_data = df.to_json(orient='records')

        # Deserialize the JSON string into a JSON object
        json_deserialized = json.loads(json_data)

        llmresponse = []

        #iterate json array
        for json_object in json_deserialized:

            # stringify the JSON object
            content=json.dumps(json_object)

            # Perform inference with the LLM
            response_raw = inference_llm(content, json_schema)

            llmresponse.append(response_raw)

       
        for each in llmresponse:
            print(each)
            # Convert the dictionary to a ConfigurationParameters object
            config_params = ConfigurationParameters(**each)    
            # config_params.azimuth = each.get("azimuth")
            # config_params.tilt = each.get("tilt")
            # config_params.height = each.get("height")
            # config_params.numberOfCells = each.get("numberOfCells")
            # config_params.deploymentScale = each.get("deploymentScale")
            # config_params.band5G = each.get("band5G")
            # config_params.tddDlUlRatio = each.get("tddDlUlRatio")
            # config_params.totalTransmitPowerIntoAntenna = each.get("totalTransmitPowerIntoAntenna")
            print(rictest_format(config_params))

    print("Script execution finished.")

   