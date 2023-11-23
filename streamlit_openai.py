# -*- coding: utf-8 -*-
"""streamlit-openai.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IKhtBhkSDqeb7RP5Fb17f-Nhg6XzvdAB
"""

import streamlit as st
from openai import OpenAI
import requests
import json

# CPIC API URLs
cpic_api_url = "https://api.cpicpgx.org/v1/"
drug_api_url = cpic_api_url + "drug"
guideline_api_url = cpic_api_url + "guideline"
recommendation_view_api_url = cpic_api_url + "recommendation_view"

# Functions for API calls

def get_drug():
    choices = ['codeine', 'abacavir', 'simvastatin']
    drug = st.selectbox("Select Drug", choices)
    return drug

def get_lookup_keys_for_query(drug):
    lookup_keys_values = get_lookup_keys_for_drug(drug)

    if lookup_keys_values:
        lookup_key = st.selectbox("Select a lookup key", list(lookup_keys_values.keys()))

        lookup_values = lookup_keys_values[lookup_key]
        lookup_value = st.selectbox(f"Select a lookup value for {lookup_key}", list(lookup_values))

        return lookup_key, lookup_value

    st.error("Failed to retrieve lookup keys.")
    return None

def get_lookup_keys_for_drug(drug):
    url = f"{recommendation_view_api_url}?drugname=eq.{drug}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            lookup_keys_values = {}

            for recommendation in data:
                lookup_key_values = recommendation.get("lookupkey", {})
                for key, value in lookup_key_values.items():
                    if key not in lookup_keys_values:
                        lookup_keys_values[key] = set()
                    lookup_keys_values[key].add(value)

            return lookup_keys_values

        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

def get_recommendation_for_specific_drug(drug, gene, phenotype):
    url = f"{recommendation_view_api_url}?drugname=eq.{drug}&lookupkey=cs.{{%22{gene}%22:%20%22{phenotype}%22}}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            st.write("CPIC Recommendations:")
            # st.json(response.json())
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

def generate_openai_completion(input_json):
    client = OpenAI(api_key=openai_api_key)
    prompt = f"You are a pharmacist that must interpret this JSON object that you just received from a CPIC API: {input_json}, please summarize this information back to the consulting physician. Be sure to include the name of the guideline mentioned in the JSON object and a link to the url in case the physician wants more information"
    try:
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1000
        )
        answer = response.choices[0].text
        st.write(answer)
    except Exception as e:
        st.error(f"Error: {e}")

# Streamlit app
if __name__ == "__main__":
    st.title("CPIC API Explorer")

    # Get user input
    drug = get_drug()
    gene, phenotype = get_lookup_keys_for_query(drug)

    # Display results
    st.subheader("OpenAI Summary")
    rec = get_recommendation_for_specific_drug(drug, gene, phenotype)
    if rec:
        generate_openai_completion(rec)

    #st.subheader("Original")
    #if gene and phenotype:
        # Get recommendations for specific drug
    #     get_recommendation_for_specific_drug(drug, gene, phenotype)