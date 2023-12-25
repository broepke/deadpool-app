"""
Scraper for NNDB
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd


def parse_linked_page(soup):
    # Extracting name from the title tag
    title_tag = soup.find("title")
    name = title_tag.text.strip() if title_tag else "N/A"

    # Extracting AKA
    aka_tag = soup.find("b", string="AKA")
    aka = aka_tag.next_sibling.strip() if aka_tag else "N/A"

    # Extracting birth details
    born_tag = soup.find("b", string="Born:")
    if born_tag:
        # Initialize born_parts list
        born_parts = []
        # Iterate over the next siblings
        for sibling in born_tag.next_siblings:
            if sibling.name == "a":  # Check if the sibling is an 'a' tag
                born_parts.append(sibling.text)
            elif sibling.name == "br":  # Break loop when reaching a 'br' tag
                break
        born = " ".join(born_parts).strip()
    else:
        born = "N/A"

    # Extracting birthplace
    birthplace_tag = soup.find("b", string="Birthplace:")
    if birthplace_tag:
        birthplace_part = birthplace_tag.next_sibling
        birthplace = birthplace_part.strip() if birthplace_part else "N/A"
    else:
        birthplace = "N/A"

    # Extracting gender, race or ethnicity, occupation
    gender_tag = soup.find("b", string="Gender:")
    gender = gender_tag.next_sibling.strip() if gender_tag else "N/A"

    race_tag = soup.find("b", string="Race or Ethnicity:")
    race = race_tag.next_sibling.strip() if race_tag else "N/A"

    occupation_tag = soup.find("b", string="Occupation:")
    occupation = occupation_tag.next_sibling.strip() if occupation_tag else "N/A"

    # Extracting nationality
    nationality_tag = soup.find("b", string="Nationality:")
    nationality = nationality_tag.next_sibling.strip() if nationality_tag else "N/A"

    # Extracting executive summary
    exec_summary_tag = soup.find("b", string="Executive summary:")
    executive_summary = (
        exec_summary_tag.next_sibling.strip() if exec_summary_tag else "N/A"
    )

    # Extracting death details
    died_tag = soup.find("b", string="Died:")
    if died_tag:
        # Initialize died_parts list
        died_parts = []
        # Iterate over the next siblings
        for sibling in died_tag.next_siblings:
            if sibling.name == "a":  # Check if the sibling is an 'a' tag
                died_parts.append(sibling.text)
            elif sibling.name == "br":  # Break loop when reaching a 'br' tag
                break
        died = " ".join(died_parts).strip()
    else:
        died = "N/A"

    location_of_death_tag = soup.find("b", string="Location of death:")
    location_of_death = (
        location_of_death_tag.next_sibling if location_of_death_tag else "N/A"
    )

    cause_of_death_tag = soup.find("b", string="Cause of death:")
    cause_of_death = (
        cause_of_death_tag.next_sibling.strip() if cause_of_death_tag else "N/A"
    )

    risk_factors = []

    risk_factors_elements = soup.find_all(string=lambda text: 'Risk Factors:' in text)
    risk_factors_label = risk_factors_elements[0] if risk_factors_elements else None

    if risk_factors_label:
        for sibling in risk_factors_label.next_siblings:
            if sibling.name == "a":  # Check if the sibling is an 'a' tag
                risk_factors.append(sibling.text.strip())
            elif sibling.name == "br":  # Break loop when reaching a 'br' tag
                break

    risk_factors_string = "; ".join(risk_factors)

    return (
        name,
        aka,
        born,
        birthplace,
        gender,
        race,
        occupation,
        nationality,
        executive_summary,
        died,
        location_of_death,
        cause_of_death,
        risk_factors_string,
    )


def scrape_website(link_url):
    # Initialize DataFrame with the necessary columns
    data = pd.DataFrame(
        columns=[
            "Link",
            "Name",
            "AKA",
            "Born",
            "Birthplace",
            "Gender",
            "Race",
            "Occupation",
            "Nationality",
            "Executive Summary",
            "Died",
            "Location of Death",
            "Cause of Death",
            "Risk Factors",
        ]
    )

    linked_page_response = requests.get(link_url)
    if linked_page_response.status_code == 200:
        linked_page_soup = BeautifulSoup(linked_page_response.content, "html.parser")
        # Extract data from the linked page
        (
            name,
            aka,
            born,
            birthplace,
            gender,
            race,
            occupation,
            nationality,
            executive_summary,
            died,
            location_of_death,
            cause_of_death,
            risk_factors_string,
        ) = parse_linked_page(linked_page_soup)

        # Append the data to the DataFrame
        data = pd.concat(
            [
                data,
                pd.DataFrame(
                    [
                        {
                            "Link": link_url,
                            "Name": name,
                            "AKA": aka,
                            "Born": born,
                            "Birthplace": birthplace,
                            "Gender": gender,
                            "Race": race,
                            "Occupation": occupation,
                            "Nationality": nationality,
                            "Executive Summary": executive_summary,
                            "Died": died,
                            "Location of Death": location_of_death,
                            "Cause of Death": cause_of_death,
                            "Risk Factors": risk_factors_string,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

        print("Name:", name)
        print("AKA:", aka)
        print("Born:", born)
        print("Birthplace:", birthplace)
        print("Gender:", gender)
        print("Race:", race)
        print("Occupation:", occupation)
        print("Nationality:", nationality)
        print("Summary:", executive_summary)
        print("Died:", died)
        print("Location of Death:", location_of_death)
        print("Cause of Death:", cause_of_death)
        print("Risk Factors:", risk_factors_string)

        print(f"Content from {link_url} scraped successfully")

    return data


scraped_data = scrape_website("https://www.nndb.com/people/851/000022785/")

