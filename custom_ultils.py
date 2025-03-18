import requests
import json
import html
import re
import asyncio

def get_schedule(date:str, student_ID: str):
    """Get the schedule dictionary of the provided `date`

    Args:
        date (str): Date, in the `ddmmyyyy` format
    """
    formatted_date = f"{date[:2]}/{date[2:4]}/{date[4:]}"
    
    url = "https://calen.lhu.edu.vn/AjaxPage/AjaxPage.aspx/LichSinhVien"
    payload = {
        'StudentID': student_ID,
        'Ngay': formatted_date,
        'RowIndex': '0'
    }

    # For .NET AJAX services, we need to wrap the payload in a dictionary with a data property
    data = json.dumps(payload)

    # Set headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    # Send the POST request
    response = requests.post(url, data=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()
        
        # Access the list of events inside the "d" key and clean the data
        raw_data = result["d"][3]  # The actual data seems to be in the 4th item in the "d" list
        
        # Decode the escaped JSON string
        cleaned_data = json.loads(raw_data)
        
        # Properly unescape HTML entities and handle Unicode correctly
        for item in cleaned_data:
            for key, value in item.items():
                if isinstance(value, str):
                    # Just unescape HTML entities
                    item[key] = html.unescape(value)
                    
        for item in cleaned_data:
            for key, value in item.items():
                if isinstance(value, str):
                    # Remove HTML tags
                    item[key] = re.sub(r"<.*?>", "", value)

        extracted_data = []

        for data in cleaned_data:
            if data["Ngay"] == date:
                temp_data = {
                    "Tên Phòng": data["TenPhong"],
                    "Ngày": data["Ngay"],
                    "Thời Gian": data["ThoiGian"],
                    "Tên Môn Học": data["TenMonHoc"],
                    "Giáo Viên": data["GiaoVien"],
                    "Tên Cơ Sở": data["TenCoSo"],
                    "Tình Trạng": "Nghỉ" if data["TinhTrang"] == 1 else "Học",      
                }
                
                extracted_data.append(temp_data)
        
        if len(extracted_data) == 0:
            return f"No schedule on {date}"
        return extracted_data

        
    else:
        print(f"Failed with status code: {response.status_code}")
        return response.status_code, response.text
