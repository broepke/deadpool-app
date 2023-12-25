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
    occupation = (occupation_tag.next_sibling.strip()
                  if occupation_tag
                  else "N/A")

    # Extracting nationality
    nationality_tag = soup.find("b", string="Nationality:")
    nationality = (nationality_tag.next_sibling.strip()
                   if nationality_tag
                   else "N/A")

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
        cause_of_death_tag.next_sibling.strip()
        if cause_of_death_tag
        else "N/A"
    )

    risk_factors = []

    risk_factors_elements = soup.find_all(string=lambda text: "Risk Factors:"
                                          in text)
    risk_factors_label = (risk_factors_elements[0]
                          if risk_factors_elements
                          else None)

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


def scrape_website(base_url):
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

    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to retrieve the main page")
        return data

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all links that contain '/people/' in their href attribute
    for link in soup.find_all("a", href=True):
        if "/people/" in link["href"]:
            link_url = link["href"]
            if not link_url.startswith("http"):
                link_url = base_url + link_url  # Adjust for relative URLs

            print(link_url)

            linked_page_response = requests.get(link_url)
            if linked_page_response.status_code == 200:
                linked_page_soup = BeautifulSoup(
                    linked_page_response.content, "html.parser"
                )
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
            else:
                print(f"Failed to retrieve {link_url}")

    return data


urls = {
    "a": "http://www.nndb.com/lists/493/000063304/",
    "b": "http://www.nndb.com/lists/494/000063305/",
    "c": "http://www.nndb.com/lists/495/000063306/",
    "d": "http://www.nndb.com/lists/496/000063307/",
    "e": "http://www.nndb.com/lists/497/000063308/",
    "f": "http://www.nndb.com/lists/498/000063309/",
    "g": "http://www.nndb.com/lists/499/000063310/",
    "h": "http://www.nndb.com/lists/500/000063311/",
    "i": "http://www.nndb.com/lists/501/000063312/",
    "j": "http://www.nndb.com/lists/502/000063313/",
    "k": "http://www.nndb.com/lists/503/000063314/",
    "l": "http://www.nndb.com/lists/504/000063315/",
    "m": "http://www.nndb.com/lists/505/000063316/",
    "n": "http://www.nndb.com/lists/506/000063317/",
    "o": "http://www.nndb.com/lists/507/000063318/",
    "p": "http://www.nndb.com/lists/508/000063319/",
    "q": "http://www.nndb.com/lists/509/000063320/",
    "r": "http://www.nndb.com/lists/510/000063321/",
    "s": "http://www.nndb.com/lists/511/000063322/",
    "t": "http://www.nndb.com/lists/512/000063323/",
    "u": "http://www.nndb.com/lists/513/000063324/",
    "v": "http://www.nndb.com/lists/514/000063325/",
    "w": "http://www.nndb.com/lists/515/000063326/",
    "x": "http://www.nndb.com/lists/516/000063327/",
    "y": "http://www.nndb.com/lists/517/000063328/",
    "z": "http://www.nndb.com/lists/518/000063329/",
}

for key, value in urls.items():
    scraped_data = scrape_website(value)
    csv_file_name = "scraped_data_" + key + ".csv"
    scraped_data.to_csv(csv_file_name, index=False)
    print(f"Data saved to {csv_file_name}")
