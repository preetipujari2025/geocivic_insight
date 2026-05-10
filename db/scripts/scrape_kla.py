#!/usr/bin/env python
"""
Karnataka Legislative Assembly MLA Scraper

In production this would scrape:
https://www.kla.kar.nic.in/members
but for now we use sample data to populate the database with realistic Karnataka MLA information.
"""

import os
import sys
import django

# Add the project directory to Python path for Windows compatibility
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
django.setup()

import requests
import json
import time
from db.models import MLA, Constituency

# Sample MLA data for Karnataka constituencies
SAMPLE_MLAS = [
    {
        'constituency_name': 'Mahadevapura',
        'name': 'C. N. Manjunath',
        'party': 'BJP',
        'education': 'MBBS, MD (Cardiology)',
        'term_start': 2023,
        'achievements_raw': 'Developed state-of-the-art healthcare facilities in the constituency with new primary health centers. Initiated major road infrastructure projects connecting Whitefield to Outer Ring Road. Established three new government schools with modern facilities and digital classrooms. Implemented comprehensive drainage system to address water logging issues during monsoons.'
    },
    {
        'constituency_name': 'Shivajinagar',
        'name': 'Rizwan Arshad',
        'party': 'INC',
        'education': 'LLB',
        'term_start': 2023,
        'achievements_raw': 'Launched women empowerment programs providing skill training to over 500 women. Developed heritage tourism circuit preserving historical monuments in the area. Constructed modern multi-level parking to address traffic congestion. Upgraded government hospitals with new equipment and emergency services.'
    },
    {
        'constituency_name': 'Yelahanka',
        'name': 'S. R. Vishwanath',
        'party': 'BJP',
        'education': 'B.Com',
        'term_start': 2023,
        'achievements_raw': 'Implemented comprehensive water supply scheme covering all residential areas. Developed five new parks with walking tracks and children\'s play areas. Constructed new flyovers to reduce traffic congestion at major junctions. Established vocational training centers for youth employment.'
    },
    {
        'constituency_name': 'Chickpet',
        'name': 'Umesh Jadhav',
        'party': 'BJP',
        'education': 'B.Sc',
        'term_start': 2023,
        'achievements_raw': 'Revitalized traditional market areas with modern infrastructure while preserving cultural heritage. Implemented smart city initiatives including WiFi zones and digital information kiosks. Developed storm water drainage system to prevent flooding. Created dedicated lanes for street vendors with proper facilities.'
    },
    {
        'constituency_name': 'Basavanagudi',
        'name': 'K. Chandrashekar',
        'party': 'JD(S)',
        'education': 'M.A.',
        'term_start': 2023,
        'achievements_raw': 'Restored and maintained the historic Bull Temple area with improved tourist facilities. Established senior citizen centers with healthcare and recreational activities. Developed educational infrastructure with new government schools and libraries. Implemented solar street lighting across the constituency.'
    },
    {
        'constituency_name': 'Hebbal',
        'name': 'K. G. Bopaiah',
        'party': 'BJP',
        'education': 'LLB',
        'term_start': 2023,
        'achievements_raw': 'Completed major road widening projects connecting to Bangalore International Airport. Established new industrial zones promoting local employment. Developed healthcare facilities with specialized maternity and child care units. Implemented rainwater harvesting systems in public buildings.'
    },
    {
        'constituency_name': 'Rajajinagar',
        'name': 'Dinesh Gundu Rao',
        'party': 'INC',
        'education': 'B.Com',
        'term_start': 2023,
        'achievements_raw': 'Launched comprehensive solid waste management program with door-to-door collection. Developed sports complexes with facilities for cricket, football, and athletics. Established women\'s self-help groups promoting entrepreneurship. Upgraded public transportation with new bus shelters and routes.'
    },
    {
        'constituency_name': 'Padmanabhanagar',
        'name': 'R. Ashoka',
        'party': 'BJP',
        'education': 'B.Sc',
        'term_start': 2023,
        'achievements_raw': 'Implemented advanced traffic management system with synchronized signals. Developed educational institutions with focus on science and technology. Created green belts and tree plantation drives improving air quality. Established emergency response centers with ambulance services.'
    },
    {
        'constituency_name': 'Vijayapura',
        'name': 'B. C. Patil',
        'party': 'BJP',
        'education': 'B.Sc',
        'term_start': 2023,
        'achievements_raw': 'Irrigation projects providing water to 5000+ acres of agricultural land. Established agricultural research center helping farmers with modern techniques. Developed rural healthcare network with mobile medical units. Constructed rural roads connecting villages to main markets.'
    },
    {
        'constituency_name': 'Hubli-Dharwad-Central',
        'name': 'Arvind Bellad',
        'party': 'BJP',
        'education': 'B.E., MBA',
        'term_start': 2023,
        'achievements_raw': 'Technology hub development with IT parks and startup incubation centers. Implemented smart city solutions including digital governance platforms. Developed educational institutions with engineering and management courses. Created comprehensive public transport system with bus rapid transit.'
    }
]

def load_sample_mlas():
    """
    Load sample MLA data into the database.
    Only creates MLAs for constituencies that already exist in the database.
    """
    print("Loading sample MLA data...")
    loaded_count = 0
    skipped_count = 0
    
    for entry in SAMPLE_MLAS:
        try:
            constituency = Constituency.objects.get(name=entry['constituency_name'])
        except Constituency.DoesNotExist:
            print(f"Skipping {entry['name']} - constituency '{entry['constituency_name']}' not in DB")
            skipped_count += 1
            continue
        
        # Update or create MLA record
        mla, created = MLA.objects.update_or_create(
            constituency=constituency,
            name=entry['name'],
            defaults={
                'party': entry['party'],
                'education': entry['education'],
                'term_start': entry['term_start'],
                'achievements_raw': entry['achievements_raw']
            }
        )
        
        if created:
            print(f"Created MLA: {entry['name']} ({entry['party']})")
        else:
            print(f"Updated MLA: {entry['name']} ({entry['party']})")
        
        loaded_count += 1
    
    print(f"\nSummary:")
    print(f"  MLAs loaded/updated: {loaded_count}")
    print(f"  MLAs skipped: {skipped_count}")
    print(f"  Total MLAs in database: {MLA.objects.count()}")

if __name__ == '__main__':
    load_sample_mlas()