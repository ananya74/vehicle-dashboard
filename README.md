# <ins> Vehicle Registration Growth Dashboard <ins>

An interactive Streamlit dashboard for analyzing **Year-on-Year (YoY)** and **Quarter-on-Quarter (QoQ)** growth trends in Indian vehicle registrations across manufacturers and vehicle categories. Built for investor-focused insights using data from the Vahan portal.

##  Setup Instructions

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/vehicle-dashboard.git
   cd vehicle-dashboard

2. **Create and Activate Virtual Environment**  
   ```bash
   python -m venv env
   env\Scripts\activate

3. **Install Requirements**  
   ```bash
   pip install -r requirements.txt

4. **Run the Dashboard**  
   ```bash
   streamlit run app.py

## Data Assumptions

**Date Format:** <br/>
YEAR: 4-digit year (e.g., 2023) <br/>
Month: Full month name or 3-letter abbreviation (e.g., Jan, JAN, December)<br/>

**Quarter Mapping is inferred from the month field using:** <br/>
Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec<br/>

**Growth Metrics:**  <br/>
YoY Growth is computed by comparing the same month across years.<br/>
QoQ Growth is computed by comparing consecutive quarters for each manufacturer.<br/>

**Missing or Zero Values:** <br/>
Zero or null values are handled gracefully but may result in NaN growth rates.<br/>

## Example Use Case
**Compare how 3W registrations from Bajaj Auto grew QoQ over 2023, and identify the top 5 fastest growing manufacturers in Q1 2024.**
   
