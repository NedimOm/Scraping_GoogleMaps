import pandas as pd
import logging
import difflib
import re
import ast
import yaml

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)


def extract_url(given_url):
    """
    Extracting name of site from given url
    :param given_url:  of possible website for facility
    :return: name of site
    """
    extracted = given_url.split('/')[2]
    extracted = extracted.split('.')

    if len(extracted) > 2 and extracted[0] != 'www':
        extracted = extracted[0] + extracted[1]
    elif len(extracted) > 2:
        extracted = extracted[1]
    else:
        extracted = extracted[0]

    logging.info(f"Extracted URL: {extracted}")
    return extracted


def form_name_of_site(facility_name):
    """
    Clearing and preparing name of facility for comparing with name of site
    :param facility_name: name of facility (i.e. Cube Smart)
    :return: cleaned and prepared name of facility (i.e. cubesmart)
    """
    lowercase_string = facility_name.lower()
    cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', lowercase_string)

    logging.info(f"Formed name of site from name of facility: {cleaned_string}")
    return cleaned_string


def clean_string(given_name):
    """
    Removing 'self' and 'storage' words from name, because they have high impact while comparing names
    :param given_name: name of facility
    :return: cleaned name of facility without words 'self' nor 'storage'
    """
    cleaned_string = given_name.replace('self', '')
    cleaned_string = cleaned_string.replace('storage', '')

    logging.info(f"Cleaned string: {cleaned_string}")
    return cleaned_string


def filter_urls():
    """
    Filtering urls and picking one url with best match for every facility that has possible websites
    """
    logging.info("Starting the URL filtering process.")

    with open(cfg['brand_sites'], 'r') as file:
        useful_urls = [line.strip() for line in file]

    facilities_with_possible_websites_df = pd.read_csv(cfg['facilities_with_possible_web'])
    found_websites = []
    popular_brand_websites = []

    for index, row in facilities_with_possible_websites_df.iterrows():
        name = row['name']
        urls = ast.literal_eval(row['possible_website'])
        website = 'NULL'

        name = form_name_of_site(name)
        name = clean_string(name)
        found_brand_in_url = False

        for url in urls:
            best = 0
            extracted_url = extract_url(url)
            cleaned_url = clean_string(extracted_url)
            temp = difflib.SequenceMatcher(None, name, cleaned_url)
            if temp.ratio() > 0.6 and temp.get_matching_blocks()[0].size-1 > len(name)/2 and cleaned_url != "":
                website = url
                best = temp.ratio()
                logging.info(f"Matched URL for {name}: {url} with ratio {best}")

            for brand_url in useful_urls:
                temp = difflib.SequenceMatcher(None, brand_url, extracted_url)
                if temp.ratio() > 0.99 and temp.ratio() > best:
                    website = url
                    best = temp.ratio()
                    found_brand_in_url = True
                    logging.info(f"Found popular brand URL: {url} for {brand_url} with ratio {best}")

        if found_brand_in_url:
            popular_brand_websites.append(True)
        else:
            popular_brand_websites.append(False)
        found_websites.append(website)

    facilities_with_possible_websites_df['website'] = found_websites
    facilities_with_possible_websites_df['popular_brand_website'] = popular_brand_websites
    facilities_with_possible_websites_df.to_csv(cfg['facilities_with_filtered_web'], index=False)
    logging.info("URL filtering process completed successfully.")
