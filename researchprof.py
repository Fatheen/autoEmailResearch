import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import warnings
import random
import json
import os

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def fetch_uic_page(url):
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.exceptions.SSLError:
        return None

def scrape_professor_details(professor_url):
    html_content = fetch_uic_page(professor_url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        name = soup.find('h2').get_text(strip=True) if soup.find('h2') else "N/A"
        email = soup.find('a', href=lambda x: x and x.startswith('mailto')).get_text(strip=True) if soup.find('a', href=lambda x: x and x.startswith('mailto')) else "N/A"
        department_info = soup.find(string="Department:").next.strip() if soup.find(string="Department:") else "N/A"
        title = soup.find(string="Title:").next.strip() if soup.find(string="Title:") else "N/A"
        office = soup.find(string="Office:").next.strip() if soup.find(string="Office:") else "N/A"
        phone = soup.find(string="Phone:").next.strip() if soup.find(string="Phone:") else "N/A"
        webpage = soup.find(string="Webpage:").find_next('a')['href'] if soup.find(string="Webpage:") else "N/A"
        research_interest = soup.find(string="Research Interest:").find_next("br").next.strip() if soup.find(string="Research Interest:") else "N/A"
        min_time_commitment = soup.find(string="Minimum time commitment in hours per week:").next.strip() if soup.find(string="Minimum time commitment in hours per week:") else "N/A"
        qualifications = soup.find(string="Qualifications of a Student:").find_next("br").next.strip() if soup.find(string="Qualifications of a Student:") else "N/A"

        summary = {
            'Name': name,
            'Email': email,
            'Department': department_info,
            'Title': title,
            'Office': office,
            'Phone': phone,
            'Webpage': webpage,
            'Research Interest': research_interest,
            'Minimum Time Commitment': min_time_commitment,
            'Student Qualifications': qualifications
        }

        return summary
    except AttributeError:
        return None

def scrape_professors(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    professors = []
    for prof_link in soup.find_all('a', href=True):
        profile_link = prof_link['href']
        name = prof_link.get_text(strip=True)
        full_profile_link = urljoin(base_url, profile_link)
        professors.append({
            'name': name,
            'profile_link': full_profile_link
        })
    return professors

def is_stem_field(professor):
    stem_keywords = ['Engineering', 'Bioengineering', 'Computer', 'Mathematics', 'Physics', 'Chemistry', 
                     'Technology', 'Neuroscience', 'Mechanical', 'Civil', 'Electrical', 'Math', 'Stat', 'Statistics']
    department = professor.get('Department', '').lower()
    research_interest = professor.get('Research Interest', '').lower()
    for keyword in stem_keywords:
        if keyword.lower() in department or keyword.lower() in research_interest:
            return True
    return False

def save_professors_to_file(professors, filename="professors_data.json"):
    with open(filename, 'w') as f:
        json.dump(professors, f, indent=4)

def load_professors_from_file(filename="professors_data.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None

if __name__ == '__main__':
    uic_url = 'https://ure.uic.edu/for_students.php'
    filename = 'professors_data.json'
    professors_data = load_professors_from_file(filename)
    
    if not professors_data:
        html_content = fetch_uic_page(uic_url)
        if html_content:
            professors_list = scrape_professors(html_content, base_url=uic_url)
            filtered_stem_professors = []
            for professor in professors_list:
                details = scrape_professor_details(professor['profile_link'])
                if details and is_stem_field(details):
                    filtered_stem_professors.append(details)
            save_professors_to_file(filtered_stem_professors, filename)
            professors_data = filtered_stem_professors

    selected_professors = random.sample(professors_data, min(5, len(professors_data)))
    for professor in selected_professors:
        print(f"Name: {professor['Name']}")
        print(f"Email: {professor['Email']}")
        print(f"Department: {professor['Department']}")
        print(f"Research Interest: {professor['Research Interest']}")
        print("=" * 40)
