import re

def convert_budget(value):
    """Convert budget strings with lakhs/crores to actual numbers"""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.lower().replace(',', '').replace(' ', '')
        if 'lakh' in value or 'lac' in value:
            num = re.findall(r'\d+\.?\d*', value)
            if num:
                return int(float(num[0]) * 100000)
        elif 'crore' in value:
            num = re.findall(r'\d+\.?\d*', value)
            if num:
                return int(float(num[0]) * 10000000)
        else:
            num = re.findall(r'\d+', value)
            if num:
                return int(num[0])
    return value

def normalize_gender(value):
    """Normalize gender field"""
    if value is None:
        return None
    value = str(value).lower()
    if value in ['male', 'boy', 'm', 'man']:
        return 'Male'
    elif value in ['female', 'girl', 'f', 'woman']:
        return 'Female'
    else:
        return value.title()
