import gspread
from google.oauth2.service_account import Credentials
scopes=[
    "https://www.googleapis.com/auth/spreadsheets"
]
creds=Credentials.from_service_account_file("credentials.json",scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "11JY8BsLhBKZnGA5C5v05DYMoC3e-tiQou8rYsHYLDbc"
sheet = client.open_by_key(sheet_id)
values_list = sheet.sheet1.row_values(1)
print(values_list)
values_list = sheet.sheet1.row_values(2)
print(values_list)