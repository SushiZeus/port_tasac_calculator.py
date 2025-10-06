import streamlit as st
import locale
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Port & Shipping Charges Calculator",
    page_icon="⚓",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .result-box {
        background-color: #F0F8FF;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF6B35;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton button {
        background-color: #2E8B57 !important;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #228B22 !important;
    }
    .section-header {
        color: #2E8B57;
        border-bottom: 2px solid #FF6B35;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# TASAC Charges Data
TASAC_CHARGES = {
    "USA/CANADA/SOUTH AMERICA": {
        "Petroleum & Products": 0.43,
        "Dry Bulk": 0.43,
        "Liquid Bulk": 1.07,
        "General Cargo": 2.49,
        "20FT Standard": 49.84,
        "40FT Standard": 99.67,
        "40FT High Cube": 124.59
    },
    "FAREAST/CHINA/MALAYSIA/SINGAPORE/THAILAND": {
        "Petroleum & Products": 0.43,
        "Dry Bulk": 0.43,
        "Liquid Bulk": 1.07,
        "General Cargo": 2.49,
        "20FT Standard": 49.84,
        "40FT Standard": 99.67,
        "40FT High Cube": 124.59
    },
    "AUSTRALIA/NEW ZEALAND": {
        "Petroleum & Products": 0.43,
        "Dry Bulk": 0.43,
        "Liquid Bulk": 1.07,
        "General Cargo": 2.49,
        "20FT Standard": 49.84,
        "40FT Standard": 99.67,
        "40FT High Cube": 124.59
    },
    "NWC/UK (EUROPE)": {
        "Petroleum & Products": 0.36,
        "Dry Bulk": 0.36,
        "Liquid Bulk": 0.71,
        "General Cargo": 2.14,
        "20FT Standard": 42.72,
        "40FT Standard": 85.43,
        "40FT High Cube": 106.79
    },
    "INDIA & PAKISTAN": {
        "Petroleum & Products": 0.43,
        "Dry Bulk": 0.43,
        "Liquid Bulk": 0.71,
        "General Cargo": 2.14,
        "20FT Standard": 42.72,
        "40FT Standard": 85.43,
        "40FT High Cube": 106.79
    },
    "ARABIA GULF/PERSIA": {
        "Petroleum & Products": 0.36,
        "Dry Bulk": 0.36,
        "Liquid Bulk": 0.36,
        "General Cargo": 1.07,
        "20FT Standard": 21.36,
        "40FT Standard": 42.72,
        "40FT High Cube": 53.40
    },
    "SOUTH AFRICA": {
        "Petroleum & Products": 0.36,
        "Dry Bulk": 0.36,
        "Liquid Bulk": 0.36,
        "General Cargo": 1.07,
        "20FT Standard": 21.36,
        "40FT Standard": 42.72,
        "40FT High Cube": 53.40
    }
}

# Constants for port charges
shf = 119
clf = 12
cvf = 140
tsf = 65
ihf = 140
ecf = 150000
sht = 79
clt = 6
cvt = 70
tst = 65
iht = 90
ect = 75000

def format_currency_with_commas(amount, currency_symbol='$'):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    
    try:
        formatted_amount = locale.currency(amount, symbol=currency_symbol, grouping=True)
        return formatted_amount
    except:
        return f"{currency_symbol}{amount:,.2f}"

def count_days_between_dates(start_date, end_date):
    delta = end_date - start_date
    return delta.days + 1

def calculate_tasac_charges(origin, cargo_type, quantity):
    """Calculate TASAC shipping fees"""
    if origin in TASAC_CHARGES and cargo_type in TASAC_CHARGES[origin]:
        rate = TASAC_CHARGES[origin][cargo_type]
        
        # Determine if it's per ton or per container
        if "FT" in cargo_type or "General Cargo" in cargo_type:
            # Containerized or General Cargo - fixed per unit
            return rate * quantity
        else:
            # Bulk cargo - per ton
            return rate * quantity
    return 0

def calculate_air_charges(weight, is_dg, carry_in_date, carry_out_date, shipment_type):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if weight < 33:
        eq = 0
    elif 33 <= weight <= 50:
        eq = 10.5
    elif 51 <= weight <= 500:
        eq = 26
    elif 501 <= weight <= 5000:
        eq = 67
    elif 5001 <= weight <= 9999:
        eq = 115
    else:
        eq = 432

    if is_dg == "DG":
        han = 0.185 * weight
        if han < 40:
            han = 40
        sto = 0.1854 * weight * d0
        if sto < 40:
            sto = 40
    else:
        han = 0.085 * weight
        if han < 22:
            han = 22
        if d0 < 3:
            sto = 0
        else:
            sto = 0.0515 * weight * (d0 - 3)
            if sto < 20:
                sto = 20

    DDT = 2
    TAA = 0.04 * weight
    sec = 0.025 * weight
    if sec < 5:
        sec = 5
    
    if shipment_type == "MAWB":
        no = 1
        doc = 20
        bre = 0
    else:
        no = 1
        doc = 0
        bre = 78

    tot = ((DDT + doc + eq + han + no + sec + sto) * 1.18) + TAA

    charges = {
        "Tanzania Airport Authority (TAA)": TAA,
        "Data Discharge Tancis": DDT,
        "Documentation": doc,
        "Equipment Charges": eq,
        "Handling Charges": han,
        "Notification Charges": no,
        "General Cargo Storage": sto,
        "Security Surcharges": sec,
        "Break Bulk Charges": bre,
        "Total Swissport Charges": tot
    }
    
    return charges, d0

def calculate_lcl_charges(cbm, carry_in_date, carry_out_date):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if d0 <= 5:
        d1 = 0
        stl = d1 * cbm * 1
        cwl = 0.3 * cbm
        shl = 7 * cbm
        stp = 5.3 * cbm
        rcl = 0
        cwt = 0
    else:
        d1 = d0 - 5
        stl = d1 * cbm * 1
        cwl = 0.3 * cbm
        shl = 7 * cbm
        stp = 5.3 * cbm
        rcl = 2 * cbm
        if d1 < 21:
            cwt = 0
        else:
            cwt = 0.33 * cbm * (d1 - 14)

    tot = ((stl + cwl + shl + stp + rcl) * 1.18)

    charges = {
        "Storage Charges": stl,
        "Corridor Levy Charges": cwl,
        "Removal Charges": rcl,
        "Shore Handling Charges": shl,
        "Stripping Charges": stp,
        "Customs Warehouse Rent": cwt,
        "Port and ICD Charges for LCL shipment": tot
    }
    
    return charges, d0

def calculate_20ft_charges(containers, carry_in_date, carry_out_date):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if d0 <= 5:
        stt = 0
        cwt = 0
        rct = 0
    elif d0 <= 15:
        d3 = d0 - 5
        dr = (d3 * 20) * 1.18
        stt = dr * containers
        cwt = 0
        rct = (100 * containers) * 1.18
    else:
        d4 = d0 - 5
        df = d4 - 10
        d5 = (10 * 20) * 1.18
        d6 = (df * 40) * 1.18
        d7 = d5 + d6
        stt = d7 * containers
        rct = (100 * containers) * 1.18
        if d0 > 21:
            cwt = (0.33 * 36 * (d0 - 14)) * containers
        else:
            cwt = 0

    s = sht * containers
    c = clt * containers
    cv = cvt * containers
    i = iht * containers
    t = tst * containers
    e = ect * containers
    sam = (s + c + cv + i + t) * 1.18
    tot = sam + stt + rct

    charges = {
        "Storage Charges": stt,
        "Removal Charges": rct,
        "Shore Handling Charges": s,
        "Customs Verification Charges": cv,
        "Corridor Levy Charges": c,
        "ICD Handling Charges": i,
        "Container Transfer Charges": t,
        "Customs Warehouse Rent Charges": cwt,
        "Port and ICD Charges for 20FT Container": tot
    }
    
    return charges, d0

def calculate_40ft_charges(containers, carry_in_date, carry_out_date, container_type="Standard"):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if d0 <= 5:
        stf = 0
        cwf = 0
        rcf = 0
    elif d0 <= 15:
        d3 = d0 - 5
        dr = (d3 * 40) * 1.18
        stf = dr * containers
        cwf = 0
        rcf = (150 * containers) * 1.18
    else:
        d4 = d0 - 5
        df = d4 - 10
        d5 = (10 * 40) * 1.18
        d6 = (df * 80) * 1.18
        d7 = d5 + d6
        stf = d7 * containers
        rcf = (150 * containers) * 1.18
        if d0 > 21:
            cwf = (0.33 * 72 * (d0 - 21)) * containers
        else:
            cwf = 0

    s = shf * containers
    c = clf * containers
    cv = cvf * containers
    i = ihf * containers
    t = tsf * containers
    e = ecf * containers
    sam = (s + c + cv + i + t) * 1.18
    tot = sam + stf + rcf

    charges = {
        "Storage Charges": stf,
        "Removal Charges": rcf,
        "Shore Handling Charges": s,
        "Customs Verification Charges": cv,
        "Corridor Levy Charges": c,
        "ICD Handling Charges": i,
        "Container Transfer Charges": t,
        "Customs Warehouse Rent Charges": cwf,
        "Port and ICD Charges for 40FT Container": tot
    }
    
    return charges, d0

# Main app
st.markdown('<div class="main-header">⚓ Port & Shipping Charges Calculator</div>', unsafe_allow_html=True)

# Shipment origin and type
st.markdown('<div class="section-header">🌍 Shipment Origin & Type</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    origin = st.selectbox(
        "Select Origin Route",
        list(TASAC_CHARGES.keys()),
        help="Choose the shipping route origin"
    )
    
with col2:
    shipment_category = st.selectbox(
        "Select Shipment Category",
        ["SEA", "AIR"],
        help="Choose between sea or air shipment"
    )

# Date inputs
st.markdown('<div class="section-header">📅 Storage Period</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    carry_in_date = st.date_input("Carry-in Date", value=date.today())
with col2:
    carry_out_date = st.date_input("Carry-out Date", value=date.today())

# Validate dates
if carry_out_date < carry_in_date:
    st.error("Carry-out date cannot be before carry-in date!")
else:
    # Shipment-specific inputs
    if shipment_category == "SEA":
        st.markdown('<div class="section-header">🚢 Sea Cargo Details</div>', unsafe_allow_html=True)
        
        cargo_type = st.selectbox(
            "Select Cargo Type",
            ["Dry Bulk", "Liquid Bulk", "Petroleum & Products", "General Cargo", "20FT Standard", "40FT Standard", "40FT High Cube"],
            help="Choose the type of cargo"
        )
        
        # Quantity input based on cargo type
        if "FT" in cargo_type:
            quantity = st.number_input("Number of Containers", min_value=1, value=1, step=1)
            quantity_label = "containers"
        elif cargo_type == "General Cargo":
            quantity = st.number_input("Freight Tons", min_value=0.1, value=10.0, step=0.1)
            quantity_label = "freight tons"
        else:  # Bulk cargo
            quantity = st.number_input("Tons", min_value=0.1, value=100.0, step=0.1)
            quantity_label = "tons"
        
        if st.button("Calculate Sea Charges", type="primary"):
            # Calculate TASAC charges
            tasac_total = calculate_tasac_charges(origin, cargo_type, quantity)
            
            # Calculate port charges based on cargo type
            if cargo_type == "20FT Standard":
                port_charges, days = calculate_20ft_charges(quantity, carry_in_date, carry_out_date)
                shipment_type = "20FT Container"
            elif cargo_type in ["40FT Standard", "40FT High Cube"]:
                port_charges, days = calculate_40ft_charges(quantity, carry_in_date, carry_out_date)
                shipment_type = "40FT Container"
            elif cargo_type == "General Cargo":
                # For general cargo, use LCL calculation
                port_charges, days = calculate_lcl_charges(quantity, carry_in_date, carry_out_date)
                shipment_type = "General Cargo"
            else:
                # For bulk cargo, minimal port charges
                days = count_days_between_dates(carry_in_date, carry_out_date)
                port_charges = {"Basic Port Handling": quantity * 5}  # Placeholder
                shipment_type = f"{cargo_type}"
            
            st.success(f"✅ Calculation Complete! Storage period: {days} days")
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚢 TASAC Shipping Fees")
                st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                st.write(f"**Origin:** {origin}")
                st.write(f"**Cargo Type:** {cargo_type}")
                st.write(f"**Quantity:** {quantity} {quantity_label}")
                st.write(f"**TASAC Rate:** {format_currency_with_commas(TASAC_CHARGES[origin][cargo_type])} per {quantity_label.split(' ')[0]}")
                st.write(f"**Total TASAC Charges:** {format_currency_with_commas(tasac_total)}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.subheader("⚓ Port Charges")
                st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                for charge_name, amount in port_charges.items():
                    if amount > 0:  # Only show non-zero charges
                        st.write(f"**{charge_name}:** {format_currency_with_commas(amount)}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Total summary
            total_port_charges = sum(port_charges.values())
            grand_total = tasac_total + total_port_charges
            
            st.markdown("---")
            st.subheader("💰 Total Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("TASAC Shipping Fees", format_currency_with_commas(tasac_total))
            with col2:
                st.metric("Port Charges", format_currency_with_commas(total_port_charges))
            with col3:
                st.metric("**Grand Total**", format_currency_with_commas(grand_total), 
                         delta=format_currency_with_commas(tasac_total))

    else:  # AIR shipment
        st.markdown('<div class="section-header">✈️ Air Cargo Details</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            weight = st.number_input("Cargo Weight (kg)", min_value=0.1, value=100.0, step=0.1)
        with col2:
            is_dg = st.radio("Cargo Type", ["DG", "NOT"])
        with col3:
            air_shipment_type = st.radio("Shipment Type", ["MAWB", "CONSO"])
        
        if st.button("Calculate Air Charges", type="primary"):
            charges, days = calculate_air_charges(weight, is_dg, carry_in_date, carry_out_date, air_shipment_type)
            
            st.success(f"✅ Calculation Complete! Storage period: {days} days")
            st.subheader("💰 Charge Breakdown")
            
            for charge_name, amount in charges.items():
                if amount > 0:  # Only show non-zero charges
                    st.markdown(f'<div class="result-box"><strong>{charge_name}:</strong> {format_currency_with_commas(amount)}</div>', unsafe_allow_html=True)

# Instructions
st.markdown("---")
st.info("💡 **Instructions:** Select shipment origin and type, enter dates and required details, then click calculate to see the comprehensive charge breakdown including TASAC shipping fees.")
