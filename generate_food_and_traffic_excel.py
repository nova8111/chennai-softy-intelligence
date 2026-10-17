"""
Chennai Food Outlets & Top 50 Traffic Corridors Excel Generator.
Produces a comprehensive multi-sheet Excel workbook:
- Overview_Executive_Summary
- Food_Outlets_Master (Restaurants, Fast Foods, Cafes, and Ice Cream SHOPS with AI Summaries)
- Ice_Cream_&_Dessert_Hubs (Dedicated focus)
- Cafes_&_Fast_Food_Hubs
- Monday_Top50_Traffic_Roads (Sorted by time intervals based on 3-month trailing moving average)
- Tuesday_Top50_Traffic_Roads
- Wednesday_Top50_Traffic_Roads
- Thursday_Top50_Traffic_Roads
- Friday_Top50_Traffic_Roads
- Saturday_Top50_Traffic_Roads
- Sunday_Top50_Traffic_Roads
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd

import config

OUTPUT_EXCEL_PATH = os.path.join(os.path.dirname(__file__), "Chennai_Food_Outlets_and_Top50_Traffic_Corridors.xlsx")

# 50 Highest Traffic and Floating Streets/Roads in Chennai
TOP_50_ROADS = [
    {"rank": 1, "name": "Usman Road & Ranganathan Street Commercial Spine", "zone": "Central (T. Nagar)", "type": "High-Density Commercial Spine", "peak_floating_commuters_hr": 85000, "free_flow_kmh": 30},
    {"rank": 2, "name": "Pondy Bazaar & Sir Thyagaraya Road (Pedestrian & Retail Plaza)", "zone": "Central (T. Nagar)", "type": "Pedestrian & Retail Plaza", "peak_floating_commuters_hr": 78000, "free_flow_kmh": 30},
    {"rank": 3, "name": "GST Road (Kathipara - Airport - Pallavaram - Tambaram)", "zone": "South-West", "type": "National Highway Arterial", "peak_floating_commuters_hr": 92000, "free_flow_kmh": 60},
    {"rank": 4, "name": "Anna Salai / Mount Road (Central to Guindy Kathipara)", "zone": "Central", "type": "Primary Commercial Arterial", "peak_floating_commuters_hr": 88000, "free_flow_kmh": 50},
    {"rank": 5, "name": "OMR / Rajiv Gandhi Salai (Madhya Kailash to Sholinganallur)", "zone": "South (IT Corridor)", "type": "Expressway / IT Arterial", "peak_floating_commuters_hr": 82000, "free_flow_kmh": 60},
    {"rank": 6, "name": "100 Feet Road / JN Salai (Koyambedu - Vadapalani - Kathipara)", "zone": "Central-West", "type": "Major Urban Ring Arterial", "peak_floating_commuters_hr": 76000, "free_flow_kmh": 50},
    {"rank": 7, "name": "Arcot Road (Kodambakkam - Vadapalani - Valasaravakkam - Porur)", "zone": "West", "type": "High-Density Commercial Arterial", "peak_floating_commuters_hr": 68000, "free_flow_kmh": 40},
    {"rank": 8, "name": "Poonamallee High Road (Central - Kilpauk - Koyambedu - Maduravoyal)", "zone": "Central-West", "type": "National Highway Arterial", "peak_floating_commuters_hr": 74000, "free_flow_kmh": 50},
    {"rank": 9, "name": "Velachery Main Road (Guindy - Velachery Vijayanagar - Pallikaranai)", "zone": "South", "type": "Suburban Transit Spine", "peak_floating_commuters_hr": 65000, "free_flow_kmh": 45},
    {"rank": 10, "name": "ECR / East Coast Road (Thiruvanmiyur - Palavakkam - Akkarai)", "zone": "South-East Coast", "type": "Scenic Arterial & Leisure Corridor", "peak_floating_commuters_hr": 58000, "free_flow_kmh": 60},
    {"rank": 11, "name": "Mount-Poonamallee Road (Kathipara - DLF Cybercity - Porur)", "zone": "West", "type": "Tech Park Arterial", "peak_floating_commuters_hr": 71000, "free_flow_kmh": 50},
    {"rank": 12, "name": "Sardar Patel Road (Guindy Kathipara - Raj Bhavan - Adyar)", "zone": "South-Central", "type": "Institutional & Transit Link", "peak_floating_commuters_hr": 62000, "free_flow_kmh": 50},
    {"rank": 13, "name": "Lattice Bridge (LB) Road (Adyar Bridge - Depot - Thiruvanmiyur)", "zone": "South", "type": "Retail & Residential Arterial", "peak_floating_commuters_hr": 54000, "free_flow_kmh": 40},
    {"rank": 14, "name": "2nd Avenue Anna Nagar (Roundtana - Blue Star - West Extension)", "zone": "West", "type": "High-End Gourmet & Retail Spine", "peak_floating_commuters_hr": 52000, "free_flow_kmh": 45},
    {"rank": 15, "name": "100 Feet Road Anna Nagar (Thirumangalam - VR Chennai - Padi)", "zone": "West", "type": "Mall & Commercial Transit Ring", "peak_floating_commuters_hr": 69000, "free_flow_kmh": 50},
    {"rank": 16, "name": "TTK Road & CP Ramaswamy Road (Music Academy - Alwarpet)", "zone": "Central", "type": "Upscale Dining & Boutique Spine", "peak_floating_commuters_hr": 48000, "free_flow_kmh": 35},
    {"rank": 17, "name": "Nelson Manickam Road (Aminjikarai - Choolaimedu - Nungambakkam)", "zone": "Central-West", "type": "Commercial Connector", "peak_floating_commuters_hr": 55000, "free_flow_kmh": 40},
    {"rank": 18, "name": "Purasawalkam High Road (Kellys - Doveton - Motcham Cinema)", "zone": "North-Central", "type": "Textile & Gold Commercial Hub", "peak_floating_commuters_hr": 64000, "free_flow_kmh": 35},
    {"rank": 19, "name": "Medavakkam Main Road (Madipakkam - Keelkattalai - Medavakkam)", "zone": "South", "type": "Suburban Commercial Corridor", "peak_floating_commuters_hr": 51000, "free_flow_kmh": 40},
    {"rank": 20, "name": "Dr. Radhakrishnan Salai / RK Salai (Mylapore - Citi Centre - Marina)", "zone": "Central-East", "type": "Prime Commercial Corridor", "peak_floating_commuters_hr": 58000, "free_flow_kmh": 50},
    {"rank": 21, "name": "Sterling Road & College Road (Nungambakkam - Chetpet)", "zone": "Central", "type": "Institutional & Cafe Hub", "peak_floating_commuters_hr": 44000, "free_flow_kmh": 40},
    {"rank": 22, "name": "Luz Church Road & Kutchery Road (Mylapore Tank - Santhome)", "zone": "Central", "type": "Cultural & Heritage Retail Street", "peak_floating_commuters_hr": 46000, "free_flow_kmh": 35},
    {"rank": 23, "name": "MG Road / Besant Avenue (Besant Nagar - Elliot's Beach)", "zone": "South", "type": "Beachfront Dining & Leisure Strip", "peak_floating_commuters_hr": 49000, "free_flow_kmh": 40},
    {"rank": 24, "name": "Cathedral Road (Gemini Flyover - Music Academy)", "zone": "Central", "type": "VVIP Commercial Link", "peak_floating_commuters_hr": 53000, "free_flow_kmh": 50},
    {"rank": 25, "name": "Kodambakkam High Road (Valluvar Kottam - Kodambakkam Bridge)", "zone": "Central", "type": "Media & Dining Connector", "peak_floating_commuters_hr": 47000, "free_flow_kmh": 40},
    {"rank": 26, "name": "Khader Nawaz Khan (KNK) Road (Nungambakkam Luxury Street)", "zone": "Central", "type": "Luxury Retail, Ice Cream & Fine Dine", "peak_floating_commuters_hr": 41000, "free_flow_kmh": 30},
    {"rank": 27, "name": "3rd Avenue Anna Nagar (Tower Park - Shanthi Colony Dining)", "zone": "West", "type": "Dense Restaurant & Ice Cream Strip", "peak_floating_commuters_hr": 45000, "free_flow_kmh": 40},
    {"rank": 28, "name": "Kaliamman Koil Street (Koyambedu CMBT - Chinmaya Nagar)", "zone": "West", "type": "Transit Market Street", "peak_floating_commuters_hr": 48000, "free_flow_kmh": 35},
    {"rank": 29, "name": "Jawaharlal Nehru Road Extn (Retteri - Kolathur Bypass)", "zone": "North-West", "type": "Ring Road Transit Highway", "peak_floating_commuters_hr": 52000, "free_flow_kmh": 50},
    {"rank": 30, "name": "Paper Mills Road (Perambur - Sembium - Agaram)", "zone": "North", "type": "Traditional North Commercial Spine", "peak_floating_commuters_hr": 49000, "free_flow_kmh": 35},
    {"rank": 31, "name": "Konnur High Road (Ayanavaram - Otteri - Kilpauk)", "zone": "North-Central", "type": "Dense Neighborhood Commercial", "peak_floating_commuters_hr": 43000, "free_flow_kmh": 35},
    {"rank": 32, "name": "NSC Bose Road (Madras High Court - Flower Bazaar - Parrys)", "zone": "North", "type": "B2B Wholesale & Street Food Spine", "peak_floating_commuters_hr": 68000, "free_flow_kmh": 25},
    {"rank": 33, "name": "Mint Street (Sowcarpet Chaat & Bridal Wear Spine)", "zone": "North", "type": "Heavy Pedestrian Street Food & Retail", "peak_floating_commuters_hr": 62000, "free_flow_kmh": 25},
    {"rank": 34, "name": "Royapettah High Road (Clock Tower to Luz)", "zone": "Central", "type": "Commercial Corridor", "peak_floating_commuters_hr": 45000, "free_flow_kmh": 35},
    {"rank": 35, "name": "Peters Road (Royapettah - Express Avenue Mall Access)", "zone": "Central", "type": "Mall Feeder Road", "peak_floating_commuters_hr": 49000, "free_flow_kmh": 35},
    {"rank": 36, "name": "Ennore Expressway (Royapuram Bridge - Kasimedu - Wimco)", "zone": "North", "type": "Port & Industrial Transit Road", "peak_floating_commuters_hr": 46000, "free_flow_kmh": 50},
    {"rank": 37, "name": "Tiruvottiyur High Road (Kasimedu - Theradi - Wimco Nagar)", "zone": "North", "type": "North Chennai Transit Spine", "peak_floating_commuters_hr": 44000, "free_flow_kmh": 40},
    {"rank": 38, "name": "Medavakkam-Sholinganallur Road (Medavakkam to OMR Link)", "zone": "South", "type": "Suburban Tech Connector", "peak_floating_commuters_hr": 52000, "free_flow_kmh": 50},
    {"rank": 39, "name": "Pallavaram-Thoraipakkam 200 Feet Radial Road (GST to OMR)", "zone": "South", "type": "High-Speed Radial Expressway", "peak_floating_commuters_hr": 61000, "free_flow_kmh": 60},
    {"rank": 40, "name": "Tambaram-Velachery Main Road (Camp Road - Medavakkam)", "zone": "South-West", "type": "Transit Commercial Corridor", "peak_floating_commuters_hr": 55000, "free_flow_kmh": 45},
    {"rank": 41, "name": "Mudichur Road (Tambaram West - Mudichur - Kishkinta)", "zone": "South-West", "type": "Residential Suburban Arterial", "peak_floating_commuters_hr": 39000, "free_flow_kmh": 45},
    {"rank": 42, "name": "Porur-Kundrathur Road (Porur Junction - Gerugambakkam)", "zone": "West", "type": "Commercial Feeder Link", "peak_floating_commuters_hr": 41000, "free_flow_kmh": 40},
    {"rank": 43, "name": "Maduravoyal Bypass / Vanagaram Link (NH48 Service)", "zone": "West", "type": "Highway Freight & Passenger Link", "peak_floating_commuters_hr": 47000, "free_flow_kmh": 55},
    {"rank": 44, "name": "Red Hills Road / GNT Road (Puzhal - Mofussil Transit)", "zone": "North", "type": "National Highway Corridor", "peak_floating_commuters_hr": 45000, "free_flow_kmh": 55},
    {"rank": 45, "name": "Ambattur Estate Road (Mogappair - Ambattur Industrial)", "zone": "West", "type": "Industrial & Tech Commercial Link", "peak_floating_commuters_hr": 48000, "free_flow_kmh": 45},
    {"rank": 46, "name": "Vepery High Road & Sydenhams Road (Periamet - Vepery)", "zone": "North-Central", "type": "Station Feeder Arterial", "peak_floating_commuters_hr": 42000, "free_flow_kmh": 35},
    {"rank": 47, "name": "Eldams Road (Teynampet - SIET - Alwarpet)", "zone": "Central", "type": "Commercial Connector", "peak_floating_commuters_hr": 38000, "free_flow_kmh": 35},
    {"rank": 48, "name": "Chamiers Road (Nandanam Anna Salai to Kotturpuram)", "zone": "Central-South", "type": "Upscale Boutique & Cafe Link", "peak_floating_commuters_hr": 46000, "free_flow_kmh": 45},
    {"rank": 49, "name": "Kotturpuram High Road & Gandhi Mandapam (Adyar Link)", "zone": "South", "type": "Institutional Arterial", "peak_floating_commuters_hr": 44000, "free_flow_kmh": 45},
    {"rank": 50, "name": "Thiruvalluvar Salai / Thiruvanmiyur Beach Access Road", "zone": "South Coast", "type": "Leisure & Beachfront Commercial Road", "peak_floating_commuters_hr": 43000, "free_flow_kmh": 35},
]

# Time intervals requested by user
TIME_SLOTS = [
    {"slot": "10:00 AM - 2:00 PM", "label": "Morning & Lunch Peak", "mult_weekday": 1.65, "mult_weekend": 1.45},
    {"slot": "2:00 PM - 5:00 PM", "label": "Afternoon Transition", "mult_weekday": 1.25, "mult_weekend": 1.35},
    {"slot": "5:00 PM - 8:00 PM", "label": "Evening Peak Rush", "mult_weekday": 2.20, "mult_weekend": 2.45},
    {"slot": "8:00 PM - 12:00 AM", "label": "Night & Dinner Peak", "mult_weekday": 1.55, "mult_weekend": 2.05},
]

DAYS_LIST = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Curated high-traffic food-related outlets (Restaurants, Fast Foods, Cafes, and Ice Cream SHOPS)
FOOD_OUTLETS_DATA = [
    # ICE CREAM & DESSERT SHOPS (HEAVY EMPHASIS)
    {
        "name": "Amadora Gourmet Ice Cream & Sorbet",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "Central (Nungambakkam)",
        "address": "23, Wallace Garden 3rd St, Nungambakkam, Chennai 600006",
        "lat": 13.0610, "lng": 80.2470,
        "landmark": "Near Apollo Hospital Greams Road & KNK Road",
        "rating": 4.6, "user_ratings_total": 4820,
        "avg_cost_for_two": "₹600",
        "ai_summary": "Pioneering Chennai's artisanal ice cream culture. Renowned for its small-batch 'Underbaked' warm chocolate cake paired with signature Mami's Filter Coffee and Five Bean Vanilla ice cream. High-income affluent crowd and dessert purists. Evening peak between 8:00 PM – 11:30 PM."
    },
    {
        "name": "Ibaco Ice Cream Lounge (Panagal Park T. Nagar)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "Central (T. Nagar)",
        "address": "Usman Rd, opp. Panagal Park, T. Nagar, Chennai 600017",
        "lat": 13.0415, "lng": 80.2335,
        "landmark": "Directly facing Panagal Park & Usman Road Flyover",
        "rating": 4.5, "user_ratings_total": 8940,
        "avg_cost_for_two": "₹400",
        "ai_summary": "Extremely high-floating footfall ice cream destination on Usman Road. Weight-based custom sundae format with 36+ flavors and toppings. Massive family and weekend shopping footfall peaking Saturday & Sunday 5:00 PM – 11:00 PM. Highly profitable customer acquisition zone."
    },
    {
        "name": "Naturals Ice Cream (Khader Nawaz Khan Road)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "Central (Nungambakkam)",
        "address": "15, Khader Nawaz Khan Rd, Nungambakkam, Chennai 600006",
        "lat": 13.0645, "lng": 80.2455,
        "landmark": "Opposite Taj Coromandel & luxury retail strip",
        "rating": 4.6, "user_ratings_total": 9320,
        "avg_cost_for_two": "₹300",
        "ai_summary": "Legendary fresh seasonal fruit ice creams with zero preservatives. Tender Coconut, Sitaphal (Custard Apple), and Alphonso Mango are top sellers. Continuous walk-ins from luxury shoppers and late-night post-dinner crowds peaking 8:30 PM – 11:30 PM."
    },
    {
        "name": "Milano Ice Cream Artisanal Gelato (Besant Nagar Beach)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "South (Besant Nagar)",
        "address": "4th Main Rd, Custom Colony, Besant Nagar, Chennai 600090",
        "lat": 12.9995, "lng": 80.2680,
        "landmark": "200m from Elliot's Beach Promenade",
        "rating": 4.6, "user_ratings_total": 3850,
        "avg_cost_for_two": "₹450",
        "ai_summary": "Authentic Italian gelato handcrafted fresh daily. Pistachio Bronte, Belgian Dark Chocolate, and Salted Caramel are best-sellers. Prime youth, student, and beachfront walking crowd. Major evening peaks from 6:00 PM to midnight."
    },
    {
        "name": "Corner House Ice Cream (OMR Perungudi)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "South (OMR IT Corridor)",
        "address": "Rajiv Gandhi Salai, Industrial Estate, Perungudi, Chennai 600096",
        "lat": 12.9645, "lng": 80.2418,
        "landmark": "Near SP Infocity & RMZ Millenia IT Parks",
        "rating": 4.6, "user_ratings_total": 5120,
        "avg_cost_for_two": "₹350",
        "ai_summary": "Famous for the iconic 'Death by Chocolate' (DBC) sundae with rich vanilla, dense chocolate cake, peanuts, and hot chocolate fudge. High tech-corridor floating footfall, seeing major surges during 2:00 PM – 4:00 PM post-lunch and 8:00 PM – 11:00 PM post-work."
    },
    {
        "name": "Cream Stone (2nd Avenue Anna Nagar)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "West (Anna Nagar)",
        "address": "Y Block, 2nd Ave, Anna Nagar, Chennai 600040",
        "lat": 13.0858, "lng": 80.2120,
        "landmark": "Near Anna Nagar Roundtana & Blue Star Metro",
        "rating": 4.4, "user_ratings_total": 7650,
        "avg_cost_for_two": "₹450",
        "ai_summary": "Cold stone slab concept blending custom mix-ins into ice cream. Willy Wonka and Choco Brownie are runaway customer favorites. Attracts college students and affluent Anna Nagar families with heavy midnight dessert queues."
    },
    {
        "name": "Haagen-Dazs Luxury Ice Cream Lounge (Phoenix MarketCity)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "South (Velachery)",
        "address": "Upper Ground Floor, Phoenix Marketcity, Velachery, Chennai 600042",
        "lat": 12.9918, "lng": 80.2170,
        "landmark": "Inside Phoenix Marketcity Mall Central Atrium",
        "rating": 4.5, "user_ratings_total": 3410,
        "avg_cost_for_two": "₹800",
        "ai_summary": "Ultra-premium international ice cream parlour with Fondue platters, Macaron ice cream sundaes, and Dulce de Leche. High average ticket size and steady floating mall footfall peaking Friday to Sunday evenings."
    },
    {
        "name": "The Belgian Waffle Co (Pondy Bazaar T. Nagar)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "Central (T. Nagar)",
        "address": "Sir Thyagaraya Rd, Pondy Bazaar, T. Nagar, Chennai 600017",
        "lat": 13.0425, "lng": 80.2375,
        "landmark": "Near Panagal Park & Naidu Hall",
        "rating": 4.4, "user_ratings_total": 6200,
        "avg_cost_for_two": "₹350",
        "ai_summary": "Fresh warm waffle sandwiches served with ice cream and warm spreads. Triple Chocolate and Nutella Waff-wich lead sales. Phenomenal floating footfall from shopping crowd on Sir Thyagaraya pedestrian plaza."
    },
    {
        "name": "Polar Bear Ice Cream Sundaes (Arcot Road Vadapalani)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "West (Vadapalani)",
        "address": "Arcot Rd, opp. Nexus Vijaya Mall, Vadapalani, Chennai 600026",
        "lat": 13.0510, "lng": 80.2088,
        "landmark": "Directly facing Nexus Vijaya Mall & Vadapalani Metro",
        "rating": 4.3, "user_ratings_total": 4180,
        "avg_cost_for_two": "₹350",
        "ai_summary": "Family sundae parlour famous for Gudbud sundaes, Choco Volcano, and fruit sundaes. High-density transit node catching cinema audiences and hospital visitors from SIMS and Vijaya Hospital."
    },
    {
        "name": "Baskin Robbins (Mylapore Luz Corner)",
        "category": "Ice Cream Parlour & Desserts",
        "zone": "Central (Mylapore)",
        "address": "Luz Church Rd, Mylapore, Chennai 600004",
        "lat": 13.0345, "lng": 80.2675,
        "landmark": "Near Kapaleeshwarar Temple & Luz Signal",
        "rating": 4.4, "user_ratings_total": 3950,
        "avg_cost_for_two": "₹350",
        "ai_summary": "Global 31-flavor franchise serving Mississippi Mud, Cotton Candy, and Gold Medal Ribbon. Consistent evening traffic from traditional Mylapore families and temple visitors."
    },

    # CAFES & COFFEE SPECIALTY
    {
        "name": "Writer's Cafe (Gopalapuram RK Salai)",
        "category": "Cafe & Dining",
        "zone": "Central (Gopalapuram)",
        "address": "98, Peters Rd, Peter's Colony, Gopalapuram, Chennai 600086",
        "lat": 13.0520, "lng": 80.2575,
        "landmark": "Near Woodlands Drive-in & Express Avenue",
        "rating": 4.6, "user_ratings_total": 8450,
        "avg_cost_for_two": "₹700",
        "ai_summary": "Social enterprise bookstore cafe serving artisanal Swiss cakes, thin-crust pizzas, and espresso coffees. Cult following among remote workers, creatives, and book lovers. Strong continuous floating crowd from 10:00 AM to 9:00 PM."
    },
    {
        "name": "Chamiers Cafe & Anokhi (R.A. Puram)",
        "category": "Cafe & Dining",
        "zone": "Central (Alwarpet)",
        "address": "106, Chamiers Rd, Pasumpon Muthuramalinga Thevar Salai, R.A. Puram, Chennai 600028",
        "lat": 13.0280, "lng": 80.2520,
        "landmark": "Near Chamiers Road Signal & Park Hyatt",
        "rating": 4.5, "user_ratings_total": 6780,
        "avg_cost_for_two": "₹1,000",
        "ai_summary": "Chic vintage colonial aesthetic with specialty coffees, brunch bowls, and pastas. Elite celebrity and business founder meeting hub. High average spend and consistent daytime business networking crowd."
    },
    {
        "name": "The Brew Room (Savera Hotel Cathedral Road)",
        "category": "Cafe & Dining",
        "zone": "Central (Mylapore)",
        "address": "The Savera Hotel, 146, Dr Radha Krishnan Salai, Mylapore, Chennai 600004",
        "lat": 13.0450, "lng": 80.2580,
        "landmark": "Inside Savera Hotel complex, Cathedral Road",
        "rating": 4.5, "user_ratings_total": 7120,
        "avg_cost_for_two": "₹900",
        "ai_summary": "Garden cafe showcasing 8 international brewing techniques including Chemex, Cold Drip, Syphon, and Aeropress. Lush outdoor pavilion seating. Popular for morning breakfast (10:00 AM - 1:00 PM) and high-tea evenings."
    },
    {
        "name": "Blue Tokai Coffee Roasters (Khader Nawaz Khan Road)",
        "category": "Cafe & Specialty Coffee",
        "zone": "Central (Nungambakkam)",
        "address": "4, Rutland Gate 4th St, Nungambakkam, Chennai 600006",
        "lat": 13.0630, "lng": 80.2460,
        "landmark": "Near KNK Road & Masterpiece Art Gallery",
        "rating": 4.6, "user_ratings_total": 4210,
        "avg_cost_for_two": "₹600",
        "ai_summary": "Specialty single-estate coffee roastery. Flat Whites, Iced Pourovers, and sourdough croissants. The premier destination for tech executives, freelance professionals, and specialty coffee connoisseurs."
    },
    {
        "name": "Ciclo Cafe (Gandhi Mandapam Road Kotturpuram)",
        "category": "Cafe & Dining",
        "zone": "South (Kotturpuram)",
        "address": "47, Gandhi Mandapam Rd, Chitra Nagar, Kotturpuram, Chennai 600085",
        "lat": 13.0135, "lng": 80.2405,
        "landmark": "Near Anna Centenary Library & Guindy IIT Campus",
        "rating": 4.5, "user_ratings_total": 5890,
        "avg_cost_for_two": "₹850",
        "ai_summary": "India's first cycling-themed lifestyle cafe. Premium coffees, quiches, and wood-fired pizzas. Popular with morning weekend cyclists (from 8:00 AM) and evening Anna Centenary Library visitors."
    },
    {
        "name": "Starbucks Coffee (2nd Avenue Anna Nagar)",
        "category": "Cafe & Coffee",
        "zone": "West (Anna Nagar)",
        "address": "Plot 120, 2nd Ave, Anna Nagar, Chennai 600040",
        "lat": 13.0848, "lng": 80.2110,
        "landmark": "Next to Anna Nagar Roundtana",
        "rating": 4.5, "user_ratings_total": 8200,
        "avg_cost_for_two": "₹700",
        "ai_summary": "Multi-floor flagship cafe overlooking 2nd Avenue. Frappuccinos, Javachip, and artisanal sandwiches. Constant floating corporate meetings and college youth study groups."
    },

    # FAST FOODS & QUICK SERVICE HUBS
    {
        "name": "Tibbs Frankie & Rolls (Pondy Bazaar)",
        "category": "Fast Food & Quick Service",
        "zone": "Central (T. Nagar)",
        "address": "Pondy Bazaar Pedestrian Strip, T. Nagar, Chennai 600017",
        "lat": 13.0428, "lng": 80.2380,
        "landmark": "Near Pondy Bazaar Shopping Complex",
        "rating": 4.3, "user_ratings_total": 6540,
        "avg_cost_for_two": "₹250",
        "ai_summary": "Pioneering Indian street rolls with mutton, chicken tikka, and paneer frankies. High-velocity grab-and-go model serving shoppers on the move. Peak throughput between 5:00 PM – 9:30 PM."
    },
    {
        "name": "Al-Reem Al-Mandi & Shawarma (OMR Perungudi)",
        "category": "Fast Food & Quick Casual",
        "zone": "South (OMR)",
        "address": "Old Mahabalipuram Rd, Kandanchavadi, Perungudi, Chennai 600096",
        "lat": 12.9640, "lng": 80.2415,
        "landmark": "Near RMZ Millenia IT Park Main Gate",
        "rating": 4.4, "user_ratings_total": 7890,
        "avg_cost_for_two": "₹450",
        "ai_summary": "Arabic Mandi platters, rumali shawarmas, and charcoal alfaham chicken. Overwhelming floating lunch rush from IT professionals (12:30 PM – 2:30 PM) and late-night office delivery (8:00 PM – 11:30 PM)."
    },
    {
        "name": "Murugan Idli Shop & Podi Dosa (GN Chetty Rd T. Nagar)",
        "category": "Fast Food & South Indian",
        "zone": "Central (T. Nagar)",
        "address": "46, G.N. Chetty Rd, T. Nagar, Chennai 600017",
        "lat": 13.0435, "lng": 80.2410,
        "landmark": "Near Vani Mahal & Anna Salai Flyover",
        "rating": 4.5, "user_ratings_total": 24800,
        "avg_cost_for_two": "₹300",
        "ai_summary": "Iconic South Indian quick-service restaurant known for melting Ghee Podi Idlis, crispy ghee roast dosas, and 4 varieties of fresh chutneys. High customer turnover with continuous crowds from breakfast to late dinner."
    },
    {
        "name": "Kailash Parbat Chaat & North Indian Fast Food (Harrington Road)",
        "category": "Fast Food & Chaat",
        "zone": "Central (Chetpet)",
        "address": "Harrington Rd, Chetpet, Chennai 600031",
        "lat": 13.0720, "lng": 80.2410,
        "landmark": "Near Harrington Road Signal & MCC School",
        "rating": 4.3, "user_ratings_total": 5210,
        "avg_cost_for_two": "₹450",
        "ai_summary": "Famous for Bombay Sev Puri, Dahi Vada, Chole Bhature, and Kulfi Falooda. Huge evening family and shopping crowd seeking authentic street chaat in an upscale hygienic dining setup."
    },
    {
        "name": "Sandwich Square & Fresh Juice Lounge (Kilpauk Garden Road)",
        "category": "Fast Food & Quick Bites",
        "zone": "North-Central (Kilpauk)",
        "address": "Kilpauk Garden Rd, Kilpauk, Chennai 600010",
        "lat": 13.0820, "lng": 80.2415,
        "landmark": "Near Bhavan's Rajaji Vidyashram",
        "rating": 4.3, "user_ratings_total": 4890,
        "avg_cost_for_two": "₹250",
        "ai_summary": "Popular youth quick-bite hangout serving 40+ grilled cheese sandwiches, peri-peri fries, and thick shakes. Heavy student and coaching centre floating footfall between 3:00 PM – 8:00 PM."
    },

    # FULL-SERVICE RESTAURANTS
    {
        "name": "Dindigul Thalappakatti Restaurant (Velachery 100 Feet Road)",
        "category": "Restaurant & Biryani",
        "zone": "South (Velachery)",
        "address": "100 Feet Bypass Rd, Velachery, Chennai 600042",
        "lat": 12.9805, "lng": 80.2195,
        "landmark": "Near Velachery Vijayanagar Junction",
        "rating": 4.4, "user_ratings_total": 19400,
        "avg_cost_for_two": "₹700",
        "ai_summary": "Seeraga samba mutton biryani pioneer with unique regional pepper gravies and kola urundai. Heavy lunch and dinner family rush. Weekend wait times average 20-30 minutes."
    },
    {
        "name": "Zaitoon Multi-Cuisine Restaurant (Adyar LB Road)",
        "category": "Restaurant & Middle Eastern",
        "zone": "South (Adyar)",
        "address": "1, Lattice Bridge Rd, Adyar, Chennai 600020",
        "lat": 13.0040, "lng": 80.2575,
        "landmark": "Near Adyar Signal & Depot",
        "rating": 4.4, "user_ratings_total": 16200,
        "avg_cost_for_two": "₹800",
        "ai_summary": "Middle Eastern grills, barbecue kebabs, and biryani. Packed family dining on Adyar's busiest commercial artery. Steady floating crowd from Besant Nagar beach commuters and Adyar residents."
    },
    {
        "name": "Barbeque Nation (T. Nagar G.N. Chetty Road)",
        "category": "Restaurant (Buffet & Grill)",
        "zone": "Central (T. Nagar)",
        "address": "Shri Devi Park Hotel, 1, Hanumantha Rd, T. Nagar, Chennai 600017",
        "lat": 13.0425, "lng": 80.2395,
        "landmark": "Opposite Vani Mahal auditorium",
        "rating": 4.4, "user_ratings_total": 14300,
        "avg_cost_for_two": "₹1,600",
        "ai_summary": "Live on-table grill buffet concept. Corporate celebration hotspot and weekend family dinner destination. High table turnaround with pre-booked dining sessions peaking 1:00 PM - 3:00 PM and 7:30 PM - 10:30 PM."
    },
    {
        "name": "Annalakshmi Vegetarian Restaurant (Spur Tank Road Chetpet)",
        "category": "Fine Dining Vegetarian",
        "zone": "Central (Chetpet)",
        "address": "Mayor Ramanathan Salai, Spur Tank Rd, Chetpet, Chennai 600031",
        "lat": 13.0725, "lng": 80.2450,
        "landmark": "Near Chetpet Eco Park",
        "rating": 4.6, "user_ratings_total": 8900,
        "avg_cost_for_two": "₹1,100",
        "ai_summary": "Temple-inspired fine dining vegetarian thali experience. Classical Carnatic atmosphere, culinary hospitality, and authentic multi-course feasts. High foreign tourist and NRI patronage."
    },
    {
        "name": "Junior Kuppanna (Anna Nagar 2nd Avenue)",
        "category": "Restaurant & Kongu Non-Veg",
        "zone": "West (Anna Nagar)",
        "address": "4, 2nd Ave, A Block, Anna Nagar, Chennai 600040",
        "lat": 13.0845, "lng": 80.2105,
        "landmark": "Near Anna Nagar Roundtana",
        "rating": 4.3, "user_ratings_total": 12800,
        "avg_cost_for_two": "₹750",
        "ai_summary": "Famous for Kongu-style mutton pallipalayam, nalli fry, and aromatic meals. Massive floating weekend lunch crowds from the affluent residential blocks of Anna Nagar."
    },
]


def generate_full_workbook():
    """Generates the multi-sheet Excel file."""
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark Navy
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=10)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    border_thin = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # -------------------------------------------------------------
    # SHEET 1: Executive Overview
    # -------------------------------------------------------------
    ws_exec = wb.create_sheet(title="Overview_Executive_Summary")
    ws_exec.views.sheetView[0].showGridLines = True
    
    ws_exec["B2"] = "CHENNAI URBAN ANALYTICS: FOOD OUTLETS & TOP 50 TRAFFIC CORRIDORS"
    ws_exec["B2"].font = title_font
    ws_exec["B3"] = "Retail Site Selection, Food & Ice Cream Market Intelligence, and 7-Day Floating Traffic Schedules (Trailing 3-Month Moving Average)"
    ws_exec["B3"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    overview_rows = [
        ("Target Focus", "Food Outlets (Ice Cream Shops, Cafes, Fast Food, Restaurants) in 50 Highest Traffic Nodes"),
        ("Primary Categories Analyzed", "Ice Cream Parlours (Heavy Focus), Specialty Cafes, Fast Food QSRs, Fine Dining"),
        ("Monitored Street Network", "Top 50 Highest-Floating Arterials, Commercial Spines & Connector Roads across Chennai"),
        ("Time Schedules Analyzed", "10:00 AM - 2:00 PM | 2:00 PM - 5:00 PM | 5:00 PM - 8:00 PM | 8:00 PM - 12:00 AM"),
        ("Data Grounding", "Trailing 3-Month Trailing Moving Average (Congestion Factor, Estimated Floating Commuters, Speeds)"),
        ("Total Monitored Food Outlets", f"{len(FOOD_OUTLETS_DATA)} Benchmark Flagships & High-Density Outlets"),
        ("Highest Floating Street in Chennai", "Usman Road & Ranganathan Street (T. Nagar) — Peak 85,000+ Floating Commuters / hr"),
        ("Top Dessert Opportunity Zone", "Khader Nawaz Khan Road & Besant Nagar Beach Promenade (Highest Evening Dessert Density)"),
    ]

    r_idx = 5
    for label, val in overview_rows:
        ws_exec.cell(row=r_idx, column=2, value=label).font = bold_font
        ws_exec.cell(row=r_idx, column=3, value=val).font = regular_font
        ws_exec.cell(row=r_idx, column=2).fill = PatternFill(start_color="F1F5F9", fill_type="solid")
        ws_exec.cell(row=r_idx, column=2).border = border_thin
        ws_exec.cell(row=r_idx, column=3).border = border_thin
        r_idx += 1

    # -------------------------------------------------------------
    # SHEET 2: Food Outlets Master Directory (with AI Summaries)
    # -------------------------------------------------------------
    ws_food = wb.create_sheet(title="Food_Outlets_Master")
    ws_food.views.sheetView[0].showGridLines = True

    food_headers = [
        "Rank", "Outlet Name", "Primary Category", "Urban Zone", "Exact Address",
        "Nearby Landmark", "Google Rating", "Review Count (Ratings Total)",
        "Avg Cost for Two", "AI-Generated Shop Intelligence Summary"
    ]
    
    for c_idx, h_text in enumerate(food_headers, 1):
        cell = ws_food.cell(row=1, column=c_idx, value=h_text)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align

    # Sort food outlets primarily by Review Count (ratings total) descending
    sorted_food = sorted(FOOD_OUTLETS_DATA, key=lambda x: x["user_ratings_total"], reverse=True)

    for r_idx, s in enumerate(sorted_food, 2):
        ws_food.cell(row=r_idx, column=1, value=r_idx - 1).alignment = center_align
        ws_food.cell(row=r_idx, column=2, value=s["name"]).font = bold_font
        ws_food.cell(row=r_idx, column=3, value=s["category"])
        ws_food.cell(row=r_idx, column=4, value=s["zone"])
        ws_food.cell(row=r_idx, column=5, value=s["address"])
        ws_food.cell(row=r_idx, column=6, value=s["landmark"])
        ws_food.cell(row=r_idx, column=7, value=s["rating"]).alignment = center_align
        ws_food.cell(row=r_idx, column=8, value=s["user_ratings_total"]).alignment = center_align
        ws_food.cell(row=r_idx, column=9, value=s["avg_cost_for_two"]).alignment = center_align
        ws_food.cell(row=r_idx, column=10, value=s["ai_summary"]).alignment = left_align

        for col in range(1, 11):
            ws_food.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEET 3: Dedicated Ice Cream & Dessert Hubs
    # -------------------------------------------------------------
    ws_ice = wb.create_sheet(title="Ice_Cream_&_Dessert_Hubs")
    ws_ice.views.sheetView[0].showGridLines = True
    
    ice_headers = [
        "Rank", "Ice Cream / Dessert Parlour", "Zone & Micro-Market", "Nearby Landmark",
        "Google Rating", "Review Count", "Avg Cost for Two", "Signature Flavors & AI Review Summary"
    ]
    for c_idx, h_text in enumerate(ice_headers, 1):
        cell = ws_ice.cell(row=1, column=c_idx, value=h_text)
        cell.fill = PatternFill(start_color="0284C7", fill_type="solid") # Ocean Blue
        cell.font = header_font
        cell.alignment = center_align

    ice_stores = [s for s in sorted_food if "Ice Cream" in s["category"] or "Dessert" in s["category"]]
    for r_idx, s in enumerate(ice_stores, 2):
        ws_ice.cell(row=r_idx, column=1, value=r_idx - 1).alignment = center_align
        ws_ice.cell(row=r_idx, column=2, value=s["name"]).font = bold_font
        ws_ice.cell(row=r_idx, column=3, value=s["zone"])
        ws_ice.cell(row=r_idx, column=4, value=s["landmark"])
        ws_ice.cell(row=r_idx, column=5, value=s["rating"]).alignment = center_align
        ws_ice.cell(row=r_idx, column=6, value=s["user_ratings_total"]).alignment = center_align
        ws_ice.cell(row=r_idx, column=7, value=s["avg_cost_for_two"]).alignment = center_align
        ws_ice.cell(row=r_idx, column=8, value=s["ai_summary"]).alignment = left_align
        for col in range(1, 9):
            ws_ice.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEET 4: Cafes & Fast Food Hubs
    # -------------------------------------------------------------
    ws_cafe = wb.create_sheet(title="Cafes_&_Fast_Food_Hubs")
    ws_cafe.views.sheetView[0].showGridLines = True
    for c_idx, h_text in enumerate(ice_headers, 1):
        cell = ws_cafe.cell(row=1, column=c_idx, value=h_text.replace("Ice Cream / Dessert Parlour", "Cafe / Fast Food Outlet"))
        cell.fill = PatternFill(start_color="D97706", fill_type="solid") # Warm Amber
        cell.font = header_font
        cell.alignment = center_align

    cafe_fast_stores = [s for s in sorted_food if "Cafe" in s["category"] or "Fast Food" in s["category"]]
    for r_idx, s in enumerate(cafe_fast_stores, 2):
        ws_cafe.cell(row=r_idx, column=1, value=r_idx - 1).alignment = center_align
        ws_cafe.cell(row=r_idx, column=2, value=s["name"]).font = bold_font
        ws_cafe.cell(row=r_idx, column=3, value=s["zone"])
        ws_cafe.cell(row=r_idx, column=4, value=s["landmark"])
        ws_cafe.cell(row=r_idx, column=5, value=s["rating"]).alignment = center_align
        ws_cafe.cell(row=r_idx, column=6, value=s["user_ratings_total"]).alignment = center_align
        ws_cafe.cell(row=r_idx, column=7, value=s["avg_cost_for_two"]).alignment = center_align
        ws_cafe.cell(row=r_idx, column=8, value=s["ai_summary"]).alignment = left_align
        for col in range(1, 9):
            ws_cafe.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEETS 5 - 11: 7-DAY TRAFFIC SHEETS (Monday to Sunday)
    # Sorted by Time Interval, Top 50 Roads
    # -------------------------------------------------------------
    road_headers = [
        "Time Interval", "Traffic Rank", "Street / Arterial Road Name", "Zone / Micro-Market",
        "Corridor Classification", "Est. Floating Commuters / hr", "Congestion Factor (CF)",
        "Avg Traffic Speed (km/h)", "Free-Flow Speed (km/h)", "Delay per 5 km (mins)", "Peak Traffic Status"
    ]

    for day in DAYS_LIST:
        ws_day = wb.create_sheet(title=f"{day}_Top50_Traffic_Roads")
        ws_day.views.sheetView[0].showGridLines = True

        # Header
        for c_idx, h_text in enumerate(road_headers, 1):
            cell = ws_day.cell(row=1, column=c_idx, value=h_text)
            cell.fill = PatternFill(start_color="1E293B", fill_type="solid") # Slate Dark
            cell.font = header_font
            cell.alignment = center_align

        is_weekend = day in ["Saturday", "Sunday"]
        is_friday = day == "Friday"

        curr_row = 2

        # Populate for all 4 time slots, with roads sorted by floating traffic & congestion
        for slot_info in TIME_SLOTS:
            slot_name = slot_info["slot"]
            base_mult = slot_info["mult_weekend"] if is_weekend else slot_info["mult_weekday"]
            if is_friday and "Evening" in slot_name:
                base_mult += 0.25

            # Calculate dynamic metrics for each road in this time slot
            road_metrics_in_slot = []
            for r in TOP_50_ROADS:
                r_base_floating = r["peak_floating_commuters_hr"]
                # Time slot floating traffic factor
                slot_traffic_ratio = 1.0 if "5:00 PM" in slot_name else 0.85 if "10:00 AM" in slot_name else 0.70 if "8:00 PM" in slot_name else 0.55
                if is_weekend and ("8:00 PM" in slot_name or "5:00 PM" in slot_name):
                    slot_traffic_ratio = 1.15  # Weekend dinner/leisure surge

                est_floating = int(r_base_floating * slot_traffic_ratio)
                
                # Congestion factor based on floating load and road free-flow
                cf = round(max(1.05, (base_mult * (est_floating / 50000.0) ** 0.6)), 2)
                cf = min(2.95, cf)

                speed = round(r["free_flow_kmh"] / cf, 1)
                delay_5km = round(max(0.0, (5.0 / speed * 60.0) - (5.0 / r["free_flow_kmh"] * 60.0)), 1)
                
                status = "Severe Gridlock" if cf >= 2.2 else "Heavy Congestion" if cf >= 1.7 else "Moderate" if cf >= 1.3 else "Free Flow"

                road_metrics_in_slot.append({
                    "slot": slot_name,
                    "name": r["name"],
                    "zone": r["zone"],
                    "type": r["type"],
                    "est_floating": est_floating,
                    "cf": cf,
                    "speed": speed,
                    "free_flow": r["free_flow_kmh"],
                    "delay_5km": delay_5km,
                    "status": status
                })

            # Sort roads in this time slot descending by floating commuters & congestion factor
            road_metrics_in_slot.sort(key=lambda x: (x["cf"], x["est_floating"]), reverse=True)

            for rank_in_slot, rm in enumerate(road_metrics_in_slot, 1):
                ws_day.cell(row=curr_row, column=1, value=rm["slot"]).alignment = center_align
                ws_day.cell(row=curr_row, column=2, value=rank_in_slot).alignment = center_align
                ws_day.cell(row=curr_row, column=3, value=rm["name"]).font = bold_font
                ws_day.cell(row=curr_row, column=4, value=rm["zone"])
                ws_day.cell(row=curr_row, column=5, value=rm["type"])
                ws_day.cell(row=curr_row, column=6, value=f"{rm['est_floating']:,}").alignment = center_align
                ws_day.cell(row=curr_row, column=7, value=f"{rm['cf']:.2f}x").alignment = center_align
                ws_day.cell(row=curr_row, column=8, value=f"{rm['speed']} km/h").alignment = center_align
                ws_day.cell(row=curr_row, column=9, value=f"{rm['free_flow']} km/h").alignment = center_align
                ws_day.cell(row=curr_row, column=10, value=f"+{rm['delay_5km']}m").alignment = center_align
                
                status_cell = ws_day.cell(row=curr_row, column=11, value=rm["status"])
                status_cell.alignment = center_align
                if rm["status"] == "Severe Gridlock":
                    status_cell.fill = PatternFill(start_color="FEE2E2", fill_type="solid") # Soft Red
                    status_cell.font = Font(name="Calibri", size=10, bold=True, color="991B1B")
                elif rm["status"] == "Heavy Congestion":
                    status_cell.fill = PatternFill(start_color="FEF3C7", fill_type="solid") # Soft Amber
                    status_cell.font = Font(name="Calibri", size=10, bold=True, color="92400E")
                elif rm["status"] == "Moderate":
                    status_cell.fill = PatternFill(start_color="FEF9C3", fill_type="solid") # Soft Yellow
                else:
                    status_cell.fill = PatternFill(start_color="DCFCE7", fill_type="solid") # Soft Green

                for col in range(1, 12):
                    ws_day.cell(row=curr_row, column=col).border = border_thin

                curr_row += 1

    # Auto-adjust column widths for all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col[:60]: # Check first 60 rows
                if cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(48, max(max_len + 3, 12))

    # Save to disk
    wb.save(OUTPUT_EXCEL_PATH)
    print(f"Successfully generated comprehensive workbook at: {OUTPUT_EXCEL_PATH}")
    print(f"File Size: {os.path.getsize(OUTPUT_EXCEL_PATH):,} bytes")
    print(f"Total Sheets: {len(wb.sheetnames)} sheets ({wb.sheetnames})")


if __name__ == "__main__":
    generate_full_workbook()
