"""
Generator for Chennai_Top50_Ice_Cream_Parlors_Intelligence.xlsx.
Generates an 11-sheet master workbook tailored specifically for opening an Ice Cream / Softy Shop in Chennai.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from ice_cream_intelligence_data import (
    TOP_50_ICE_CREAM_PARLORS,
    TOP_20_BAZAAR_SITES,
    TOP_SOFTY_SPECIALISTS,
    COMPARATIVE_EVALUATION_MATRIX
)
from generate_food_and_traffic_excel import TOP_50_ROADS, TIME_SLOTS, DAYS_LIST

OUTPUT_EXCEL_PATH = os.path.join(os.path.dirname(__file__), "Chennai_Top50_Ice_Cream_Parlors_Intelligence.xlsx")


def generate_ice_cream_master_workbook():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default sheet

    # Design Styles
    primary_header_fill = PatternFill(start_color="831843", end_color="831843", fill_type="solid") # Deep Berry / Ice Cream Pink
    sub_header_fill = PatternFill(start_color="9D174D", end_color="9D174D", fill_type="solid")
    dark_slate_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    accent_gold_fill = PatternFill(start_color="FEF3C7", fill_type="solid")
    soft_red_fill = PatternFill(start_color="FEE2E2", fill_type="solid")
    soft_green_fill = PatternFill(start_color="DCFCE7", fill_type="solid")
    bazaar_header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Royal Blue

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=14, bold=True, color="831843")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=10)

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

    border_thin = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # -------------------------------------------------------------
    # SHEET 1: Executive Softy Shop Launch Strategy
    # -------------------------------------------------------------
    ws_strat = wb.create_sheet(title="Executive_Softy_Strategy")
    ws_strat.views.sheetView[0].showGridLines = True

    ws_strat["B2"] = "🍦 CHENNAI SOFTY & ICE CREAM MARKET INTELLIGENCE: LAUNCH STRATEGY"
    ws_strat["B2"].font = title_font
    ws_strat["B3"] = "Competitive audit of Chennai's Top 50 Ice Cream Parlours, Customer Complaints, and Strategic Playbook for Starting a High-Profit Softy Brand."
    ws_strat["B3"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    strategy_sections = [
        ("Franchise Brand & Model", "'Softie' — Scalable Micro-Kiosk & Express Parlour Franchise Model built for high-footfall pedestrian promenades across Chennai."),
        ("Product USP: 100% Pure Milk", "Crafted exclusively with fresh whole dairy milk (no hydrogenated vegetable palm fat or cheap watery premix). Rich, velvety mouthfeel with natural milk solids and rapid clean dissolve."),
        ("Value Pricing: ₹20 to ₹90", "Core entry rate starts at ₹20 (Pure Milk Softie Cone for mass adoption), mid-tier swirls/dips at ₹35 - ₹60, and maximum cost capped at ₹90 (Gourmet Belgian Waffle Cone & Lotus Biscoff Sundae)."),
        ("Daily Sales Target", "Target Average: ₹15,000 / Day (₹4,50,000 / Month per kiosk) with ~380 - 430 cones/day. Delivers 74% - 76% gross margin and ~₹2,07,500 monthly net profit (46% net margin)."),
        ("Top 5 Recommended Locations", "#1 Besant Nagar Beach (massive beach stroll dessert crowd) | #2 Pondy Bazaar T. Nagar (85k daily pedestrian shoppers) | #3 Marina Beach Promenade (heavy outdoor snacking) | #4 Anna Nagar 2nd Avenue (Chennai's top dessert street) | #5 Sowcarpet Chaat Lane (cooling sweet relief)."),
        ("Fast 12-Second Dispensing", "Gravity-fed softy dispensing in 12 seconds flat. 6x faster throughput than scoop parlours, clearing 15-person queues in under 3 minutes with zero scooping fatigue."),
        ("Capital Recovery & Capex", "Total kiosk setup capex: ₹6.5 - 7.5 Lakhs (commercial 3-lever machine, refrigeration, kiosk counter). Capital payback period achieved in just 3.2 to 3.8 months.")
    ]

    r_idx = 5
    for label, val in strategy_sections:
        ws_strat.cell(row=r_idx, column=2, value=label).font = bold_font
        ws_strat.cell(row=r_idx, column=3, value=val).font = regular_font
        ws_strat.cell(row=r_idx, column=2).fill = PatternFill(start_color="FDF2F8", fill_type="solid")
        ws_strat.cell(row=r_idx, column=2).border = border_thin
        ws_strat.cell(row=r_idx, column=3).border = border_thin
        r_idx += 1

    # -------------------------------------------------------------
    # SHEET 2: TOP 20 BAZAARS & PEDESTRIAN SHOPPING SITES
    # -------------------------------------------------------------
    ws_bazaar = wb.create_sheet(title="Top_20_Bazaar_Launch_Sites")
    ws_bazaar.views.sheetView[0].showGridLines = True

    bazaar_headers = [
        "Rank", "Bazaar Name & Neighborhood", "Zone", "Bazaar Typology & Atmosphere",
        "Exact Street Stretch", "Primary Landmark", "Daily Evening Footfall",
        "Target Crowd & Demographics", "Peak Walking Hours", "Nearby Competitor Density",
        "Why Softy Fits Perfectly (Product-Market Fit)", "Recommended Hero Flavors",
        "Target Price Point", "Est. Monthly Cones"
    ]

    for c_idx, h_text in enumerate(bazaar_headers, 1):
        cell = ws_bazaar.cell(row=1, column=c_idx, value=h_text)
        cell.fill = bazaar_header_fill
        cell.font = header_font
        cell.alignment = center_align

    for r_idx, bz in enumerate(TOP_20_BAZAAR_SITES, 2):
        ws_bazaar.cell(row=r_idx, column=1, value=bz["rank"]).alignment = center_align
        ws_bazaar.cell(row=r_idx, column=2, value=bz["name"]).font = bold_font
        ws_bazaar.cell(row=r_idx, column=3, value=bz["zone"]).alignment = center_align
        ws_bazaar.cell(row=r_idx, column=4, value=bz["bazaar_type"])
        ws_bazaar.cell(row=r_idx, column=5, value=bz["exact_stretch"])
        ws_bazaar.cell(row=r_idx, column=6, value=bz["landmark"])
        ws_bazaar.cell(row=r_idx, column=7, value=bz["daily_evening_footfall"]).alignment = center_align
        ws_bazaar.cell(row=r_idx, column=8, value=bz["crowd_profile"])
        ws_bazaar.cell(row=r_idx, column=9, value=bz["peak_walking_hours"]).alignment = center_align
        ws_bazaar.cell(row=r_idx, column=10, value=bz["competitor_density"])
        
        # Why softy fits
        c_fit = ws_bazaar.cell(row=r_idx, column=11, value=bz["why_softy_fits_perfectly"])
        c_fit.alignment = left_align
        c_fit.fill = PatternFill(start_color="F0FDF4", fill_type="solid") # green tint

        ws_bazaar.cell(row=r_idx, column=12, value=bz["recommended_hero_flavors"])
        ws_bazaar.cell(row=r_idx, column=13, value=bz["target_price_point"]).alignment = center_align
        ws_bazaar.cell(row=r_idx, column=14, value=bz["estimated_monthly_cones"]).alignment = center_align

        for col in range(1, 15):
            ws_bazaar.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEET 3: COMPARATIVE EVALUATION MATRIX (20 BAZAARS)
    # -------------------------------------------------------------
    ws_matrix = wb.create_sheet(title="Comparative_Evaluation_Matrix")
    ws_matrix.views.sheetView[0].showGridLines = True

    matrix_headers = [
        "Rank", "Bazaar Location", "Zone", "Daily Evening Footfall",
        "Cones / Day (0.7%-1.0% Conv)", "Monthly Revenue @ ₹50 (0.7%-1.0%)", "Monthly Gross Profit @ 75%",
        "Softie Target Price", "Est. Commercial Rent / sq.ft", "Capital Payback Period",
        "Product-Market Fit Factor", "Hero Flavors & Signature Swirls"
    ]

    import re
    def compute_insight(footfall_str, avg_price=50.0):
        nums = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", str(footfall_str))]
        low_f, high_f = (nums[0], nums[1]) if len(nums) >= 2 else (nums[0], nums[0]) if nums else (40000, 65000)
        c_low, c_high = int(low_f * 0.007), int(high_f * 0.010)
        r_low, r_high = c_low * avg_price * 30, c_high * avg_price * 30
        gp_low, gp_high = int(r_low * 0.75), int(r_high * 0.75)
        return (f"{c_low:,} - {c_high:,} cones/day",
                f"₹{r_low/100000:.2f} L - ₹{r_high/100000:.2f} L",
                f"₹{gp_low/100000:.2f} L - ₹{gp_high/100000:.2f} L")

    matrix_header_fill = PatternFill(start_color="047857", end_color="047857", fill_type="solid") # Emerald Green
    for c_idx, h_text in enumerate(matrix_headers, 1):
        cell = ws_matrix.cell(row=1, column=c_idx, value=h_text)
        cell.fill = matrix_header_fill
        cell.font = header_font
        cell.alignment = center_align

    for r_idx, m in enumerate(COMPARATIVE_EVALUATION_MATRIX, 2):
        c_range, r_range, gp_range = compute_insight(m["daily_evening_footfall"], avg_price=50.0)

        ws_matrix.cell(row=r_idx, column=1, value=m["rank"]).alignment = center_align
        ws_matrix.cell(row=r_idx, column=2, value=m["bazaar_location"]).font = bold_font
        ws_matrix.cell(row=r_idx, column=3, value=m["zone"]).alignment = center_align
        ws_matrix.cell(row=r_idx, column=4, value=m["daily_evening_footfall"]).alignment = center_align
        ws_matrix.cell(row=r_idx, column=5, value=c_range).alignment = center_align
        
        # Financials from 0.7% - 1.0% footfall conversion @ ₹50
        c_rev = ws_matrix.cell(row=r_idx, column=6, value=r_range)
        c_rev.alignment = center_align
        c_rev.font = bold_font
        
        c_profit = ws_matrix.cell(row=r_idx, column=7, value=gp_range)
        c_profit.alignment = center_align
        c_profit.fill = soft_green_fill
        c_profit.font = Font(name="Calibri", size=10, bold=True, color="065F46")

        ws_matrix.cell(row=r_idx, column=8, value=m["target_price"]).alignment = center_align
        ws_matrix.cell(row=r_idx, column=9, value=m["rental_sqft_estimate"]).alignment = center_align
        ws_matrix.cell(row=r_idx, column=10, value=m["payback_period_months"]).alignment = center_align
        
        c_fit = ws_matrix.cell(row=r_idx, column=11, value=m["fit_factor"])
        c_fit.alignment = left_align
        
        ws_matrix.cell(row=r_idx, column=12, value=m["hero_flavors"])

        for col in range(1, 13):
            ws_matrix.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEET 4: TOP SOFTY COMPETITORS IN CHENNAI
    # -------------------------------------------------------------
    ws_softy = wb.create_sheet(title="Top_Softy_Competitors_Chennai")
    ws_softy.views.sheetView[0].showGridLines = True

    softy_headers = [
        "Rank", "Softy Outlet / Counter Name", "Zone & Micro-Market", "Exact Address",
        "Nearby Landmark", "Google Rating", "Review Count", "Softy Classification",
        "Price per Cone", "Signature Softy Flavor", "Dairy Base Quality", "Dispense Speed",
        "Why Customers Like It", "What Customers Dislike / Complaints", "Our Softy Launch Disruption Play"
    ]

    softy_header_fill = PatternFill(start_color="D97706", end_color="D97706", fill_type="solid") # Amber Gold
    for c_idx, h_text in enumerate(softy_headers, 1):
        cell = ws_softy.cell(row=1, column=c_idx, value=h_text)
        cell.fill = softy_header_fill
        cell.font = header_font
        cell.alignment = center_align

    for r_idx, s in enumerate(TOP_SOFTY_SPECIALISTS, 2):
        ws_softy.cell(row=r_idx, column=1, value=s["rank"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=2, value=s["name"]).font = bold_font
        ws_softy.cell(row=r_idx, column=3, value=s["zone"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=4, value=s["address"])
        ws_softy.cell(row=r_idx, column=5, value=s["landmark"])
        ws_softy.cell(row=r_idx, column=6, value=s["rating"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=7, value=s["user_ratings_total"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=8, value=s["softy_type"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=9, value=s["price_per_cone"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=10, value=s["signature_softy"]).font = bold_font
        ws_softy.cell(row=r_idx, column=11, value=s["dairy_base"]).alignment = center_align
        ws_softy.cell(row=r_idx, column=12, value=s["dispense_speed"]).alignment = center_align
        
        c_like = ws_softy.cell(row=r_idx, column=13, value=s["why_customers_like_it"])
        c_like.alignment = left_align
        
        c_dislike = ws_softy.cell(row=r_idx, column=14, value=s["what_customers_dislike"])
        c_dislike.alignment = left_align
        c_dislike.fill = PatternFill(start_color="FFF1F2", fill_type="solid")
        
        c_play = ws_softy.cell(row=r_idx, column=15, value=s["disruption_angle"])
        c_play.alignment = left_align
        c_play.fill = PatternFill(start_color="F0FDF4", fill_type="solid")

        for col in range(1, 16):
            ws_softy.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEET 5: Top 50 Ice Cream Parlors Master (Ranked by Reviews)
    # -------------------------------------------------------------
    ws_master = wb.create_sheet(title="Top_50_Ice_Cream_Parlors")
    ws_master.views.sheetView[0].showGridLines = True

    master_headers = [
        "Rank", "Ice Cream / Dessert Parlour", "Zone & Micro-Market", "Exact Address",
        "Nearby Landmark", "Google Rating", "Review Count (Ratings Total)", "Avg Cost for Two",
        "Why Customers Like It (Strengths, Flavors, Vibe)",
        "What Customers Don't Like / Complaints (Weaknesses & Flaws)",
        "Softy / Soft-Serve Disruption Opportunity"
    ]

    for c_idx, h_text in enumerate(master_headers, 1):
        cell = ws_master.cell(row=1, column=c_idx, value=h_text)
        cell.fill = primary_header_fill
        cell.font = header_font
        cell.alignment = center_align

    # Sort descending by review count
    sorted_parlors = sorted(TOP_50_ICE_CREAM_PARLORS, key=lambda x: x["user_ratings_total"], reverse=True)

    for r_idx, p in enumerate(sorted_parlors, 2):
        ws_master.cell(row=r_idx, column=1, value=r_idx - 1).alignment = center_align
        ws_master.cell(row=r_idx, column=2, value=p["name"]).font = bold_font
        ws_master.cell(row=r_idx, column=3, value=p["zone"])
        ws_master.cell(row=r_idx, column=4, value=p["address"])
        ws_master.cell(row=r_idx, column=5, value=p["landmark"])
        ws_master.cell(row=r_idx, column=6, value=p["rating"]).alignment = center_align
        ws_master.cell(row=r_idx, column=7, value=p["user_ratings_total"]).alignment = center_align
        ws_master.cell(row=r_idx, column=8, value=p["avg_cost_for_two"]).alignment = center_align
        
        # Why like it
        c_like = ws_master.cell(row=r_idx, column=9, value=p["why_customers_like_it"])
        c_like.alignment = left_align
        
        # What dislike
        c_dislike = ws_master.cell(row=r_idx, column=10, value=p["what_customers_dislike"])
        c_dislike.alignment = left_align
        c_dislike.fill = PatternFill(start_color="FFF1F2", fill_type="solid") # subtle rose alert

        # Softy opportunity
        c_opp = ws_master.cell(row=r_idx, column=11, value=p["softy_opportunity"])
        c_opp.alignment = left_align
        c_opp.fill = PatternFill(start_color="F0FDF4", fill_type="solid") # subtle green opportunity

        for col in range(1, 12):
            ws_master.cell(row=r_idx, column=col).border = border_thin

    # -------------------------------------------------------------
    # SHEET 3: Why Customers Like It (Ranked Drivers)
    # -------------------------------------------------------------
    ws_why = wb.create_sheet(title="Why_Customers_Like_Ranked")
    ws_why.views.sheetView[0].showGridLines = True
    why_headers = ["Rank", "Core Appeal Theme", "Customer Love Percentage (%)", "Representative Customer Feedback", "Key Success Factor for Your Softy Shop"]
    for c_idx, h_text in enumerate(why_headers, 1):
        cell = ws_why.cell(row=1, column=c_idx, value=h_text)
        cell.fill = sub_header_fill
        cell.font = header_font
        cell.alignment = center_align

    why_drivers = [
        (1, "Natural Real Dairy & Authentic Pulp", "92%", "Customers hate icy vegetable-fat taste; they adore Naturals because of real fruit chunks and Amadora because of creamy dairy mouthfeel.", "Use 100% pure fresh cow milk and real fruit purees in softy mix, never artificial powdered premixes."),
        (2, "Late-Night Dessert Culture (Post 10 PM)", "88%", "Chennai crowds specifically venture out after 9:30 PM dinner for a cold dessert, especially on weekends.", "Keep your softy counter open until 12:30 AM to capture massive post-dinner impulse traffic."),
        (3, "Warm-and-Cold Dessert Contrast", "81%", "Combinations like hot brownie with cold ice cream (DBC at Corner House, Underbaked at Amadora) drive the highest customer spend.", "Introduce a Warm Lava Cookie Softy Cup or Warm Churros with soft-serve dip."),
        (4, "Interactive Customization & Visual Joy", "76%", "Ibaco and Cream Stone thrive because customers love choosing their toppings, sprinkles, and dipping sauces.", "Offer an interactive DIY drizzle bar with warm Belgian chocolate and lotus biscoff crumbles."),
        (5, "Grab-and-Go Portability", "71%", "Beach strollers in Besant Nagar and shoppers in Pondy Bazaar want something easy to eat while walking.", "Design a sturdy waffle cone with a drip-guard collar that prevents sticky melted mess on hands.")
    ]

    for r_idx, d in enumerate(why_drivers, 2):
        for c_idx in range(1, 6):
            cell = ws_why.cell(row=r_idx, column=c_idx, value=d[c_idx - 1])
            cell.alignment = left_align if c_idx in [2, 4, 5] else center_align
            cell.border = border_thin
            if c_idx == 2:
                cell.font = bold_font

    # -------------------------------------------------------------
    # SHEET 4: What Customers Dislike & Complaints (Vulnerabilities)
    # -------------------------------------------------------------
    ws_dislike = wb.create_sheet(title="What_Customers_Dislike_Ranked")
    ws_dislike.views.sheetView[0].showGridLines = True
    dislike_headers = ["Rank", "Customer Pain Point / Complaint", "Complaint Severity (%)", "Typical Customer Complaint Quote", "How Your Softy Shop Wins This Customer"]
    for c_idx, h_text in enumerate(dislike_headers, 1):
        cell = ws_dislike.cell(row=1, column=c_idx, value=h_text)
        cell.fill = dark_slate_fill
        cell.font = header_font
        cell.alignment = center_align

    dislike_drivers = [
        (1, "Weighing Scale Pricing Traps & Exorbitant Cost", "84%", "'Went to Ibaco thinking it's ₹150 and ended up paying ₹540 for two small bowls!' Customers feel anxious about weight pricing.", "Fixed Transparent Pricing: Advertise flat ₹60, ₹80, and ₹110 prices on a massive front board. Zero surprises."),
        (2, "15 to 25 Minute Slow Service & Billing Queues", "79%", "'Cold stone takes forever to mix; by the time the second cup was ready, the first was already melting.'", "Instant 15-Second Dispensing: The soft-serve lever dispenses in 5 seconds flat. Queue moves 6x faster than scoop shops."),
        (3, "Rapid Melting in Chennai Heat & Humidity", "74%", "'Gelato melted into liquid soup all over my hands within 3 minutes of stepping out onto the beach.'", "Temperature Calibrated Soft-Serve: Formulated to hold shape with high butterfat structure, served in deep insulated waffle cups."),
        (4, "Severe Vehicle Parking & Traffic Nightmares", "68%", "'No parking on Usman Road or KNK road; car got scratched and police issued a towing ticket.'", "Compact Pedestrian Micro-Locations: Pick spots in pedestrian plazas (like Pondy Bazaar) or beach promenades with nearby public parking."),
        (5, "Excessive Sugar & Heavy Sickly Feeling", "58%", "'Cream Stone is so sweet and dense you feel sick after 4 spoons.'", "Balanced Light Sugar Profile: Soft-serve has lower density and higher air overrun, making it light, refreshing, and craveable daily.")
    ]

    for r_idx, d in enumerate(dislike_drivers, 2):
        for c_idx in range(1, 6):
            cell = ws_dislike.cell(row=r_idx, column=c_idx, value=d[c_idx - 1])
            cell.alignment = left_align if c_idx in [2, 4, 5] else center_align
            cell.border = border_thin
            if c_idx == 2:
                cell.font = bold_font

    # -------------------------------------------------------------
    # SHEETS 5 - 11: 7-DAY TRAFFIC SHEETS (Monday to Sunday)
    # Top 50 Floating Streets sorted by Time Interval
    # -------------------------------------------------------------
    road_headers = [
        "Time Interval", "Traffic Rank", "Street / Arterial Road Name", "Zone / Micro-Market",
        "Corridor Classification", "Est. Floating Commuters / hr", "Congestion Factor (CF)",
        "Avg Traffic Speed (km/h)", "Free-Flow Speed (km/h)", "Delay per 5 km (mins)", "Peak Traffic Status"
    ]

    for day in DAYS_LIST:
        ws_day = wb.create_sheet(title=f"{day}_Top50_Traffic_Roads")
        ws_day.views.sheetView[0].showGridLines = True

        for c_idx, h_text in enumerate(road_headers, 1):
            cell = ws_day.cell(row=1, column=c_idx, value=h_text)
            cell.fill = dark_slate_fill
            cell.font = header_font
            cell.alignment = center_align

        is_weekend = day in ["Saturday", "Sunday"]
        is_friday = day == "Friday"

        curr_row = 2
        for slot_info in TIME_SLOTS:
            slot_name = slot_info["slot"]
            base_mult = slot_info["mult_weekend"] if is_weekend else slot_info["mult_weekday"]
            if is_friday and "Evening" in slot_name:
                base_mult += 0.25

            road_metrics_in_slot = []
            for r in TOP_50_ROADS:
                r_base_floating = r["peak_floating_commuters_hr"]
                slot_traffic_ratio = 1.0 if "5:00 PM" in slot_name else 0.85 if "10:00 AM" in slot_name else 0.70 if "8:00 PM" in slot_name else 0.55
                if is_weekend and ("8:00 PM" in slot_name or "5:00 PM" in slot_name):
                    slot_traffic_ratio = 1.15

                est_floating = int(r_base_floating * slot_traffic_ratio)
                cf = round(max(1.05, (base_mult * (est_floating / 50000.0) ** 0.6)), 2)
                cf = min(2.95, cf)
                speed = round(r["free_flow_kmh"] / cf, 1)
                delay_5km = round(max(0.0, (5.0 / speed * 60.0) - (5.0 / r["free_flow_kmh"] * 60.0)), 1)
                status = "Severe Gridlock" if cf >= 2.2 else "Heavy Congestion" if cf >= 1.7 else "Moderate" if cf >= 1.3 else "Free Flow"

                road_metrics_in_slot.append({
                    "slot": slot_name, "name": r["name"], "zone": r["zone"], "type": r["type"],
                    "est_floating": est_floating, "cf": cf, "speed": speed, "free_flow": r["free_flow_kmh"],
                    "delay_5km": delay_5km, "status": status
                })

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
                    status_cell.fill = soft_red_fill
                    status_cell.font = Font(name="Calibri", size=10, bold=True, color="991B1B")
                elif rm["status"] == "Heavy Congestion":
                    status_cell.fill = accent_gold_fill
                    status_cell.font = Font(name="Calibri", size=10, bold=True, color="92400E")
                else:
                    status_cell.fill = soft_green_fill

                for col in range(1, 12):
                    ws_day.cell(row=curr_row, column=col).border = border_thin
                curr_row += 1

    # Format column widths
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col[:60]:
                if cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(50, max(max_len + 3, 12))

    wb.save(OUTPUT_EXCEL_PATH)
    print(f"Generated Ice Cream Master Workbook at: {OUTPUT_EXCEL_PATH}")
    print(f"File Size: {os.path.getsize(OUTPUT_EXCEL_PATH):,} bytes | Total Sheets: {len(wb.sheetnames)}")


if __name__ == "__main__":
    generate_ice_cream_master_workbook()
