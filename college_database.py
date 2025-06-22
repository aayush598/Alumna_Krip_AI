def get_college_database():
    return [
        # Premier Engineering Institutes
        {"name": "IIT Bombay", "type": "Engineering", "location": "Mumbai", "fees": 800000, "min_rank": 100, "streams": ["Engineering", "Technology"], "acceptance": "Very Low"},
        {"name": "IIT Delhi", "type": "Engineering", "location": "Delhi", "fees": 750000, "min_rank": 150, "streams": ["Engineering", "Computer Science"], "acceptance": "Very Low"},
        {"name": "IIT Madras", "type": "Engineering", "location": "Chennai", "fees": 800000, "min_rank": 120, "streams": ["Engineering", "Technology"], "acceptance": "Very Low"},

        # Private Engineering
        {"name": "BITS Pilani", "type": "Engineering", "location": "Rajasthan", "fees": 1200000, "min_rank": 5000, "streams": ["Engineering", "Pharmacy", "Science"], "acceptance": "Low"},
        {"name": "VIT Vellore", "type": "Engineering", "location": "Tamil Nadu", "fees": 900000, "min_rank": 15000, "streams": ["Engineering", "Bio-Technology"], "acceptance": "Moderate"},
        {"name": "Manipal Institute of Technology", "type": "Engineering", "location": "Karnataka", "fees": 1500000, "min_rank": 20000, "streams": ["Engineering", "Medicine"], "acceptance": "Moderate"},

        # NITs
        {"name": "NIT Trichy", "type": "Engineering", "location": "Tamil Nadu", "fees": 500000, "min_rank": 3000, "streams": ["Engineering"], "acceptance": "Low"},
        {"name": "NIT Surathkal", "type": "Engineering", "location": "Karnataka", "fees": 480000, "min_rank": 3500, "streams": ["Engineering"], "acceptance": "Low"},

        # Medical Colleges
        {"name": "AIIMS Delhi", "type": "Medical", "location": "Delhi", "fees": 600000, "min_rank": 50, "streams": ["Medicine", "Nursing"], "acceptance": "Very Low"},
        {"name": "JIPMER Puducherry", "type": "Medical", "location": "Puducherry", "fees": 500000, "min_rank": 100, "streams": ["Medicine"], "acceptance": "Very Low"},

        # Universities
        {"name": "Delhi University", "type": "University", "location": "Delhi", "fees": 200000, "min_rank": None, "streams": ["Arts", "Commerce", "Science"], "acceptance": "Moderate"},
        {"name": "Jawaharlal Nehru University", "type": "University", "location": "Delhi", "fees": 300000, "min_rank": None, "streams": ["Arts", "Social Sciences"], "acceptance": "Low"},

        # Business Schools
        {"name": "IIM Ahmedabad", "type": "Management", "location": "Gujarat", "fees": 2300000, "min_rank": 99, "streams": ["MBA", "Management"], "acceptance": "Very Low"},
        {"name": "IIM Bangalore", "type": "Management", "location": "Bangalore", "fees": 2400000, "min_rank": 98, "streams": ["MBA", "Management"], "acceptance": "Very Low"},

        # Regional Options
        {"name": "Tula's Institute", "type": "Engineering", "location": "Dehradun", "fees": 600000, "min_rank": 50000, "streams": ["BCA", "MCA", "BBA", "MBA"], "acceptance": "High"},
        {"name": "Graphic Era University", "type": "University", "location": "Dehradun", "fees": 700000, "min_rank": 40000, "streams": ["Engineering", "Management"], "acceptance": "Moderate"},
    ]
