import numpy as np
import pandas as pd
import gspread
# from google.auth import default
# from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials
# import google_auth_oauthlib

SCOPE = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(r'/etc/secrets/credentials.json', scopes=SCOPE)

# # creds, _ = default()
gc = gspread.authorize(creds)

lgas = {
    "Esan North-East": "esan-north-east",
    "Ovia South-West": "ovia-south-west",
    "Ovia North-East": "ovia-north-east",
    "Oredo": "oredo",
    "Ikpoba Okha": "ikpoba-okha",
    "Orhionmwon": "orhionmwon",
    "Uhunmwonde": "uhunmwonde",
    "Owan West": "owan-west",
    "Owan East": "owan-east",
    "Akoko Edo": "akoko-edo",
    "Etsako East": "etsako-east",
    "Etsako Central": "etsako-central",
    "Etsako West": "etsako-west",
    "Esan Central": "esan-central",
    "Esan South-East": "esan-south-east",
    "Igueben": "igueben",
    "Esan West": "esan-west",
    "Egor": "egor",
}

filters = [
    {
        "column": "Who Were the Victims?",
        "title": "Categories of Victims",
        "key": "victims",
        "values": [
            "INEC Official",
            "Security Agent",
            "Party Member",
            "Party Agent",
            "Voter",
            "Observer"
        ]
    },
    {
        "column": "Who Did the Violence? (Perpetrator)",
        "title": "Categories of Perpetrators",
        "key": "perpetrators",
        "values": [
            "Security Agent",
            "Party Member",
            "Party Agent",
            "Party Thugs",
            "Voter"
        ]
    },
    {
        "column": "Type of Violence",
        "title": "Types of Violence",
        "key": "violence_types",
        "values": [
            "Murder",
            "Attempted Murder",
            "Physical Harm/Torture",
            "Intimidation/Harassment",
            "Kidnapping",
            "Group Clash",
            "Political Motivated Arrest or Detention",
            "BVAS / Ballot Box Snatching and Destruction",
            "Sporadic Gunshot"
        ]
    }
]

def getViolenceData():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1r0sIvIpJBuDiIs-Eu5nOZ4S-Kh5R6i0srRwSHAjNXzQ/edit?resourcekey=&gid=643848264#gid=643848264"

    # Load the Google Sheet
    sheet = gc.open_by_url(spreadsheet_url)
    # Select the first worksheet
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_values()

    # Convert to a pandas DataFrame
    import pandas as pd
    df = pd.DataFrame(data[1:], columns=data[0])
    
    outputData = []
    totalReports = 0
    totalMen = 0
    totalWomen = 0
    totalUnidentified = 0
    totalVictims = 0

    for lga in lgas:
        lgaData = {
            "id": lgas[lga],
            "name": lga
        }
        for filter in filters:
            labels = []
            lData = []
            col = filter["column"]
            vals = filter["values"]
            for val in vals:
                filterResult = filterData(df, lga, col, val)
                labels.append(val)
                lData.append(filterResult)
            lgaData[filter["key"]] = {
                "title": filter["title"],
                "labels": labels,
                "data": lData
            }
        totals = getTotalsData(df, lga)
        lgaData["totalVictims"] = totals["totalVictims"]
        lgaData["totalReports"] = totals["totalLgaReports"]
        totalMen = totals["totalMen"]
        totalWomen = totals["totalWomen"]
        totalUnidentified = totals["totalUnidentified"]

        # aggregate data
        totalMen += totals["totalMen"]
        totalVictims += totals["totalVictims"]
        totalWomen += totals["totalWomen"]
        totalUnidentified += totals["totalUnidentified"]
        totalReports += totals["totalLgaReports"]
        outputData.append(lgaData)
    return {
        "totalReports": totalReports,
        "totalMen": totalMen,
        "totalWomen": totalWomen,
        "totalVictims": totalVictims,
        "totalUnidentified": totalUnidentified,
        "lgaData": outputData
    }

def filterData(df, lga, column, value):
    numRows = len(df['State'])
    count = 0
    for i in range(0, numRows):
        if(df["Local Government (Edo)"][i] == lga and df["Types of Report"][i] == "Violence Report" and df[column][i] == value):
            count += 1
    return count

def getTotalsData(df, lga):
    numRows = len(df["State"])
    totals = {
        "totalLgaReports": 0,
        "totalVictims": 0,
        "totalMen": 0,
        "totalWomen": 0,
        "totalUnidentified": 0
    }
    for i in range(0, numRows):
        if(df["Types of Report"][i] != "Violence Report"): continue
        if(df["Local Government (Edo)"][i] == lga):
            c = df["How many Persons? (Victims)"][i]
            try:
                totals["totalVictims"] += int(c) if c != '' else 0
            except:
                totals["totalVictims"] += 0
            totals["totalLgaReports"] += 1
    return totals