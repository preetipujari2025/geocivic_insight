"""
Mapping of Karnataka Assembly Constituencies to Lok Sabha (Parliamentary) seats.
Each of the 28 Lok Sabha seats contains 8 Assembly segments (224 total).
Source: Election Commission of India delimitation order.
"""

# Lok Sabha seat -> list of Assembly constituency names
LOKSABHA_TO_ASSEMBLY = {
    "Chikkodi": [
        "Nippani", "Chikkodi-Sadalga", "Athani", "Kagwad",
        "Kudachi (SC)", "Raybag (SC)", "Hukkeri", "Arabhavi",
    ],
    "Belgaum": [
        "Gokak", "Belgaum Uttar", "Belgaum Dakshin", "Belgaum Rural",
        "Bailhongal", "Saundatti Yellamma", "Ramdurg", "Kittur",
    ],
    "Bagalkot": [
        "Badami", "Bagalkot", "Bilgi", "Hungund",
        "Jamkhandi", "Mudhol (SC)", "Terdal", "Basavana Bagevadi",
    ],
    "Bijapur": [
        "Bijapur City", "Babaleshwar", "Devar Hippargi", "Muddebihal",
        "Indi", "Sindgi", "Nagthan (SC)", "Yemkanmardi (ST)",
    ],
    "Gulbarga": [
        "Gulbarga Uttar", "Gulbarga Dakshin", "Gulbarga Rural (SC)", "Afzalpur",
        "Jevargi", "Sedam", "Chincholi (SC)", "Chittapur (SC)",
    ],
    "Raichur": [
        "Raichur", "Raichur Rural (ST)", "Manvi (ST)", "Sindhanur",
        "Gangawati", "Kanakagiri (SC)", "Maski (ST)", "Lingsugur (SC)",
    ],
    "Bidar": [
        "Bidar", "Bidar South", "Bhalki", "Aurad (SC)",
        "Basavakalyan", "Homnabad", "Aland", "Shahapur",
    ],
    "Koppal": [
        "Koppal", "Kushtagi", "Yelburga", "Gangawati",
        "Shirahatti (SC)", "Gadag", "Nargund", "Ron",
    ],
    "Dharwad": [
        "Dharwad", "Hubli-Dharwad-Central", "Hubli-Dharwad-East (SC)", "Hubli-Dharwad- West",
        "Kundgol", "Navalgund", "Kalghatgi", "Hangal",
    ],
    "Haveri": [
        "Haveri (SC)", "Byadgi", "Hirekerur", "Ranibennur",
        "Harihar", "Shiggaon", "Savanur", "Shirhatti",
    ],
    "Uttara Kannada": [
        "Karwar", "Kumta", "Bhatkal", "Sirsi",
        "Yellapur", "Haliyal", "Khanapur", "Kittur",
    ],
    "Davanagere": [
        "Davanagere North", "Davanagere South", "Mayakonda (SC)", "Channagiri",
        "Honnali", "Harapanahalli", "Jagalur (ST)", "Hadagalli (SC)",
    ],
    "Shimoga": [
        "Shimoga", "Shimoga Rural (SC)", "Bhadravati", "Tirthahalli",
        "Shikaripura", "Sorab", "Sagar", "Byndoor",
    ],
    "Udupi Chikmagalur": [
        "Udupi", "Kapu", "Karkal", "Sringeri",
        "Mudigere (SC)", "Chikmagalur", "Kadur", "Tarikere",
    ],
    "Hassan": [
        "Hassan", "Holenarasipur", "Arkalgud", "Belur",
        "Sakleshpur (SC)", "Shravanabelagola", "Arsikere", "Channapatna",
    ],
    "Dakshina Kannada": [
        "Mangalore", "Mangalore City North", "Mangalore City South", "Bantval",
        "Belthangady", "Moodabidri", "Sullia (SC)", "Puttur",
    ],
    "Mandya": [
        "Mandya", "Maddur", "Melukote", "Nagamangala",
        "Krishnarajpet", "Shrirangapattana", "Malavalli (SC)", "Kollegal (SC)",
    ],
    "Mysore": [
        "Krishnaraja", "Chamaraja", "Narasimharaja", "Chamundeshwari",
        "Krishnarajanagara", "Hunsur", "Heggadadevankote (ST)", "Nanjangud (SC)",
    ],
    "Chamarajanagar": [
        "Chamarajanagar", "Gundlupet", "Hanur", "Kollegal (SC)",
        "T.Narasipur (SC)", "Piriyapatna", "Varuna", "Chamrajpet",
    ],
    "Tumkur": [
        "Tumkur City", "Tumkur Rural", "Kunigal", "Gubbi",
        "Tiptur", "Chiknayakanhalli", "Sira", "Madhugiri",
    ],
    "Chitradurga": [
        "Chitradurga", "Hiriyur", "Hosadurga", "Holalkere (SC)",
        "Challakere (ST)", "Molakalmuru (ST)", "Kudligi (ST)", "Hadagalli (SC)",
    ],
    "Bangalore North": [
        "Byatarayanapura", "Yeshvanthapura", "Dasarahalli", "Mahalakshmi Layout",
        "Malleshwaram", "Hebbal", "Pulakeshinagar (SC)", "Sarvagnanagar",
    ],
    "Bangalore Central": [
        "Shanti Nagar", "Gandhi Nagar", "Rajaji Nagar", "Govindraj Nagar",
        "Vijay Nagar", "Chamrajpet", "Chickpet", "Shivajinagar",
    ],
    "Bangalore South": [
        "Basavanagudi", "Padmanaba Nagar", "Jayanagar", "B.T.M Layout",
        "Bommanahalli", "Bangalore South", "C.V. Raman Nagar (SC)", "Mahadevapura",
    ],
    "Bangalore Rural": [
        "Yelahanka", "K.R.Pura", "Hosakote", "Anekal (SC)",
        "Devanahalli (SC)", "Doddaballapur", "Nelamangala (SC)", "Rajarajeshwarinagar",
    ],
    "Chikkballapur": [
        "Chikkaballapur", "Sidlaghatta", "Bagepalli", "Chintamani",
        "Srinivaspur", "Mulbagal (SC)", "Kolar Gold Field (SC)", "Gauribidanur",
    ],
    "Kolar": [
        "Kolar", "Malur", "Bangarpet (SC)", "K.R.Pura",
        "Ramanagaram", "Magadi", "Kanakapura", "Channapatna",
    ],
    "Bellary": [
        "Bellary City", "Bellary (ST)", "Sandur (ST)", "Kampli (ST)",
        "Siruguppa (ST)", "Hadagalli (SC)", "Hagaribommanahalli (SC)", "Kudligi (ST)",
    ],
}

# Reverse mapping: Assembly constituency name -> Lok Sabha seat
ASSEMBLY_TO_LOKSABHA = {}
for ls_seat, assemblies in LOKSABHA_TO_ASSEMBLY.items():
    for ac in assemblies:
        # If an assembly appears in multiple LS seats (edge cases in delimitation),
        # keep the first mapping
        if ac not in ASSEMBLY_TO_LOKSABHA:
            ASSEMBLY_TO_LOKSABHA[ac] = ls_seat


def get_loksabha_seat(assembly_name):
    """Given an assembly constituency name, return the Lok Sabha seat it belongs to."""
    return ASSEMBLY_TO_LOKSABHA.get(assembly_name)
