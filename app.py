from flask import Flask, render_template 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_stats(stat_name):
    """Extracts stats based on the <h2> title inside the leaderboard div."""
    
    service = Service(r"C:\webdriver\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.nba.com/stats")

    wait = WebDriverWait(driver, 10)  
    try:
        # Find all leaderboard sections
        sections = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "LeaderBoardCard_lbcWrapper__e4bCZ"))
        )
    except Exception as e:
        print(f"Error: Leaderboard sections did not load within the time limit.")
        driver.quit()
        return []

    target_div = None
    for section in sections:
        try:
            # Get the title inside <h2>
            h2_element = section.find_element(By.TAG_NAME, "h2")
            if h2_element and stat_name.lower() in h2_element.text.lower():
                target_div = section
                break
        except:
            continue  # Skip if no <h2> is found

    if not target_div:
        print(f"Error: Could not find leaderboard for {stat_name}")
        driver.quit()
        return []

    # Extract HTML from the correct section
    html = target_div.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "html.parser")

    # Find the table inside this section
    table = soup.find("table")
    if not table:
        print(f"Error: No table found for {stat_name}")
        driver.quit()
        return []

    rows = table.find_all("tr")  # Skip header row

    stats_list = []
    for row in rows[:5]:  # Get top 5 players
        columns = row.find_all("td")
        if len(columns) < 3:
            continue  # Skip invalid rows
        
        player_name = columns[1].text.strip()
        stat_value = columns[2].text.strip()
        stats_list.append((player_name, stat_value))

    driver.quit()
    return stats_list


@app.route('/')
def index():
    points = get_stats("Points")
    rebounds = get_stats("Rebounds")
    assists = get_stats("Assists")
    steals = get_stats("Steals")
    blocks = get_stats("Blocks")
    turnovers = get_stats("Turnovers")

    return render_template(
        "index.html",
        points=points,
        rebounds=rebounds,
        assists=assists,
        steals=steals,
        blocks=blocks,
        turnovers=turnovers
    )

if __name__ == '__main__':
    app.run(debug=True)

