# Phase 3 Requirements System - Main Application
import streamlit as st
import os
import json
import time
from datetime import datetime, date
from dotenv import load_dotenv
from db_connector import DatabaseConnector
from bundling_engine import SmartBundlingEngine
# Page configuration
st.set_page_config(
    page_title="Requirements Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

def require_login():
    """Login gate - adapted from Phase 2's proven pattern"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
        
    if not st.session_state.logged_in:
        st.title("Requirements Management System")
        st.caption("Please enter your credentials to continue.")
        
        with st.form("login_form"):
            user = st.text_input("Username", key="login_user")
            pwd = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Check credentials against database (simple string password)
                if user.strip() and pwd:
                    try:
                        db = DatabaseConnector()
                        
                        # Check database connection first
                        if not db.conn:
                            st.error(f"Database connection failed: {db.connection_error}")
                            return
                        
                        # 1) Check for Master/Operator/Operation credentials from Streamlit secrets (preferred)
                        master_user = master_pass = operator_user = operator_pass = None
                        operation_user = operation_pass = None
                        try:
                            master_user = st.secrets["app_roles"]["master"].get("username")
                            master_pass = st.secrets["app_roles"]["master"].get("password")
                        except Exception:
                            pass
                        try:
                            operator_user = st.secrets["app_roles"]["operator"].get("username")
                            operator_pass = st.secrets["app_roles"]["operator"].get("password")
                        except Exception:
                            pass
                        try:
                            operation_user = st.secrets["app_roles"]["operation"].get("username")
                            operation_pass = st.secrets["app_roles"]["operation"].get("password")
                        except Exception:
                            pass

                        # 2) Fallback to environment variables only if secrets are not configured
                        if not master_user:
                            master_user = os.getenv('MASTER_USERNAME')
                            master_pass = os.getenv('MASTER_PASSWORD')
                        if not operator_user:
                            operator_user = os.getenv('OPERATOR_USERNAME')
                            operator_pass = os.getenv('OPERATOR_PASSWORD')
                        if not operation_user:
                            operation_user = os.getenv('OPERATION_USERNAME')
                            operation_pass = os.getenv('OPERATION_PASSWORD')

                        entered = user.strip()
                        if master_user and entered == master_user and pwd == (master_pass or ''):
                            # Master login via secrets/env
                            st.session_state.logged_in = True
                            st.session_state.user_role = 'master'
                            st.session_state.user_id = 'master'
                            st.session_state.username = master_user
                            st.success("Logged in successfully as Master")
                            st.rerun()
                        elif operator_user and entered == operator_user and pwd == (operator_pass or ''):
                            # Operator login via secrets/env
                            st.session_state.logged_in = True
                            st.session_state.user_role = 'operator'
                            st.session_state.user_id = 'operator'
                            st.session_state.username = operator_user
                            st.success("Logged in successfully as Operator")
                            st.rerun()
                        elif operation_user and entered == operation_user and pwd == (operation_pass or ''):
                            # Operation Team login via secrets/env
                            st.session_state.logged_in = True
                            st.session_state.user_role = 'operation'
                            st.session_state.user_id = 'operation'
                            st.session_state.username = 'Operation Team'
                            st.success("Logged in successfully as Operation Team")
                            st.rerun()
                        else:
                            # Try to authenticate regular user from database
                            user_data = db.authenticate_user(user.strip(), pwd)
                            
                            if user_data:
                                st.session_state.logged_in = True
                                st.session_state.user_role = user_data['user_role']
                                st.session_state.user_id = user_data['user_id']
                                st.session_state.username = user_data['username']
                                st.success(f"Logged in successfully as {user_data['user_role']}")
                                st.rerun()
                            else:
                                st.error("Invalid credentials. Please check your username and password.")
                            
                        db.close_connection()
                        
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
                    st.error("Please enter both username and password.")
        
        
        st.stop()

def main():
    """Main application"""
    # Initialize database connection
    try:
        db = DatabaseConnector()
    except Exception as e:
        st.error(f"Failed to initialize database connector: {str(e)}")
        st.stop()
    
    # Require login
    require_login()
    
    # Role-based routing
    if str(st.session_state.user_role or '').lower() == 'operation':
        # Load operation team dashboard
        display_operation_team_dashboard(db)
        return
    elif str(st.session_state.user_role or '').lower() in ('operator', 'admin', 'master'):
        # Load operator/master dashboard
        display_operator_dashboard(db)
        return
    
    # Create sidebar for regular users
    with st.sidebar:
        st.markdown("**Requirements Management System**")
        st.markdown(f"*Logged in as: {st.session_state.user_role}*")
        st.markdown(f"*User: {st.session_state.username}*")
        st.markdown("---")
        
        # Database connection status (same as Phase 2)
        st.subheader("Database")
        is_connected, message, connection_details, error_info = db.check_db_connection()
        
        if is_connected:
            st.success("Connected")
        else:
            st.error("Connection Failed")
            if "ODBC Driver" in message:
                st.warning("ODBC Driver issue detected")
            elif "firewall" in message.lower():
                st.warning("Possible firewall block")
            elif "login failed" in message.lower():
                st.warning("Invalid credentials")
            
            with st.expander("Error Details"):
                st.error(message)
        
        # Logout
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    # Initialize cart in session state
    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []
    
    # Main content area - Simple tab navigation
    if st.session_state.user_role != 'operator':  # Show for all non-operator users
        # Create tabs - clean and simple
        # BOXHERO TAB - HIDDEN (Users can't request BoxHero items yet - will enable later)
        # Uncomment line below and adjust tab variables when ready to enable
        # tab1, tab2, tab3, tab4 = st.tabs(["📦 BoxHero Items", "🔧 Raw Materials", "🛒 My Cart", "📋 My Requests"])
        tab1, tab2, tab3 = st.tabs(["🔧 Raw Materials", "🛒 My Cart", "📋 My Requests"])
        
        # with tab1:
        #     display_boxhero_tab(db)
        
        with tab1:
            display_raw_materials_tab(db)
        
        with tab2:
            display_cart_tab(db)
        
        with tab3:
            display_my_requests_tab(db)
    
    else:
        # Fallback for unknown user roles
        st.error(f"Unknown user role: {st.session_state.user_role}")
        st.info("Please contact administrator or try logging out and back in.")
    
    
    # Close database connection
    db.close_connection()

def display_boxhero_tab(db):
    """Smart questionnaire flow for BoxHero items selection"""
    st.header("📦 BoxHero Items")
    st.caption("Select your item step by step")
    
    # Initialize session state for BoxHero flow
    if 'bh_step' not in st.session_state:
        st.session_state.bh_step = 1
    if 'bh_selected_type' not in st.session_state:
        st.session_state.bh_selected_type = None
    if 'bh_selected_item' not in st.session_state:
        st.session_state.bh_selected_item = None
    
    try:
        # Get all BoxHero items with lightweight session cache (TTL ~60s)
        now_ts = time.time()
        cache_key = 'bh_items_cache'
        cache_ttl = 60
        if cache_key not in st.session_state or (now_ts - st.session_state[cache_key]['ts'] > cache_ttl):
            all_items = db.get_all_items(source_filter="BoxHero")
            st.session_state[cache_key] = {'data': all_items or [], 'ts': now_ts}
        else:
            all_items = st.session_state[cache_key]['data']
        
        if not all_items:
            st.info("No BoxHero items available at the moment.")
            return
        
        # Use all items - duplicate check happens in add_to_cart()
        available_items = all_items
        
        # Step 1: Select Item Type
        if st.session_state.bh_step >= 1:
            st.subheader("Step 1: What type of item do you need?")
            
            # Get unique item types from available items only
            item_types = sorted(list(set(item.get('item_type', '') for item in available_items if item.get('item_type'))))
            
            selected_type = st.selectbox(
                "Choose item type:",
                [""] + item_types,
                index=0 if not st.session_state.bh_selected_type else item_types.index(st.session_state.bh_selected_type) + 1,
                key="bh_type_select"
            )
            
            if selected_type and selected_type != st.session_state.bh_selected_type:
                st.session_state.bh_selected_type = selected_type
                st.session_state.bh_step = 2
                st.session_state.bh_selected_item = None
        
        # Step 2: Select Item Name
        if st.session_state.bh_step >= 2 and st.session_state.bh_selected_type:
            st.subheader("Step 2: Which specific item?")
            st.caption(f"Selected type: **{st.session_state.bh_selected_type}**")
            
            # Filter available items by selected type
            type_items = [item for item in available_items if item.get('item_type') == st.session_state.bh_selected_type]
            
            # Get unique item names for this type
            item_names = sorted(list(set(item.get('item_name', '') for item in type_items if item.get('item_name'))))
            
            selected_name = st.selectbox(
                "Choose item:",
                [""] + item_names,
                key="bh_name_select"
            )
            
            if selected_name:
                # Find the item with this name (BoxHero items should be unique by name within type)
                selected_item = next((item for item in type_items if item.get('item_name') == selected_name), None)
                
                if selected_item:
                    st.session_state.bh_selected_item = selected_item
                    st.session_state.bh_step = 3
                    st.success("✅ Item selected!")
        
        # Step 3: Project Selection, Quantity and Add to Cart
        if st.session_state.bh_step >= 3 and st.session_state.bh_selected_item:
            st.subheader("Step 3: Select Project and Quantity")
            
            # Just show the item name - simple
            st.info(f"Selected: **{st.session_state.bh_selected_item.get('item_name', 'Unknown Item')}**")
            
            # Project selection
            project_number, project_name, parent_project_id, sub_project_number = display_project_selector(db, "bh")
            
            # Date needed input (mandatory)
            date_needed = st.date_input(
                "📅 Date Needed *",
                value=date.today(),
                min_value=date.today(),
                help="When do you need this item delivered? (Required)",
                key="bh_date_needed"
            )
            
            # Quantity input
            col1, col2 = st.columns([2, 1])
            
            with col1:
                quantity = st.number_input(
                    "Quantity needed:",
                    min_value=1,
                    value=1,
                    key="bh_quantity"
                )
            
            with col2:
                # Only enable Add to Cart if project and date are selected
                if project_number and date_needed:
                    if st.button("🛒 Add to Cart", type="primary", key="bh_add_to_cart"):
                        result = add_to_cart(st.session_state.bh_selected_item, quantity, "BoxHero", project_number, project_name, parent_project_id, sub_project_number, date_needed, db)
                        if result == "added":
                            st.success("✅ Added to cart!")
                            # Reset flow for next selection
                            reset_boxhero_flow()
                            st.rerun()
                else:
                    st.button("🛒 Add to Cart", type="primary", disabled=True, key="bh_add_to_cart_disabled")
                    st.caption("⬆️ Please select a project first")
        
        # Reset button
        if st.session_state.bh_step > 1:
            st.markdown("---")
            if st.button("🔄 Start Over", key="bh_reset"):
                reset_boxhero_flow()
                st.rerun()
    
    except Exception as e:
        st.error(f"Error in BoxHero items selection: {str(e)}")

def display_selected_boxhero_details(item):
    """Display details of selected BoxHero item"""
    st.markdown("### 📋 Selected Item Details")
    
    # Item info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {item.get('item_name', 'N/A')}")
        st.write(f"**Type:** {item.get('item_type', 'N/A')}")
    
    with col2:
        st.write(f"**SKU:** {item.get('sku', 'N/A')}")
        st.write(f"**Barcode:** {item.get('barcode', 'N/A')}")

def reset_boxhero_flow():
    """Reset the BoxHero selection flow"""
    st.session_state.bh_step = 1
    st.session_state.bh_selected_type = None
    st.session_state.bh_selected_item = None

def display_raw_materials_tab(db):
    """Smart questionnaire flow for Raw Materials selection"""
    st.header("🔧 Raw Materials")
    st.caption("Select your material step by step")
    
    # Initialize session state for raw materials flow
    if 'rm_step' not in st.session_state:
        st.session_state.rm_step = 1
    if 'rm_selected_type' not in st.session_state:
        st.session_state.rm_selected_type = None
    if 'rm_selected_name' not in st.session_state:
        st.session_state.rm_selected_name = None
    if 'rm_selected_item' not in st.session_state:
        st.session_state.rm_selected_item = None
    
    try:
        # Get all raw materials with lightweight session cache (TTL ~60s)
        now_ts = time.time()
        cache_key = 'rm_items_cache'
        cache_ttl = 60
        if cache_key not in st.session_state or (now_ts - st.session_state[cache_key]['ts'] > cache_ttl):
            all_items = db.get_all_items(source_filter="Raw Materials")
            st.session_state[cache_key] = {'data': all_items or [], 'ts': now_ts}
        else:
            all_items = st.session_state[cache_key]['data']
        
        if not all_items:
            st.info("No raw materials available at the moment.")
            return
        
        # Use all items - duplicate check happens in add_to_cart()
        available_items = all_items
        
        # Step 1: Select Item Type
        if st.session_state.rm_step >= 1:
            st.subheader("Step 1: What type of material do you need?")
            
            # Get unique item types from available items only
            item_types = sorted(list(set(item.get('item_type', '') for item in available_items if item.get('item_type'))))
            
            selected_type = st.selectbox(
                "Choose material type:",
                [""] + item_types,
                index=0 if not st.session_state.rm_selected_type else item_types.index(st.session_state.rm_selected_type) + 1,
                key="rm_type_select"
            )
            
            if selected_type and selected_type != st.session_state.rm_selected_type:
                st.session_state.rm_selected_type = selected_type
                st.session_state.rm_step = 2
                st.session_state.rm_selected_name = None
                st.session_state.rm_selected_item = None
        
        # Step 2: Select Item Name
        if st.session_state.rm_step >= 2 and st.session_state.rm_selected_type:
            st.subheader("Step 2: Which specific material?")
            st.caption(f"Selected type: **{st.session_state.rm_selected_type}**")
            
            # Filter available items by selected type
            type_items = [item for item in available_items if item.get('item_type') == st.session_state.rm_selected_type]
            
            # Get unique item names for this type
            item_names = sorted(list(set(item.get('item_name', '') for item in type_items if item.get('item_name'))))
            
            selected_name = st.selectbox(
                "Choose material:",
                [""] + item_names,
                index=0 if not st.session_state.rm_selected_name else item_names.index(st.session_state.rm_selected_name) + 1,
                key="rm_name_select"
            )
            
            if selected_name and selected_name != st.session_state.rm_selected_name:
                st.session_state.rm_selected_name = selected_name
                st.session_state.rm_step = 3
                st.session_state.rm_selected_item = None
        
        # Step 3: Select Dimensions (if multiple variants exist)
        if st.session_state.rm_step >= 3 and st.session_state.rm_selected_name:
            st.subheader("Step 3: Select dimensions")
            st.caption(f"Selected material: **{st.session_state.rm_selected_name}**")
            
            # Filter available items by selected type and name
            name_items = [item for item in available_items if 
                         item.get('item_type') == st.session_state.rm_selected_type and 
                         item.get('item_name') == st.session_state.rm_selected_name]
            
            if len(name_items) == 1:
                # Only one variant - auto-select it
                st.session_state.rm_selected_item = name_items[0]
                st.session_state.rm_step = 4
                st.success("✅ Material selected!")
            else:
                # Multiple variants - let user choose with separate dimension fields
                st.info(f"Found {len(name_items)} variants with different dimensions:")
                
                # Display variants in a table format for better comparison
                st.write("**Available variants:**")
                
                # Create columns for the dimension table
                col_headers = st.columns([1, 2, 2, 2, 2])
                with col_headers[0]:
                    st.write("**Select**")
                with col_headers[1]:
                    st.write("**Height**")
                with col_headers[2]:
                    st.write("**Width**")
                with col_headers[3]:
                    st.write("**Thickness**")
                with col_headers[4]:
                    st.write("**Action**")
                
                # Display each variant as a row
                for idx, item in enumerate(name_items):
                    cols = st.columns([1, 2, 2, 2, 2])
                    
                    with cols[0]:
                        st.write(f"#{idx + 1}")
                    
                    with cols[1]:
                        height = fmt_dim(item.get('height'))
                        st.write(height if height else "N/A")
                    
                    with cols[2]:
                        width = fmt_dim(item.get('width'))
                        st.write(width if width else "N/A")
                    
                    with cols[3]:
                        thickness = fmt_dim(item.get('thickness'))
                        st.write(thickness if thickness else "N/A")
                    
                    with cols[4]:
                        if st.button(f"Select", key=f"select_variant_{idx}"):
                            st.session_state.rm_selected_item = item
                            st.session_state.rm_step = 4
        
        # Step 4: Project Selection, Quantity and Add to Cart
        if st.session_state.rm_step >= 4 and st.session_state.rm_selected_item:
            st.subheader("Step 4: Select Project and Quantity")
            
            # Just show the material name - simple
            sel = st.session_state.rm_selected_item
            dims = []
            h = fmt_dim(sel.get('height'))
            w = fmt_dim(sel.get('width'))
            t = fmt_dim(sel.get('thickness'))
            if h: dims.append(h)
            if w: dims.append(w)
            if t: dims.append(t)
            dim_txt = f" ({' x '.join(dims)})" if dims else ""
            st.info(f"Selected: **{sel.get('item_name', 'Unknown Material')}**{dim_txt}")
            
            # Project selection
            project_number, project_name, parent_project_id, sub_project_number = display_project_selector(db, "rm")
            
            # Date needed input (mandatory)
            date_needed = st.date_input(
                "📅 Date Needed *",
                value=date.today(),
                min_value=date.today(),
                help="When do you need this item delivered? (Required)",
                key="rm_date_needed"
            )
            
            # Quantity input
            col1, col2 = st.columns([2, 1])
            
            with col1:
                quantity = st.number_input(
                    "Quantity needed:",
                    min_value=1,
                    value=1,
                    key="rm_quantity"
                )
            
            with col2:
                # Only enable Add to Cart if project and date are selected
                if project_number and date_needed:
                    if st.button("🛒 Add to Cart", type="primary", key="rm_add_to_cart"):
                        result = add_to_cart(st.session_state.rm_selected_item, quantity, "Raw Materials", project_number, project_name, parent_project_id, sub_project_number, date_needed, db)
                        if result == "added":
                            st.success("✅ Added to cart!")
                            # Reset flow for next selection
                            reset_raw_materials_flow()
                            st.rerun()
                else:
                    st.button("🛒 Add to Cart", type="primary", disabled=True, key="rm_add_to_cart_disabled")
                    st.caption("⬆️ Please select a project first")
        
        # Reset button
        if st.session_state.rm_step > 1:
            st.markdown("---")
            if st.button("🔄 Start Over", key="rm_reset"):
                reset_raw_materials_flow()
                st.rerun()
    
    except Exception as e:
        st.error(f"Error in raw materials selection: {str(e)}")

def display_selected_material_details(item):
    """Display details of selected material with separate dimension fields"""
    st.markdown("### 📋 Selected Material Details")
    
    # Material info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {item.get('item_name', 'N/A')}")
        st.write(f"**Type:** {item.get('item_type', 'N/A')}")
    
    with col2:
        st.write(f"**Item ID:** {item.get('item_id', 'N/A')}")
        st.write(f"**Source:** {item.get('source_sheet', 'N/A')}")
    
    # Dimensions in separate fields
    st.markdown("**Dimensions:**")
    dim_col1, dim_col2, dim_col3 = st.columns(3)
    
    with dim_col1:
        height = fmt_dim(item.get('height'))
        st.metric("Height", height if height else "Not specified")
    
    with dim_col2:
        width = fmt_dim(item.get('width'))
        st.metric("Width", width if width else "Not specified")
    
    with dim_col3:
        thickness = fmt_dim(item.get('thickness'))
        st.metric("Thickness", thickness if thickness else "Not specified")

def reset_raw_materials_flow():
    """Reset the raw materials selection flow"""
    st.session_state.rm_step = 1
    st.session_state.rm_selected_type = None
    st.session_state.rm_selected_name = None
    st.session_state.rm_selected_item = None

def display_item_card(item, col, category):
    """Display individual item card in marketplace style"""
    with col:
        # Create a card-like container
        with st.container():
            st.markdown(f"**{item.get('item_name', 'Unknown Item')}**")
            
            # Item details
            if item.get('sku'):
                st.caption(f"SKU: {item['sku']}")
            
            if item.get('item_type'):
                st.caption(f"Type: {item['item_type']}")
            
            # Dimensions if available (formatted)
            dimensions = []
            h = fmt_dim(item.get('height'))
            w = fmt_dim(item.get('width'))
            t = fmt_dim(item.get('thickness'))
            if h: dimensions.append(f"H: {h}")
            if w: dimensions.append(f"W: {w}")
            if t: dimensions.append(f"T: {t}")
            
            if dimensions:
                st.caption(f"Size: {' × '.join(dimensions)}")
            
            # Quantity input and Add to Cart
            col1, col2 = st.columns([2, 1])
            
            with col1:
                quantity = st.number_input(
                    "Qty", 
                    min_value=1, 
                    value=1, 
                    key=f"qty_{item['item_id']}_{category}"
                )
            
            with col2:
                if st.button("Add", key=f"add_{item['item_id']}_{category}", type="primary"):
                    add_to_cart(item, quantity, category)
                    st.success("Added!")
                    st.rerun()
        
        st.markdown("---")

def display_project_selector(db, key_suffix=""):
    """
    Reusable project dropdown - returns (project_number, project_name, parent_project_id, sub_project_number).
    For letter-based projects (CP-2025, BCHS 2025, etc.), asks for sub-project number.
    Returns:
        - Regular projects: (project_number, project_name, None, None)
        - Letter-based: (parent_project, project_name, parent_project, sub_project_number)
    """
    try:
        projects = db.get_all_projects()
        if not projects:
            st.warning("⚠️ No projects available. Please contact your administrator.")
            return None, None, None, None
        
        # Build dropdown options: Show only ProjectNumber
        options_dict = {}
        for p in projects:
            options_dict[p['ProjectNumber']] = {
                'number': p['ProjectNumber'],
                'name': p['ProjectName'],
                'type': p.get('ProjectType', 'N/A')
            }
        
        selected = st.selectbox(
            "Select Project Number:",
            ["-- Select a project --"] + list(options_dict.keys()),
            key=f"project_select_{key_suffix}"
        )
        
        if selected and selected != "-- Select a project --":
            project_info = options_dict[selected]
            parent_project = project_info['number']
            
            # Check if project starts with letter (letter-based project)
            if parent_project and parent_project[0].isalpha():
                # Letter-based project - need sub-project number
                st.info(f"📋 **{parent_project}** - {project_info['name']} ({project_info['type']}) requires a project number")
                
                # Get previously used sub-projects
                previous_subs = db.get_previous_sub_projects(parent_project)
                
                if previous_subs:
                    # Show dropdown with previous + new option
                    sub_options = previous_subs + ["+ Enter new number"]
                    selected_sub = st.selectbox(
                        f"Select or enter project number for {parent_project}:",
                        sub_options,
                        key=f"sub_project_select_{key_suffix}"
                    )
                    
                    if selected_sub == "+ Enter new number":
                        # Show text input for new number
                        sub_project = st.text_input(
                            f"Enter project number for {parent_project}:",
                            placeholder="e.g., 25-3456",
                            key=f"sub_project_input_{key_suffix}"
                        )
                    else:
                        # Use selected previous sub-project
                        sub_project = selected_sub
                else:
                    # No previous sub-projects, show text input directly
                    sub_project = st.text_input(
                        f"Enter project number for {parent_project}:",
                        placeholder="e.g., 25-3456",
                        key=f"sub_project_input_{key_suffix}"
                    )
                
                if sub_project and sub_project.strip():
                    # Return: (parent_project, project_name, parent_project_id, sub_project_number)
                    st.success(f"✓ Project: {parent_project} ({sub_project.strip()}) - {project_info['name']} ({project_info['type']})")
                    return parent_project, project_info['name'], parent_project, sub_project.strip()
                else:
                    # Sub-project not entered yet
                    return None, None, None, None
            else:
                # Regular number-based project
                st.success(f"✓ Project: {parent_project} - {project_info['name']} ({project_info['type']})")
                return parent_project, project_info['name'], None, None
        
        return None, None, None, None
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
        return None, None, None, None

def format_project_display(project_number, sub_project_number=None):
    """
    Format project number for display.
    If sub_project_number exists, returns "parent (sub)".
    Otherwise returns project_number as-is.
    """
    if sub_project_number:
        return f"{project_number} ({sub_project_number})"
    return project_number

def add_to_cart(item, quantity, category, project_number=None, project_name=None, parent_project_id=None, sub_project_number=None, date_needed=None, db=None):
    """Add item to cart with project info and required date needed"""
    try:
        # Check if user already has this item+project in pending or locked status
        if 'user_id' in st.session_state and db:
            
            # Check 1: Pending requests (show warning, suggest edit)
            pending_items = db.get_user_pending_items(st.session_state.user_id)
            for pending in pending_items:
                # Check if same item + same project (including sub-project)
                if (pending['item_id'] == item['item_id'] and 
                    pending['project_number'] == project_number and
                    pending.get('sub_project_number') == sub_project_number):
                    
                    # Show warning
                    formatted_project = format_project_display(project_number, sub_project_number)
                    st.warning(f"⚠️ **You already have this item for this project in a pending request!**")
                    st.info(f"📋 **{pending['item_name']}** - Project: {formatted_project}")
                    st.info(f"Current quantity in **{pending['req_number']}**: {pending['quantity']} pieces")
                    st.info("💡 Go to **'My Requests'** tab to edit the quantity instead of creating a duplicate.")
                    return "duplicate"
            
            # Check 2: Locked items (In Progress/Ordered) - block completely
            locked_items = db.get_locked_item_project_pairs(st.session_state.user_id)
            for locked in locked_items:
                # Check if same item + same project (including sub-project)
                if (locked['item_id'] == item['item_id'] and 
                    locked['project_number'] == project_number and
                    locked.get('sub_project_number') == sub_project_number):
                    
                    # Block with error message
                    formatted_project = format_project_display(project_number, sub_project_number)
                    st.error(f"❌ **This item is already being processed for this project!**")
                    st.info(f"📋 **{locked['item_name']}** - Project: {formatted_project}")
                    st.info(f"Request: **{locked['req_number']}** - Status: **{locked['status']}**")
                    st.info("⏳ Please wait for the current order to complete before requesting this item again.")
                    return "blocked"
        
        # Check if item already in current cart with same project
        for cart_item in st.session_state.cart_items:
            if (cart_item['item_id'] == item['item_id'] and 
                cart_item.get('project_number') == project_number):
                # Update quantity if same item and same project
                cart_item['quantity'] += quantity
                return "added"
        
        # Add new item to cart
        cart_item = {
            'item_id': item['item_id'],
            'item_name': item.get('item_name', 'Unknown Item'),
            'sku': item.get('sku', ''),
            'category': category,
            'quantity': quantity,
            'item_type': item.get('item_type', ''),
            # Include dimensions if present so Cart and downstream screens can render them
            'height': item.get('height'),
            'width': item.get('width'),
            'thickness': item.get('thickness'),
            'source_sheet': item.get('source_sheet', ''),
            'project_number': project_number,
            'project_name': project_name,
            'parent_project_id': parent_project_id,
            'sub_project_number': sub_project_number,
            'date_needed': date_needed
        }
        
        st.session_state.cart_items.append(cart_item)
        return "added"
        
    except Exception as e:
        st.error(f"Error adding to cart: {str(e)}")
        return "error"

def display_cart_tab(db):
    """Display shopping cart"""
    st.header("🛒 My Cart")
    
    if not st.session_state.cart_items:
        st.info("Your cart is empty. Browse items and add them to your cart!")
        return
    
    st.write(f"You have {len(st.session_state.cart_items)} different items in your cart")
    
    # Display cart items
    total_items = 0
    for i, cart_item in enumerate(st.session_state.cart_items):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            st.write(f"**{cart_item['item_name']}**")
            st.caption(f"{cart_item['category']} • SKU: {cart_item.get('sku', 'N/A')}")
            # Project info
            if cart_item.get('project_number'):
                formatted_project = format_project_display(cart_item['project_number'], cart_item.get('sub_project_number'))
                st.caption(f"📋 Project: {formatted_project} - {cart_item.get('project_name', 'N/A')}")
            # Date needed
            if cart_item.get('date_needed'):
                st.caption(f"📅 Needed: {cart_item['date_needed']}")
            # Dimensions if available
            dims = []
            h = fmt_dim(cart_item.get('height'))
            w = fmt_dim(cart_item.get('width'))
            t = fmt_dim(cart_item.get('thickness'))
            if h: dims.append(f"H: {h}")
            if w: dims.append(f"W: {w}")
            if t: dims.append(f"T: {t}")
            if dims:
                st.caption(f"Size: {' × '.join(dims)}")
        
        with col2:
            # Editable quantity
            new_qty = st.number_input(
                "Qty", 
                min_value=1, 
                value=cart_item['quantity'],
                key=f"cart_qty_{i}"
            )
            if new_qty != cart_item['quantity']:
                st.session_state.cart_items[i]['quantity'] = new_qty
                st.rerun()
            st.caption(f"Current quantity: {cart_item['quantity']}")
            total_items += cart_item['quantity']
        
        with col3:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.cart_items.pop(i)
                st.rerun()
        
        st.markdown("---")
    
    # Cart summary
    st.subheader("📊 Cart Summary")
    
    # Summary metrics in clean layout
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("Total Items", f"{len(st.session_state.cart_items)} types")
    with metric_col2:
        st.metric("Total Quantity", f"{total_items} pieces")
    
    st.markdown("---")
    
    # Notes section - always visible
    st.markdown("### 📝 Notes for Operator")
    st.caption("💡 Optional - Add special instructions, vendor preferences, or urgency details")
    
    user_notes = st.text_area(
        "Your Notes:",
        value="",
        max_chars=1000,
        height=90,
        placeholder="Example:\n• Please use Master NY vendor\n• Urgent - needed by Friday\n• Contact me if any issues",
        help="Optional notes for the procurement team (max 1000 characters)",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Action buttons
    col_clear, col_submit = st.columns([1, 2])
    
    with col_clear:
        if st.button("🗑️ Clear Cart", type="secondary", use_container_width=True):
            st.session_state.cart_items = []
            st.rerun()
    
    with col_submit:
        if st.button("✅ Submit Request", type="primary", use_container_width=True):
            if submit_cart_as_request(db, user_notes=user_notes):
                st.success("🎉 Request submitted successfully!")
                st.balloons()
                st.session_state.cart_items = []
                st.rerun()

def display_my_requests_tab(db):
    """Display user's past requests and their status - organized by status"""
    st.header("📋 My Requests")
    st.caption("View your submitted requests and their current status")
    
    # Help section - collapsible
    with st.expander("ℹ️ **How Request Status Works** - Click to learn more", expanded=False):
        st.markdown("""
        ### 📊 **Status Meanings**
        
        | Status | What It Means | What You Can Do |
        |--------|---------------|-----------------|
        | 🟡 **Pending** | Your request is waiting to be processed | ✏️ Edit quantities or cancel |
        | 🔵 **In Progress** | Your items are being prepared for ordering | ⏳ Wait - team is working on it |
        | ✅ **Ordered** | Order placed with supplier | 📦 Items will arrive soon |
        | 🎉 **Completed** | Items received and available | ✅ You can request this item again |
        
        ---
        
        ### 🚫 **Why Can't I Request the Same Item Again?**
        
        **Rule:** You cannot request an item that's already **Pending** or **In Progress**.
        
        **Reason:** We group requests together to save costs. If you need more of the same item:
        - **If Pending:** Edit the quantity in your existing request
        - **If In Progress:** Wait for completion, then submit a new request
        - **If Completed:** You can freely request it again
        
        ---
        
        ### 💡 **Quick Tips**
        - **Pending requests** can be edited anytime before processing (Tue/Thu 10 AM)
        - **In Progress** means processing started - no changes allowed
        - **Completed items** are available - request them anytime
        - Check this tab regularly to track your order progress
        """)
    
    st.markdown("---")
    
    try:
        # Get user's requests from database
        user_requests = get_user_requests(db, st.session_state.user_id)
        
        if not user_requests:
            st.info("You haven't submitted any requests yet. Browse items and add them to your cart to get started!")
            return
        
        # Group requests by status
        requests_by_status = {
            'Pending': [],
            'In Progress': [],
            'Ordered': [],
            'Completed': []
        }
        
        for request in user_requests:
            status = request.get('status', 'Pending')
            if status in requests_by_status:
                requests_by_status[status].append(request)
        
        # Count requests per status
        pending_count = len(requests_by_status['Pending'])
        in_progress_count = len(requests_by_status['In Progress'])
        ordered_count = len(requests_by_status['Ordered'])
        completed_count = len(requests_by_status['Completed'])
        
        # Create status tabs
        tabs = st.tabs([
            f"🟡 Pending ({pending_count})",
            f"🔵 In Progress ({in_progress_count})",
            f"✅ Ordered ({ordered_count})",
            f"🎉 Completed ({completed_count})"
        ])
        
        # Display requests for each status
        status_list = ['Pending', 'In Progress', 'Ordered', 'Completed']
        
        for idx, status in enumerate(status_list):
            with tabs[idx]:
                requests = requests_by_status[status]
                
                if not requests:
                    if status == 'Pending':
                        st.info("No pending requests. All your requests have been processed!")
                    elif status == 'In Progress':
                        st.info("No requests in progress.")
                    elif status == 'Ordered':
                        st.info("No ordered requests. Check 'In Progress' or 'Completed' tabs.")
                    else:
                        st.info("No completed requests yet.")
                    continue
                
                st.write(f"**Showing: {len(requests)} {status} Request{'s' if len(requests) != 1 else ''}**")
                st.markdown("---")
                
                # Display each request as an expander
                for request in requests:
                    # Format date nicely
                    req_date = request.get('req_date', 'Unknown')
                    if hasattr(req_date, 'strftime'):
                        formatted_date = req_date.strftime('%Y-%m-%d %H:%M')
                    else:
                        formatted_date = str(req_date)
                    
                    with st.expander(f"📋 {request['req_number']} - {status}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Request Date:** {formatted_date}")
                            st.write(f"**Total Items:** {request['total_items']} pieces")
                        
                        with col2:
                            st.write(f"**Request ID:** {request['req_id']}")
                            if request.get('user_notes'):
                                st.write(f"**Notes:** {request['user_notes']}")
                        
                        # Show items in this request
                        request_items = get_request_items(db, request['req_id'])
                        if request_items:
                            st.write("**Your Items:**")
                            for item in request_items:
                                # Build item description with dimensions for Raw Materials
                                item_desc = f"• **{item['item_name']}**"
                                
                                # Add dimensions for Raw Materials (formatted)
                                if item.get('source_sheet') == 'Raw Materials':
                                    dimensions = []
                                    h = fmt_dim(item.get('height'))
                                    w = fmt_dim(item.get('width'))
                                    t = fmt_dim(item.get('thickness'))
                                    if h: dimensions.append(f"H: {h}")
                                    if w: dimensions.append(f"W: {w}")
                                    if t: dimensions.append(f"T: {t}")
                                    if dimensions:
                                        dim_str = " × ".join(dimensions)
                                        item_desc += f" ({dim_str})"
                        
                                # Add SKU for BoxHero items
                                elif item.get('source_sheet') == 'BoxHero' and item.get('sku'):
                                    item_desc += f" (SKU: {item['sku']})"
                        
                                # Add project info if available
                                if item.get('project_number'):
                                    formatted_project = format_project_display(item['project_number'], item.get('sub_project_number'))
                                    item_desc += f" | 📋 Project: {formatted_project}"
                                
                                # Add date needed if available
                                if item.get('date_needed'):
                                    item_desc += f" | 📅 Needed: {item['date_needed']}"
                        
                                # Show quantity with edit option for pending requests
                                if request['status'] == 'Pending':
                                    col_item, col_qty, col_btn, col_del = st.columns([3, 1, 1, 0.5])
                                    with col_item:
                                        st.write(item_desc)
                                    with col_qty:
                                        new_qty = st.number_input(
                                            "Qty", 
                                            min_value=1, 
                                            value=item['quantity'], 
                                            key=f"qty_{request['req_id']}_{item['item_id']}"
                                        )
                                    with col_btn:
                                        if new_qty != item['quantity']:
                                            if st.button("Update", key=f"update_{request['req_id']}_{item['item_id']}"):
                                                try:
                                                    success = db.update_order_item_quantity(request['req_id'], item['item_id'], new_qty)
                                                    if success:
                                                        st.success("✅ Updated!")
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Failed to update")
                                                except Exception as e:
                                                    st.error(f"❌ Error: {str(e)}")
                                    with col_del:
                                        if st.button("🗑️", key=f"delete_{request['req_id']}_{item['item_id']}", help="Delete this item"):
                                            try:
                                                result = db.delete_order_item(request['req_id'], item['item_id'])
                                                if result == "request_deleted":
                                                    st.success("✅ Last item deleted. Request removed.")
                                                else:
                                                    st.success("✅ Item deleted!")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"❌ Error: {str(e)}")
                                else:
                                    # For non-pending requests, just show the quantity
                                    item_desc += f" - {item['quantity']} pieces"
                                    st.write(item_desc)
                        else:
                            st.write("*No items found for this request*")
                        
                        # Delete entire request button for pending requests
                        if request['status'] == 'Pending':
                            st.markdown("---")
                            col1, col2, col3 = st.columns([2, 1, 2])
                            with col2:
                                if st.button("🗑️ Delete This Request", key=f"delete_req_{request['req_id']}", type="secondary"):
                                    try:
                                        success = db.delete_request(request['req_id'])
                                        if success:
                                            st.success("✅ Request deleted!")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                
                        # Show order information for non-pending requests (simplified for users)
                        if request['status'] != 'Pending':
                            bundles_query = """
                            SELECT DISTINCT
                                b.bundle_id,
                                b.status,
                                b.po_number,
                                b.po_date,
                                b.expected_delivery_date,
                                b.actual_delivery_date
                            FROM requirements_bundle_mapping rbm
                            JOIN requirements_bundles b ON rbm.bundle_id = b.bundle_id
                            WHERE rbm.req_id = ?
                            ORDER BY b.bundle_id
                            """
                            bundles = db.execute_query(bundles_query, (request['req_id'],))
                            
                            if bundles:
                                st.markdown("---")
                                st.write("**📦 Order Status**")
                                
                                # Count ordered and completed bundles
                                ordered_count_bundle = sum(1 for b in bundles if b['status'] in ('Ordered', 'Completed'))
                                completed_count_bundle = sum(1 for b in bundles if b['status'] == 'Completed')
                                total_count_bundle = len(bundles)
                                
                                # Show status message
                                if completed_count_bundle == total_count_bundle:
                                    st.success(f"🎉 Completed ({completed_count_bundle} of {total_count_bundle} items)")
                                elif ordered_count_bundle == total_count_bundle:
                                    st.info(f"✅ All Ordered ({ordered_count_bundle} of {total_count_bundle} items)")
                                elif ordered_count_bundle > 0:
                                    st.info(f"🔵 In Progress ({ordered_count_bundle} of {total_count_bundle} items ordered)")
                                else:
                                    st.caption("⏳ Processing...")
                                
                                # Separate ordered and processing items
                                ordered_bundles = [b for b in bundles if b['status'] in ('Ordered', 'Completed')]
                                processing_bundles = [b for b in bundles if b['status'] not in ('Ordered', 'Completed')]
                                
                                # Show ordered items
                                if ordered_bundles:
                                    if completed_count_bundle == total_count_bundle:
                                        st.write("**✅ Delivered:**")
                                    else:
                                        st.write("**✅ Ordered:**")
                                    
                                    for bundle in ordered_bundles:
                                        # Get items in this bundle
                                        bundle_items_query = """
                                        SELECT DISTINCT i.item_name, roi.quantity
                                        FROM requirements_order_items roi
                                        JOIN Items i ON roi.item_id = i.item_id
                                        JOIN requirements_bundle_items bi ON roi.item_id = bi.item_id
                                        WHERE roi.req_id = ? AND bi.bundle_id = ?
                                        """
                                        bundle_items = db.execute_query(bundle_items_query, (request['req_id'], bundle['bundle_id']))
                                        
                                        # Show items
                                        for item in bundle_items or []:
                                            st.write(f"   • {item['item_name']} ({item['quantity']} pcs)")
                                        
                                        # Show PO info
                                        if bundle.get('po_number'):
                                            po_date = ""
                                            if bundle.get('po_date'):
                                                po_date = bundle['po_date'].strftime('%B %d, %Y') if hasattr(bundle['po_date'], 'strftime') else str(bundle['po_date'])[:10]
                                            st.caption(f"     📋 PO#: {bundle['po_number']} | 📅 Order Date: {po_date}")
                                            
                                            # Show delivery dates based on status
                                            if bundle['status'] == 'Completed' and bundle.get('actual_delivery_date'):
                                                # Completed: Show actual delivery date
                                                delivery_date = bundle['actual_delivery_date'].strftime('%B %d, %Y') if hasattr(bundle['actual_delivery_date'], 'strftime') else str(bundle['actual_delivery_date'])[:10]
                                                st.caption(f"     ✅ Delivered: {delivery_date}")
                                            elif bundle.get('expected_delivery_date'):
                                                # Ordered: Show expected delivery date
                                                delivery_date = bundle['expected_delivery_date'].strftime('%B %d, %Y') if hasattr(bundle['expected_delivery_date'], 'strftime') else str(bundle['expected_delivery_date'])[:10]
                                                st.caption(f"     🚚 Expected Delivery: {delivery_date}")
                                    
                                    st.write("")
                                
                                # Show processing items
                                if processing_bundles:
                                    st.write("**⏳ Processing:**")
                                    
                                    for bundle in processing_bundles:
                                        # Get items in this bundle
                                        bundle_items_query = """
                                        SELECT DISTINCT i.item_name, roi.quantity
                                        FROM requirements_order_items roi
                                        JOIN Items i ON roi.item_id = i.item_id
                                        JOIN requirements_bundle_items bi ON roi.item_id = bi.item_id
                                        WHERE roi.req_id = ? AND bi.bundle_id = ?
                                        """
                                        bundle_items = db.execute_query(bundle_items_query, (request['req_id'], bundle['bundle_id']))
                                        
                                        # Show items
                                        for item in bundle_items or []:
                                            st.write(f"   • {item['item_name']} ({item['quantity']} pcs)")
    
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")

def get_status_badge(status):
    """Return colored status badge"""
    if status == "Pending":
        return "🟡 Pending"
    elif status == "In Progress":
        return "🔵 In Progress"
    elif status == "Completed":
        return "🟢 Completed"
    else:
        return f"⚪ {status}"

def get_user_requests(db, user_id):
    """Get all requests for a user"""
    query = """
    SELECT req_id, req_number, req_date, status, total_items, user_notes
    FROM requirements_orders 
    WHERE user_id = ?
    ORDER BY req_date DESC
    """
    return db.execute_query(query, (user_id,))

def get_request_items(db, req_id):
    """Get items for a specific request with dimensions"""
    query = """
    SELECT ri.quantity, ri.item_notes, ri.project_number, ri.sub_project_number, ri.date_needed,
           i.item_id, i.item_name, i.sku, i.source_sheet,
           i.height, i.width, i.thickness, i.item_type
    FROM requirements_order_items ri
    JOIN items i ON ri.item_id = i.item_id
    WHERE ri.req_id = ?
    """
    return db.execute_query(query, (req_id,))

def submit_cart_as_request(db, user_notes=""):
    """Submit cart items as a requirement request to database"""
    try:
        # Get cart items and user info
        cart_items = st.session_state.cart_items
        user_id = st.session_state.user_id
        
        if not cart_items:
            st.error("Cart is empty!")
            return False
        
        if not user_id:
            st.error("User not logged in!")
            return False
        
        # Submit to database with notes
        result = db.submit_cart_as_order(user_id, cart_items, user_notes=user_notes)
        
        if result['success']:
            # Show success message with request details
            st.success(f"🎉 Request submitted successfully!")
            st.info(f"**Request Number:** {result['req_number']}")
            st.info(f"**Total Items:** {result['total_items']} pieces")
            st.info("**Status:** Pending - You can track this in 'My Requests' tab")
            return True
        else:
            st.error(f"Failed to submit request: {result['error']}")
            return False
            
    except Exception as e:
        st.error(f"Error submitting request: {str(e)}")
        return False

def display_operation_team_dashboard(db):
    """Operation Team Dashboard - Load from separate module"""
    try:
        import operation_team_dashboard
        operation_team_dashboard.main(db)  # Pass the database connection
    except Exception as e:
        st.error(f"❌ Error loading Operation Team Dashboard: {str(e)}")
        st.info("Please ensure operation_team_dashboard.py exists in the Phase3 directory.")
        import traceback
        st.code(traceback.format_exc())

def display_operator_dashboard(db):
    """Operator Dashboard integrated into main app"""
    st.title("⚙️ Operator Dashboard")
    st.caption("Bundle Management for Procurement Team")
    
    # Sidebar for operator navigation
    with st.sidebar:
        st.markdown("**Operator Dashboard**")
        st.markdown(f"*Logged in as: {st.session_state.user_role}*")
        st.markdown(f"*User: {st.session_state.username}*")
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
        
        st.markdown("---")
        
        # Database connection status (sidebar only)
        st.subheader("Database")
        is_connected, message, connection_details, error_info = db.check_db_connection()
        if is_connected:
            st.success("Connected")
        else:
            st.error("Connection Failed")
            with st.expander("Error Details"):
                st.write(message)

    # Main content (outside sidebar)
    if not is_connected:
        st.error("Database connection is not available. Please check settings.")
        return

    # Allow 'Operator', 'Admin', and 'Master' roles, case-insensitive
    role_val = str(st.session_state.get('user_role') or '').lower()
    if role_val not in ('operator', 'admin', 'master'):
        display_user_interface(db)
        return

    st.header("🎯 Operator Dashboard")
    st.write("Smart Procurement Management")

    # Role-based tabs: Master sees admin tools; Operator/Admin see only operational tabs
    # Note: Smart Recommendations removed - bundles created automatically by cron job
    if role_val == 'master':
        tabs = st.tabs(["📋 User Requests", "📦 Active Bundles", "📊 Analytics", "🤖 Manual Bundling", "🧹 System Reset", "👤 User Management"])
        with tabs[0]:
            display_user_requests_for_operator(db)
        with tabs[1]:
            display_active_bundles_for_operator(db)
        with tabs[2]:
            display_analytics_dashboard(db)
        with tabs[3]:
            display_manual_bundling(db)
        with tabs[4]:
            display_system_reset(db)
        with tabs[5]:
            display_user_management_admin(db)
    else:
        tabs = st.tabs(["📋 User Requests", "📦 Active Bundles", "📊 Analytics"])
        with tabs[0]:
            display_user_requests_for_operator(db)
        with tabs[1]:
            display_active_bundles_for_operator(db)
        with tabs[2]:
            display_analytics_dashboard(db)

def display_user_requests_for_operator(db):
    """Show all user requests in a clean, operator-friendly format"""
    st.header("📋 User Requests Overview")
    st.write("See what users have requested and need to be ordered")
    
    try:
        # Get all pending requests with user details
        pending_requests = db.get_all_pending_requests()
        
        if not pending_requests:
            st.info("✅ No pending requests - all caught up!")
            return
        
        # Separate user requests from BoxHero requests
        user_requests = []
        boxhero_requests = []
        
        for req in pending_requests:
            # Check if this is BoxHero request (user_id = 5)
            if req['user_id'] == 5:
                boxhero_requests.append(req)
            else:
                user_requests.append(req)
        
        # Group user requests by user and request
        requests_by_user = {}
        for req in user_requests:
            user_key = f"{req['user_id']} - {req['req_number']}"
            if user_key not in requests_by_user:
                # Get user display name (prefer full_name, fallback to username)
                user_display = req.get('full_name') or req.get('username') or f"User {req['user_id']}"
                requests_by_user[user_key] = {
                    'user_id': req['user_id'],
                    'user_name': user_display,
                    'req_number': req['req_number'],
                    'req_date': req['req_date'],
                    'items': [],
                    'total_pieces': 0
                }
            requests_by_user[user_key]['items'].append({
                'item_name': req['item_name'],
                'quantity': req['quantity'],
                'source_sheet': req['source_sheet'],
                'project_number': req.get('project_number'),
                'parent_project_id': req.get('parent_project_id'),
                'sub_project_number': req.get('sub_project_number'),
                'date_needed': req.get('date_needed')
            })
            requests_by_user[user_key]['total_pieces'] += req['quantity']
        
        # Group BoxHero requests
        boxhero_by_request = {}
        for req in boxhero_requests:
            req_key = req['req_number']
            if req_key not in boxhero_by_request:
                boxhero_by_request[req_key] = {
                    'req_number': req['req_number'],
                    'req_date': req['req_date'],
                    'items': [],
                    'total_pieces': 0
                }
            boxhero_by_request[req_key]['items'].append({
                'item_name': req['item_name'],
                'quantity': req['quantity'],
                'source_sheet': req['source_sheet']
            })
            boxhero_by_request[req_key]['total_pieces'] += req['quantity']
        
        # Summary
        total_user_items = len(user_requests)
        total_boxhero_items = len(boxhero_requests)
        st.write(f"**📊 Summary: {len(requests_by_user)} user requests ({total_user_items} items) + {len(boxhero_by_request)} BoxHero requests ({total_boxhero_items} items)**")
        
        # Display user requests
        if requests_by_user:
            st.subheader("👤 User Requests")
            for user_key, req_data in requests_by_user.items():
                with st.expander(f"👤 {req_data['user_name']} - {req_data['req_number']} ({req_data['total_pieces']} pieces total)", expanded=True):
                    st.write(f"**Request Date:** {req_data['req_date']}")
                    st.write(f"**Items Requested:**")
                    
                    # Create a clean table of items
                    for i, item in enumerate(req_data['items'], 1):
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                        with col1:
                            st.write(f"{i}. **{item['item_name']}**")
                        with col2:
                            st.write(f"**{item['quantity']} pieces**")
                        with col3:
                            st.write(f"*{item['source_sheet']}*")
                        with col4:
                            if item.get('project_number'):
                                formatted_project = format_project_display(item['project_number'], item.get('sub_project_number'))
                                st.write(f"📋 {formatted_project}")
                            else:
                                st.write("—")
                        with col5:
                            if item.get('date_needed'):
                                st.write(f"📅 {item['date_needed']}")
                            else:
                                st.write("—")
        
        # Display BoxHero requests separately
        if boxhero_by_request:
            st.markdown("---")
            st.subheader("📦 BoxHero Inventory Restock")
            st.info("⚠️ These items are automatically generated based on inventory levels falling below threshold")
            
            for req_key, req_data in boxhero_by_request.items():
                with st.expander(f"📦 {req_data['req_number']} - BoxHero Auto-Restock ({req_data['total_pieces']} pieces total)", expanded=True):
                    st.write(f"**Generated Date:** {req_data['req_date']}")
                    st.warning("🔄 **Automatic Restock Request** - Items below reorder threshold")
                    st.write(f"**Items Needing Restock:**")
                    
                    # Create a clean table of items
                    for i, item in enumerate(req_data['items'], 1):
                        col1, col2, col3 = st.columns([4, 1, 1])
                        with col1:
                            st.write(f"{i}. **{item['item_name']}**")
                        with col2:
                            st.write(f"**{item['quantity']} pieces**")
                        with col3:
                            st.write(f"*{item['source_sheet']}*")
        
        st.markdown("---")
        st.info("💡 **Next Step:** Bundles will be created automatically by the system. Check 'Active Bundles' tab to manage them.")
        
    except Exception as e:
        st.error(f"Error loading user requests: {str(e)}")

def display_smart_recommendations(db):
    """Show smart bundling recommendations in operator-friendly format"""
    st.header("🎯 Smart Bundling Recommendations")
    st.write("AI-powered vendor recommendations for maximum efficiency")
    
    try:
        # Check if there are pending requests
        pending_requests = db.get_all_pending_requests()
        
        if not pending_requests:
            st.info("No pending requests to bundle.")
            return
        
        st.success(f"Found {len(pending_requests)} items across multiple users ready for bundling!")
        
        # Show bundling button
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🚀 Generate Smart Recommendations", type="primary", use_container_width=True):
                with st.spinner("Analyzing items and vendors..."):
                    from bundling_engine import SmartBundlingEngine
                    engine = SmartBundlingEngine()
                    result = engine.run_bundling_process()
                    
                    if result['success']:
                        st.success("🎉 Smart bundling analysis complete!")
                        
                        # Show the enhanced debug info in operator-friendly format
                        debug_info = result.get('debug_info', {})
                        if debug_info:
                            st.markdown("---")
                            st.subheader("📋 **RECOMMENDED VENDOR STRATEGY**")
                            
                            # Show bundle recommendations
                            if 'coverage_strategy' in debug_info:
                                st.write("**🎯 Here's what you should order:**")
                                
                                for i, strategy in enumerate(debug_info['coverage_strategy'], 1):
                                    with st.container():
                                        st.markdown(f"### 📦 Order #{i}: Contact **{strategy['vendor_name']}**")
                                        
                                        # Vendor contact info prominently displayed
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"📧 **Email:** {strategy['contact_email']}")
                                        with col2:
                                            st.write(f"📞 **Phone:** {strategy['contact_phone']}")
                                        
                                        # Items to order
                                        st.write(f"**📋 Order these items ({strategy['total_pieces']} pieces total):**")
                                        for item in strategy['items_list']:
                                            st.write(f"• **{item['item_name']}** - {item['quantity']} pieces")
                                        
                                        # Approval button for each bundle
                                        if st.button(f"✅ Approve Order #{i} - {strategy['vendor_name']}", key=f"approve_{i}"):
                                            st.success(f"✅ Order #{i} approved! You can now contact {strategy['vendor_name']}")
                                        
                                        st.markdown("---")
                            
                            # Summary
                            st.info(f"💡 **Summary:** {result.get('total_bundles', 0)} vendors will provide {result.get('coverage_percentage', 0):.0f}% coverage of all requested items")
                    else:
                        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        
        with col2:
            st.info("💡 This will analyze all pending requests and recommend the most efficient vendor strategy")
    
    except Exception as e:
        st.error(f"Error in smart recommendations: {str(e)}")

def display_user_management_admin(db):
    """Admin-only user management inside integrated operator dashboard.
    Note: Only visible to users in operator dashboard, so no extra login prompt.
    """
    st.header("👤 User Management")
    st.caption("Create, edit, activate/deactivate users; change roles; reset passwords")

    # Show success after rerun if user was created (show for 1s then clear)
    if st.session_state.get('um_user_created_success'):
        _ph = st.empty()
        _ph.success("User created.")
        time.sleep(1)
        del st.session_state['um_user_created_success']
        st.rerun()

    # Clean table-based user management
    try:
        users = db.list_users() or []
        if not users:
            st.info("No users found.")
        else:
            # Display users in a clean table format
            st.subheader(f"All Users ({len(users)})")
            
            # Create a clean table display
            for i, u in enumerate(users):
                with st.container():
                    st.markdown(f"**{u['username']}** - {u.get('full_name') or 'No name'}")
                    
                    # User info in clean columns
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        st.write(f"📧 {u.get('email') or 'No email'}")
                        st.write(f"🏢 {u.get('department') or 'No department'}")
                    with col2:
                        status = "🟢 Active" if u.get('is_active') else "🔴 Inactive"
                        st.write(f"Status: {status}")
                        st.write(f"Role: {u.get('user_role') or 'User'}")
                    with col3:
                        st.write(f"Created: {str(u.get('created_at', ''))[:10]}")
                        st.write(f"Last login: {str(u.get('last_login', 'Never'))[:10]}")
                    with col4:
                        # Action buttons
                        if st.button("✏️ Edit", key=f"edit_{u['user_id']}", use_container_width=True):
                            st.session_state[f'editing_user_{u["user_id"]}'] = True
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"del_{u['user_id']}", use_container_width=True):
                            st.session_state[f'confirm_delete_{u["user_id"]}'] = True
                            st.rerun()
                    
                    # Edit form (appears when Edit is clicked)
                    if st.session_state.get(f'editing_user_{u["user_id"]}'):
                        st.markdown("---")
                        with st.form(f"edit_form_{u['user_id']}"):
                            st.write("**Edit User**")
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                edit_name = st.text_input("Full Name", value=u.get('full_name') or "")
                                edit_email = st.text_input("Email", value=u.get('email') or "")
                                edit_dept = st.text_input("Department", value=u.get('department') or "")
                            with ec2:
                                role_options = ["User", "Operator", "Operation"]
                                current_role = u.get('user_role') or "User"
                                role_index = role_options.index(current_role) if current_role in role_options else 0
                                edit_role = st.selectbox("Role", role_options, index=role_index)
                                edit_active = st.checkbox("Active", value=bool(u.get('is_active')))
                                edit_pw = st.text_input("New Password (optional)", type="password")
                            
                            eb1, eb2 = st.columns(2)
                            with eb1:
                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                    ok1 = db.update_user_profile(u['user_id'], edit_name, edit_email, edit_dept)
                                    ok2 = db.set_user_role(u['user_id'], edit_role)
                                    ok3 = db.set_user_active(u['user_id'], edit_active)
                                    
                                    if edit_pw.strip():
                                        ok4 = db.reset_user_password(u['user_id'], edit_pw.strip())
                                    else:
                                        ok4 = True
                                    
                                    if ok1 and ok2 and ok3 and ok4:
                                        del st.session_state[f'editing_user_{u["user_id"]}']
                                        st.success("User updated successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to update user.")
                            with eb2:
                                if st.form_submit_button("❌ Cancel"):
                                    del st.session_state[f'editing_user_{u["user_id"]}']
                                    st.rerun()
                    
                    # Delete confirmation (appears when Delete is clicked)
                    if st.session_state.get(f'confirm_delete_{u["user_id"]}'):
                        st.markdown("---")
                        st.warning(f"⚠️ Are you sure you want to delete user **{u['username']}**?")
                        dc1, dc2 = st.columns(2)
                        with dc1:
                            if st.button("🗑️ Yes, Delete", key=f"confirm_del_{u['user_id']}", type="primary"):
                                if db.delete_user(u['user_id']):
                                    del st.session_state[f'confirm_delete_{u["user_id"]}']
                                    st.success("User deleted successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to delete user. They may have linked requests.")
                        with dc2:
                            if st.button("❌ Cancel", key=f"cancel_del_{u['user_id']}"):
                                del st.session_state[f'confirm_delete_{u["user_id"]}']
                                st.rerun()
                    
                    st.markdown("---")

    except Exception as e:
        st.error(f"Error loading users: {str(e)}")

    st.markdown("---")
    st.subheader("Create New User")
    with st.form("um_create_user_form", clear_on_submit=True):
        cu1, cu2 = st.columns(2)
        with cu1:
            c_username = st.text_input("Username")
            c_fullname = st.text_input("Full name")
            c_department = st.text_input("Department")
        with cu2:
            c_email = st.text_input("Email")
            c_role = st.selectbox("Role", ["User", "Operator", "Operation"])
            c_active = st.checkbox("Active", value=True)
        c_pw = st.text_input("Initial password", type="password")
        submit_new = st.form_submit_button("Create User", type="primary")
    if submit_new:
        if not c_username or not c_pw:
            st.warning("Username and password are required.")
        else:
            res = db.create_user(c_username.strip(), c_pw.strip(), c_fullname.strip(), c_email.strip(), c_department.strip(), c_role, 1 if c_active else 0)
            if res.get('success'):
                st.session_state['um_user_created_success'] = True
                st.rerun()
            else:
                st.error(f"Failed to create user: {res.get('error')}")

def display_active_bundles_for_operator(db):
    """Show active bundles in operator-friendly format"""
    st.header("📦 Active Orders & Bundles")
    st.write("Track your approved orders and their status")
    
    try:
        # Batch fetch: bundles with vendor info in a single query
        all_bundles = get_bundles_with_vendor_info(db)
        
        if not all_bundles:
            st.info("No active bundles yet. Generate recommendations first!")
            return
        
        # Count bundles by status
        status_counts = {
            'Active': sum(1 for b in all_bundles if b['status'] == 'Active'),
            'Reviewed': sum(1 for b in all_bundles if b['status'] == 'Reviewed'),
            'Approved': sum(1 for b in all_bundles if b['status'] == 'Approved'),
            'Ordered': sum(1 for b in all_bundles if b['status'] == 'Ordered'),
            'Completed': sum(1 for b in all_bundles if b['status'] == 'Completed')
        }
        
        # Status filter
        col_filter, col_total = st.columns([3, 1])
        with col_filter:
            status_options = [
                f"🟡 Active ({status_counts['Active']})",
                f"🟢 Reviewed ({status_counts['Reviewed']})",
                f"🔵 Approved ({status_counts['Approved']})",
                f"📦 Ordered ({status_counts['Ordered']})",
                f"🎉 Completed ({status_counts['Completed']})",
                f"📋 All Bundles ({len(all_bundles)})"
            ]
            selected_filter = st.selectbox("Filter by Status:", status_options, index=5)
        
        with col_total:
            st.metric("Total", len(all_bundles))
        
        # Filter bundles based on selection
        if "Active" in selected_filter and "All" not in selected_filter:
            bundles = [b for b in all_bundles if b['status'] == 'Active']
            st.info(f"Showing {len(bundles)} Active bundles (Need Review)")
        elif "Reviewed" in selected_filter and "All" not in selected_filter:
            bundles = [b for b in all_bundles if b['status'] == 'Reviewed']
            st.success(f"Showing {len(bundles)} Reviewed bundles (Ready to Approve)")
        elif "Approved" in selected_filter:
            bundles = [b for b in all_bundles if b['status'] == 'Approved']
            st.info(f"Showing {len(bundles)} Approved bundles (Ready to Order)")
        elif "Ordered" in selected_filter:
            bundles = [b for b in all_bundles if b['status'] == 'Ordered']
            st.info(f"Showing {len(bundles)} Ordered bundles (Waiting Delivery)")
        elif "Completed" in selected_filter:
            bundles = [b for b in all_bundles if b['status'] == 'Completed']
            st.success(f"Showing {len(bundles)} Completed bundles")
        else:
            bundles = all_bundles
            st.write(f"**📊 Showing all {len(bundles)} bundles**")
        
        if not bundles:
            st.info("No bundles in this status")
            return
        
        st.markdown("---")
        
        # Review Progress Indicator (for Active/Reviewed bundles only)
        active_or_reviewed_bundles = [b for b in bundles if b['status'] in ('Active', 'Reviewed')]
        if active_or_reviewed_bundles:
            reviewed_count = len([b for b in active_or_reviewed_bundles if b['status'] == 'Reviewed'])
            active_count = len([b for b in active_or_reviewed_bundles if b['status'] == 'Active'])
            total_count = len(active_or_reviewed_bundles)
            
            # Simple progress indicator
            if active_count > 0:
                st.info(f"📊 **Review Progress:** {reviewed_count}/{total_count} bundles reviewed • {active_count} remaining")
            
            st.markdown("---")

        # Prepare IDs for batched item and user lookups
        bundle_ids = [b.get('bundle_id') for b in bundles if b.get('bundle_id') is not None]

        # Batch fetch: all items for these bundles in one query
        items_by_bundle = {}
        if bundle_ids:
            items_list = get_bundle_items_for_bundles(db, bundle_ids)
            for row in items_list or []:
                items_by_bundle.setdefault(row['bundle_id'], []).append(row)

        # Collect all user IDs from user_breakdown across all items
        user_ids_set = set()
        for rows in items_by_bundle.values():
            for it in rows:
                try:
                    breakdown = json.loads(it.get('user_breakdown') or '{}') if isinstance(it.get('user_breakdown'), str) else it.get('user_breakdown') or {}
                except Exception:
                    breakdown = {}
                for uid in breakdown.keys():
                    if str(uid).isdigit():
                        user_ids_set.add(int(uid))

        # Batch fetch: user names for all referenced user IDs
        user_name_map = get_user_names_map(db, sorted(user_ids_set)) if user_ids_set else {}
        
        # Initialize session state for selections (MUST be before any usage)
        if 'selected_bundles' not in st.session_state:
            st.session_state.selected_bundles = []
        
        # Bulk Approval Actions (ONLY for Reviewed bundles - NO bulk review)
        reviewed_bundles = [b for b in bundles if b['status'] == 'Reviewed']
        if reviewed_bundles and active_count == 0:
            # Only show bulk approval when ALL bundles are reviewed - CLEAN UI
            st.success("✅ **All bundles reviewed!** Select bundles below to approve.")
            
            # Compact action row
            col_select, col_button = st.columns([1, 5])
            with col_select:
                select_all = st.checkbox("Select All", key="select_all_bundles")
                if select_all:
                    st.session_state.selected_bundles = [b['bundle_id'] for b in reviewed_bundles]
                else:
                    if st.session_state.get('deselect_triggered'):
                        st.session_state.selected_bundles = []
                        st.session_state.deselect_triggered = False
            
            with col_button:
                if st.session_state.selected_bundles:
                    if st.button(f"🎯 Approve Selected ({len(st.session_state.selected_bundles)})", type="primary", key="bulk_approve"):
                        result = db.mark_bundles_approved_bulk(st.session_state.selected_bundles)
                        if result['success']:
                            st.success(f"✅ Approved {result['approved_count']} bundle(s)!")
                            st.session_state.selected_bundles = []
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
            
            st.markdown("---")
        
        # Sort bundles: rejected ones first, then by created date
        bundles_sorted = sorted(bundles, key=lambda b: (
            0 if (b['status'] == 'Active' and b.get('rejection_reason')) else 1,
            b.get('created_at') or ''
        ), reverse=False)
        
        # Track if we need separator after rejected bundles
        rejected_count = sum(1 for b in bundles if b['status'] == 'Active' and b.get('rejection_reason'))
        rejected_shown = 0
        
        # Display bundles in operator-friendly format
        for bundle in bundles_sorted:
            # Build expander title with merge badge
            merge_badge = ""
            merge_count_val = bundle.get('merge_count') or 0  # Handle NULL from database
            if merge_count_val > 0:
                merge_badge = f" 🔄 Updated {merge_count_val}x"
            
            # Add rejection badge if bundle was rejected
            rejection_badge = ""
            if bundle['status'] == 'Active' and bundle.get('rejection_reason'):
                rejection_badge = " ⚠️ REJECTED"
            
            expander_title = f"📦 {bundle['bundle_name']}{merge_badge}{rejection_badge} - {get_status_badge(bundle['status'])}"
            
            # Add checkbox ONLY for Reviewed bundles (for approval)
            if bundle['status'] == 'Reviewed':
                col_check, col_exp = st.columns([0.5, 11.5])
                with col_check:
                    is_selected = bundle['bundle_id'] in st.session_state.selected_bundles
                    if st.checkbox("", value=is_selected, key=f"check_{bundle['bundle_id']}", label_visibility="collapsed"):
                        if bundle['bundle_id'] not in st.session_state.selected_bundles:
                            st.session_state.selected_bundles.append(bundle['bundle_id'])
                    else:
                        if bundle['bundle_id'] in st.session_state.selected_bundles:
                            st.session_state.selected_bundles.remove(bundle['bundle_id'])
                
                with col_exp:
                    expander_obj = st.expander(expander_title, expanded=False)
            else:
                expander_obj = st.expander(expander_title, expanded=False)
            
            # Add separator after rejected bundles
            if bundle['status'] == 'Active' and bundle.get('rejection_reason'):
                rejected_shown += 1
            
            # Show separator after last rejected bundle (if there are more bundles)
            if rejected_shown == rejected_count and rejected_count > 0 and rejected_count < len(bundles):
                # Only show separator once after rejected bundles
                if rejected_shown == rejected_count:
                    st.markdown("")
                    rejected_shown += 1  # Prevent showing separator again
            
            with expander_obj:
                # Show merge indicators if bundle was updated
                merge_count = bundle.get('merge_count') or 0  # Handle NULL from database
                last_merged = bundle.get('last_merged_at')
                merge_reason = bundle.get('merge_reason')
                
                if merge_count > 0:
                    st.info(f"🔄 **This bundle has been updated {merge_count} time(s)**")
                    
                    if last_merged:
                        if hasattr(last_merged, 'strftime'):
                            last_merged_str = last_merged.strftime('%b %d, %Y at %I:%M %p')
                        else:
                            last_merged_str = str(last_merged)
                        st.caption(f"Last updated: {last_merged_str}")
                    
                    if merge_reason:
                        st.warning(f"ℹ️ {merge_reason}")
                    
                    st.markdown("---")
                
                # Show rejection warning if bundle was rejected by Operation Team
                if bundle['status'] == 'Active' and bundle.get('rejection_reason'):
                    st.error("⚠️ **REJECTED BY OPERATION TEAM**")
                    rejected_date = bundle.get('rejected_at', 'N/A')
                    if hasattr(rejected_date, 'strftime'):
                        rejected_date = rejected_date.strftime('%Y-%m-%d %H:%M:%S')
                    st.markdown(f"""
                    <div style='background-color: #ffebee; padding: 15px; border-radius: 5px; border-left: 5px solid #f44336;'>
                        <p style='margin: 0; color: #c62828;'><strong>Rejected on:</strong> {rejected_date}</p>
                        <p style='margin: 5px 0 0 0; color: #c62828;'><strong>Reason:</strong> {bundle.get('rejection_reason', 'No reason provided')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                
                # Vendor details already joined
                vendor_name = bundle.get('vendor_name') or "Unknown Vendor"
                vendor_email = bundle.get('vendor_email') or ""
                vendor_phone = bundle.get('vendor_phone') or ""

                # Summary row
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    st.write(f"**Vendor:** {vendor_name}")
                    if vendor_email:
                        st.write(f"📧 {vendor_email}")
                    if vendor_phone:
                        st.write(f"📞 {vendor_phone}")
                with col2:
                    st.write(f"**Items:** {bundle.get('total_items', 'N/A')}")
                    st.write(f"**Pieces:** {bundle.get('total_quantity', 'N/A')}")
                with col3:
                    st.write(f"**Status:** {get_status_badge(bundle['status'])}")
                
                # Show PO details if Ordered or Completed
                if bundle['status'] in ('Ordered', 'Completed') and bundle.get('po_number'):
                    st.markdown("---")
                    st.info("📦 **Order Details**")
                    po_col1, po_col2, po_col3 = st.columns(3)
                    with po_col1:
                        st.write(f"**PO Number:** {bundle['po_number']}")
                    with po_col2:
                        if bundle.get('po_date'):
                            po_date = bundle['po_date'].strftime('%B %d, %Y') if hasattr(bundle['po_date'], 'strftime') else str(bundle['po_date'])[:10]
                            st.write(f"**Order Date:** {po_date}")
                    with po_col3:
                        if bundle.get('expected_delivery_date'):
                            delivery_date = bundle['expected_delivery_date'].strftime('%B %d, %Y') if hasattr(bundle['expected_delivery_date'], 'strftime') else str(bundle['expected_delivery_date'])[:10]
                            st.write(f"**Expected Delivery:** {delivery_date}")
                
                # Show delivery details if Completed
                if bundle['status'] == 'Completed':
                    st.success("📦 **Delivery Details**")
                    delivery_col1, delivery_col2 = st.columns(2)
                    # PACKING SLIP - HIDDEN (Can reactivate if needed)
                    # with delivery_col1:
                    #     if bundle.get('packing_slip_code'):
                    #         st.write(f"**Packing Slip:** {bundle['packing_slip_code']}")
                    with delivery_col1:
                        if bundle.get('actual_delivery_date'):
                            delivery_date = bundle['actual_delivery_date'].strftime('%B %d, %Y') if hasattr(bundle['actual_delivery_date'], 'strftime') else str(bundle['actual_delivery_date'])[:10]
                            st.write(f"**Delivered:** {delivery_date}")
                    with delivery_col2:
                        if bundle.get('completed_at'):
                            completed_date = bundle['completed_at'].strftime('%B %d, %Y') if hasattr(bundle['completed_at'], 'strftime') else str(bundle['completed_at'])[:10]
                            completed_by = bundle.get('completed_by', 'Unknown')
                            st.write(f"**Marked Complete:** {completed_date}")
                            st.caption(f"by {completed_by}")

                st.markdown("---")
                
                # User Requests & Notes section
                st.write("**📋 User Requests in this Bundle:**")
                requests_in_bundle = db.get_bundle_requests_with_notes(bundle.get('bundle_id'))
                
                if requests_in_bundle:
                    for req in requests_in_bundle:
                        with st.container():
                            # Request header
                            st.markdown(f"**👤 {req['req_number']}** ({req['full_name']}) - {req['item_count']} item(s)")
                            
                            # Show notes if exist
                            if req.get('user_notes') and req['user_notes'].strip():
                                st.info(f"📝 {req['user_notes']}")
                            else:
                                st.caption("(No notes)")
                            
                            st.markdown("")  # Small spacing
                else:
                    st.caption("No request information available")
                
                st.markdown("---")
                st.write("**Items in this bundle:**")
                # Use batched items
                items = items_by_bundle.get(bundle.get('bundle_id'), [])
                
                # Get costs if Ordered status
                item_costs_map = {}
                if bundle['status'] == 'Ordered':
                    order_details = db.get_order_details(bundle.get('bundle_id'))
                    for detail in order_details or []:
                        if detail.get('cost'):
                            item_costs_map[detail['item_id']] = detail['cost']
                
                if items:
                    # Build HTML table
                    html_table = """
                    <style>
                        .bundle-table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 10px;
                            font-size: 14px;
                        }
                        .bundle-table thead {
                            background-color: #f0f2f6;
                        }
                        .bundle-table th {
                            padding: 12px 10px;
                            text-align: left;
                            border-bottom: 2px solid #ddd;
                            font-weight: 600;
                        }
                        .bundle-table td {
                            padding: 10px;
                            border-bottom: 1px solid #eee;
                            vertical-align: top;
                        }
                        .bundle-table tbody tr:nth-child(even) {
                            background-color: #f9f9f9;
                        }
                        .bundle-table tbody tr:hover {
                            background-color: #f0f0f0;
                        }
                        .item-name {
                            font-weight: 600;
                            color: #1f1f1f;
                        }
                        .item-dims {
                            font-size: 12px;
                            color: #666;
                        }
                        .item-total {
                            font-size: 12px;
                            color: #0066cc;
                        }
                        .user-name {
                            font-weight: 500;
                            color: #333;
                        }
                        .project-icon {
                            margin-right: 4px;
                        }
                        .qty-cell {
                            text-align: right;
                            font-weight: 500;
                        }
                    </style>
                    <table class="bundle-table">
                        <thead>
                            <tr>
                                <th style="width: 30%;">Item</th>
                                <th style="width: 20%;">User</th>
                                <th style="width: 20%;">Project</th>
                                <th style="width: 15%;">Date Needed</th>
                                <th style="width: 15%; text-align: right;">Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    
                    for it in items:
                        # Build dimension text
                        dims = []
                        for key in ('height', 'width', 'thickness'):
                            sval = fmt_dim(it.get(key))
                            if sval and sval.lower() not in ("n/a", "none", "null"):
                                dims.append(sval)
                        dim_txt = f"{' x '.join(dims)}" if dims else ""
                        
                        # Show cost if Ordered
                        cost_txt = ""
                        if bundle['status'] == 'Ordered' and it['item_id'] in item_costs_map:
                            cost = item_costs_map[it['item_id']]
                            cost_txt = f" @ ${cost:.2f}/pc"
                        
                        # Get user breakdown
                        try:
                            breakdown = json.loads(it.get('user_breakdown') or '{}') if isinstance(it.get('user_breakdown'), str) else it.get('user_breakdown') or {}
                        except Exception:
                            breakdown = {}
                        
                        if breakdown:
                            # Get project breakdown for this item
                            project_breakdown = db.get_bundle_item_project_breakdown(bundle.get('bundle_id'), it['item_id'])
                            project_map = {}
                            date_map = {}
                            for pb in project_breakdown or []:
                                key = (pb['user_id'], pb.get('project_number'))
                                project_map[key] = project_map.get(key, 0) + pb['quantity']
                                if pb.get('date_needed'):
                                    date_map[key] = pb['date_needed']
                            
                            # Count total rows for this item (for rowspan)
                            total_rows = sum(len([(k[1], v) for k, v in project_map.items() if k[0] == int(uid) and k[1]]) or 1 
                                           for uid in breakdown.keys())
                            
                            # First row flag
                            first_row = True
                            
                            for uid, qty in breakdown.items():
                                # Check if this is BoxHero system user (user_id = 5)
                                is_boxhero = (int(uid) == 5) if str(uid).isdigit() else False
                                
                                if is_boxhero:
                                    # BoxHero item - show special indicator
                                    uname = "BoxHero Restock"
                                    user_icon = "📦"
                                else:
                                    # Regular user item
                                    uname = user_name_map.get(int(uid), f"User {uid}") if str(uid).isdigit() else f"User {uid}"
                                    user_icon = "👤"
                                
                                user_project_breakdown = [(k[1], v) for k, v in project_map.items() if k[0] == int(uid) and k[1]]
                                
                                if user_project_breakdown:
                                    # Multiple projects for this user
                                    user_rows = len(user_project_breakdown)
                                    for idx, (project_num, project_qty) in enumerate(user_project_breakdown):
                                        html_table += "<tr>"
                                        
                                        # Item cell (only on first row)
                                        if first_row:
                                            html_table += f"""
                                            <td rowspan="{total_rows}">
                                                <div class="item-name">{it['item_name']}</div>
                                                <div class="item-dims">{dim_txt}</div>
                                                <div class="item-total">Total: {it['total_quantity']} pcs{cost_txt}</div>
                                            </td>
                                            """
                                            first_row = False
                                        
                                        # User cell (rowspan if multiple projects)
                                        if idx == 0:
                                            html_table += f'<td rowspan="{user_rows}"><span class="user-name">{user_icon} {uname}</span></td>'
                                        
                                        # Project cell
                                        formatted_project = format_project_display(project_num, None)
                                        html_table += f'<td><span class="project-icon">📋</span>{formatted_project}</td>'
                                        
                                        # Date needed cell
                                        date_key = (int(uid), project_num)
                                        date_value = date_map.get(date_key, None)
                                        date_display = str(date_value) if date_value else "—"
                                        html_table += f'<td style="color:#666;">{date_display}</td>'
                                        
                                        # Quantity cell
                                        html_table += f'<td class="qty-cell">{project_qty} pcs</td>'
                                        html_table += "</tr>"
                                else:
                                    # No project info (typical for BoxHero items)
                                    html_table += "<tr>"
                                    if first_row:
                                        html_table += f"""
                                        <td rowspan="{total_rows}">
                                            <div class="item-name">{it['item_name']}</div>
                                            <div class="item-dims">{dim_txt}</div>
                                            <div class="item-total">Total: {it['total_quantity']} pcs{cost_txt}</div>
                                        </td>
                                        """
                                        first_row = False
                                    html_table += f'<td><span class="user-name">{user_icon} {uname}</span></td>'
                                    html_table += '<td>—</td>'
                                    html_table += '<td>—</td>'
                                    html_table += f'<td class="qty-cell">{qty} pcs</td>'
                                    html_table += '</tr>'
                        else:
                            # No breakdown
                            html_table += f"""
                            <tr>
                                <td>
                                    <div class="item-name">{it['item_name']}</div>
                                    <div class="item-dims">{dim_txt}</div>
                                    <div class="item-total">Total: {it['total_quantity']} pcs{cost_txt}</div>
                                </td>
                                <td>—</td>
                                <td>—</td>
                                <td>—</td>
                                <td class="qty-cell">{it['total_quantity']} pcs</td>
                            </tr>
                            """
                    
                    html_table += """
                        </tbody>
                    </table>
                    """
                    
                    st.markdown(html_table, unsafe_allow_html=True)
                else:
                    st.write("No items found for this bundle")

                # Duplicate Project Detection and Review
                st.markdown("---")
                duplicates = db.detect_duplicate_projects_in_bundle(bundle.get('bundle_id'))
                duplicates_reviewed = bundle.get('duplicates_reviewed', 0)
                
                if duplicates and not duplicates_reviewed:
                    # Show warning and edit interface ONLY if duplicates exist AND not yet reviewed
                    st.error(f"⚠️ **{len(duplicates)} DUPLICATE PROJECT(S) DETECTED - REVIEW REQUIRED**")
                    
                    # Display each duplicate with edit interface
                    for idx, dup in enumerate(duplicates):
                        # Format project display with sub-project if available
                        formatted_project = format_project_display(dup['project_number'], dup.get('sub_project_number'))
                        st.markdown(f"**🔍 Duplicate {idx+1}: {dup['item_name']} - Project {formatted_project}**")
                        st.warning(f"Multiple users requested this item for the same project")
                        
                        # Show each user's contribution with edit capability
                        st.write("**User Contributions:**")
                        for user_data in dup['users']:
                            user_id = user_data['user_id']
                            current_qty = user_data['quantity']
                            uname = user_data.get('full_name', user_name_map.get(user_id, f"User {user_id}"))
                            
                            col_name, col_qty, col_btn = st.columns([2, 1, 1])
                            with col_name:
                                st.write(f"👤 **{uname}**")
                            with col_qty:
                                new_qty = st.number_input(
                                    "Quantity",
                                    min_value=0,
                                    value=current_qty,
                                    key=f"dup_qty_{bundle.get('bundle_id')}_{dup['item_id']}_{user_id}",
                                    help="Set to 0 to remove this user's contribution"
                                )
                            with col_btn:
                                if new_qty != current_qty:
                                    if st.button("Update", key=f"dup_update_{bundle.get('bundle_id')}_{dup['item_id']}_{user_id}"):
                                        result = db.update_bundle_item_user_quantity(
                                            bundle.get('bundle_id'),
                                            dup['item_id'],
                                            user_id,
                                            new_qty
                                        )
                                        if result['success']:
                                            if new_qty == 0:
                                                st.success(f"✅ Removed {uname}'s contribution")
                                            else:
                                                st.success(f"✅ Updated {uname}: {result['old_quantity']} → {new_qty} pcs")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Update failed: {result.get('error')}")
                        
                        st.caption("💡 **Options:** Adjust quantities, remove a user (set to 0), or keep both as-is.")
                        
                        if idx < len(duplicates) - 1:
                            st.markdown("---")
                    
                    # Mark as Reviewed button
                    st.markdown("---")
                    if st.button("✅ Mark Duplicates as Reviewed", key=f"mark_reviewed_{bundle.get('bundle_id')}", type="primary"):
                        if db.mark_bundle_duplicates_reviewed(bundle.get('bundle_id')):
                            st.success("✅ Duplicates marked as reviewed!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to mark as reviewed")
                
                elif duplicates and duplicates_reviewed:
                    # Just show a success message if duplicates were reviewed
                    st.success(f"✅ Duplicates Reviewed - {len(duplicates)} item(s) were checked")

                # Read-only vendor options for single-item bundles (Active/Reviewed status only)
                try:
                    items = items_by_bundle.get(bundle.get('bundle_id'), [])
                    if len(items) == 1 and bundle['status'] in ('Active', 'Reviewed'):
                        st.markdown("---")
                        st.caption("Other vendor options for this item (view-only)")
                        single_item = items[0]
                        # Fetch all vendors for this item
                        vendor_rows = db.get_item_vendors([single_item['item_id']]) or []
                        # Build options list
                        options = []
                        default_index = 0
                        for idx, vr in enumerate(vendor_rows):
                            label_parts = [vr.get('vendor_name') or 'Unknown']
                            email = vr.get('contact_email') or ''
                            phone = vr.get('contact_phone') or ''
                            meta = " — " + " | ".join([p for p in [email, phone] if p]) if (email or phone) else ""
                            label = f"{label_parts[0]}{meta}"
                            options.append(label)
                            # Preselect current bundle vendor if names match
                            if (bundle.get('vendor_name') or '').strip().lower() == (vr.get('vendor_name') or '').strip().lower():
                                default_index = idx
                        if len(options) > 1:
                            sel = st.selectbox(
                                "Vendor options",
                                options,
                                index=default_index,
                                key=f"vendor_options_{bundle.get('bundle_id')}"
                            )
                            # Show selected details explicitly
                            sel_row = vendor_rows[options.index(sel)] if options else None
                            if sel_row:
                                st.info(f"Selected: {sel_row.get('vendor_name')}  |  {sel_row.get('contact_email') or 'No email'}  |  {sel_row.get('contact_phone') or 'No phone'}")
                                
                                # Show "Change Vendor" button if different vendor selected
                                selected_vendor_id = sel_row.get('vendor_id')
                                current_vendor_id = bundle.get('recommended_vendor_id')
                                
                                if selected_vendor_id and selected_vendor_id != current_vendor_id:
                                    if st.button(f"🔄 Change to {sel_row.get('vendor_name')}", key=f"change_vendor_{bundle.get('bundle_id')}", type="primary"):
                                        # Move item to selected vendor
                                        result = db.move_item_to_vendor(
                                            bundle.get('bundle_id'),
                                            single_item['item_id'],
                                            selected_vendor_id
                                        )
                                        
                                        if result.get('success'):
                                            st.success(f"✅ {result.get('message', 'Item moved successfully!')}")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {result.get('error', 'Failed to move item')}")
                        # If only one vendor, skip showing the selector entirely
                except Exception as _e:
                    # Fail silently to avoid breaking bundle view in cloud
                    pass

                st.markdown("---")
                # Show related requests (traceability) using batched map
                bundle_req_numbers = get_bundle_request_numbers_map(db, bundle_ids)
                req_list = bundle_req_numbers.get(bundle.get('bundle_id'), [])
                if req_list:
                    st.write("**From Requests:** " + ", ".join(req_list))

                # Actions - Dynamic based on status
                if bundle['status'] == 'Active':
                    # Active: Show Mark as Reviewed (with checklist) and Report Issue buttons ONLY
                    action_cols = st.columns(2)
                    with action_cols[0]:
                        if st.button(f"✅ Mark as Reviewed", key=f"review_{bundle['bundle_id']}", type="primary"):
                            st.session_state[f'reviewing_bundle_{bundle["bundle_id"]}'] = True
                            st.rerun()
                    with action_cols[1]:
                        if st.button(f"⚠️ Report Issue", key=f"report_{bundle['bundle_id']}"):
                            st.session_state[f'reporting_issue_{bundle["bundle_id"]}'] = True
                            st.rerun()
                
                elif bundle['status'] == 'Reviewed':
                    # Reviewed: Minimal UI - just revert option
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption("✅ Reviewed - ready for approval")
                    with col2:
                        if st.button(f"↩️ Revert", key=f"revert_{bundle['bundle_id']}", help="Revert to Active if changes needed"):
                            revert_q = "UPDATE requirements_bundles SET status = 'Active' WHERE bundle_id = ?"
                            db.execute_insert(revert_q, (bundle['bundle_id'],))
                            db.conn.commit()
                            st.success("Bundle reverted to Active")
                            st.rerun()
                
                elif bundle['status'] == 'Approved':
                    # Approved: Show Order Placed button (completion disabled until ordered)
                    action_cols = st.columns(2)
                    with action_cols[0]:
                        if st.button(f"📦 Order Placed", key=f"order_{bundle['bundle_id']}", type="primary"):
                            st.session_state[f'placing_order_{bundle["bundle_id"]}'] = True
                            st.rerun()
                    with action_cols[1]:
                        st.button(f"🏁 Mark as Completed", key=f"complete_{bundle['bundle_id']}", disabled=True)
                        st.caption("⚠️ Place order first")
                
                elif bundle['status'] == 'Ordered':
                    # Ordered: Only show completion button
                    if st.button(f"🏁 Mark as Completed", key=f"complete_{bundle['bundle_id']}", type="primary"):
                        st.session_state[f'completing_bundle_{bundle["bundle_id"]}'] = True
                        st.rerun()
                
                # Review Checklist Flow (for marking as Reviewed)
                if st.session_state.get(f'reviewing_bundle_{bundle["bundle_id"]}'):
                    st.markdown("---")
                    display_review_checklist(db, bundle, items_by_bundle.get(bundle.get('bundle_id'), []), duplicates, duplicates_reviewed)
                
                # Approval Checklist Flow
                if st.session_state.get(f'approving_bundle_{bundle["bundle_id"]}'):
                    st.markdown("---")
                    display_approval_checklist(db, bundle, items_by_bundle.get(bundle.get('bundle_id'), []), duplicates, duplicates_reviewed)
                
                # Report Issue Flow
                if st.session_state.get(f'reporting_issue_{bundle["bundle_id"]}'):
                    st.markdown("---")
                    display_issue_resolution_flow(db, bundle, items_by_bundle.get(bundle.get('bundle_id'), []))
                
                # Order Placement Flow
                if st.session_state.get(f'placing_order_{bundle["bundle_id"]}'):
                    st.markdown("---")
                    display_order_placement_form(db, bundle)
                
                # Completion Flow (with packing slip)
                if st.session_state.get(f'completing_bundle_{bundle["bundle_id"]}'):
                    st.markdown("---")
                    display_completion_form(db, bundle)
    
    except Exception as e:
        st.error(f"Error loading active bundles: {str(e)}")

def display_review_checklist(db, bundle, bundle_items, duplicates, duplicates_reviewed):
    """Display review checklist before marking bundle as Reviewed"""
    st.subheader("📋 Bundle Review Checklist")
    
    bundle_id = bundle['bundle_id']
    vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
    
    st.write(f"**Before marking this bundle as Reviewed, please confirm:**")
    st.caption("All items must be checked to mark as reviewed")
    
    # Checklist items
    check1 = st.checkbox(
        f"I have verified **{vendor_name}** contact information is correct",
        key=f"review_check1_{bundle_id}"
    )
    
    # Show items list
    st.markdown("**Items in this bundle:**")
    for item in bundle_items:
        st.write(f"• {item['item_name']} ({item['total_quantity']} pcs)")
    
    check2 = st.checkbox(
        f"I have reviewed ALL {len(bundle_items)} items and quantities in this bundle",
        key=f"review_check2_{bundle_id}"
    )
    
    # Duplicate check (conditional)
    if duplicates:
        if duplicates_reviewed:
            check3 = st.checkbox(
                f"All duplicate project issues have been reviewed and resolved ✅",
                value=True,
                disabled=True,
                key=f"review_check3_{bundle_id}"
            )
        else:
            st.warning(f"⚠️ **{len(duplicates)} duplicate project(s) detected** - Must be reviewed first")
            check3 = st.checkbox(
                f"All duplicate project issues have been reviewed and resolved",
                value=False,
                disabled=True,
                key=f"review_check3_{bundle_id}"
            )
            st.caption("👆 Please scroll up and mark duplicates as reviewed first")
    else:
        check3 = True  # No duplicates, auto-pass
    
    check4 = st.checkbox(
        f"**{vendor_name}** is the correct vendor for these items",
        key=f"review_check4_{bundle_id}"
    )
    
    st.markdown("---")
    
    # Validation
    all_checked = check1 and check2 and check3 and check4
    
    col1, col2 = st.columns(2)
    with col1:
        if all_checked:
            if st.button("✅ Confirm & Mark as Reviewed", key=f"confirm_review_{bundle_id}", type="primary"):
                if db.mark_bundle_reviewed(bundle_id):
                    del st.session_state[f'reviewing_bundle_{bundle_id}']
                    st.success(f"✅ Bundle marked as Reviewed!")
                    st.rerun()
                else:
                    st.error("❌ Failed to mark as reviewed")
        else:
            st.button("✅ Confirm & Mark as Reviewed", key=f"confirm_review_{bundle_id}", disabled=True)
            if not check3 and duplicates and not duplicates_reviewed:
                st.caption("⚠️ Review duplicates first")
            else:
                st.caption("⚠️ Please confirm all items above")
    
    with col2:
        if st.button("Cancel", key=f"cancel_review_{bundle_id}"):
            del st.session_state[f'reviewing_bundle_{bundle_id}']
            st.rerun()

def display_approval_checklist(db, bundle, bundle_items, duplicates, duplicates_reviewed):
    """Display approval checklist before approving bundle"""
    st.subheader("📋 Bundle Approval Checklist")
    
    bundle_id = bundle['bundle_id']
    vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
    
    st.write(f"**Before approving this bundle with {vendor_name}, please confirm:**")
    st.caption("All items must be checked before approval")
    
    # Checklist items
    check1 = st.checkbox(
        f"I have contacted **{vendor_name}** and confirmed they can supply these items",
        key=f"check1_{bundle_id}"
    )
    
    # Show items list (no nested expander - use container instead)
    st.markdown("**Items in this bundle:**")
    for item in bundle_items:
        st.write(f"• {item['item_name']} ({item['total_quantity']} pcs)")
    
    check2 = st.checkbox(
        f"**{vendor_name}** can supply ALL {len(bundle_items)} items in this bundle",
        key=f"check2_{bundle_id}"
    )
    
    # Duplicate check (conditional)
    if duplicates:
        if duplicates_reviewed:
            check3 = st.checkbox(
                f"All duplicate project issues have been reviewed and resolved ✅",
                value=True,
                disabled=True,
                key=f"check3_{bundle_id}"
            )
        else:
            st.warning(f"⚠️ **{len(duplicates)} duplicate project(s) detected** - Must be reviewed before approval")
            check3 = st.checkbox(
                f"All duplicate project issues have been reviewed and resolved",
                value=False,
                disabled=True,
                key=f"check3_{bundle_id}"
            )
            st.caption("👆 Please scroll up and mark duplicates as reviewed first")
    else:
        check3 = True  # No duplicates, auto-pass
    
    check4 = st.checkbox(
        "Pricing and delivery terms are acceptable",
        key=f"check4_{bundle_id}"
    )
    
    st.markdown("---")
    
    # Validation
    all_checked = check1 and check2 and check3 and check4
    
    col1, col2 = st.columns(2)
    with col1:
        if all_checked:
            if st.button("✅ Confirm & Approve Bundle", key=f"confirm_approve_{bundle_id}", type="primary"):
                mark_bundle_approved(db, bundle_id)
                del st.session_state[f'approving_bundle_{bundle_id}']
                st.success(f"✅ Bundle approved with {vendor_name}!")
                st.rerun()
        else:
            st.button("✅ Confirm & Approve Bundle", key=f"confirm_approve_{bundle_id}", disabled=True)
            if not check3 and duplicates and not duplicates_reviewed:
                st.caption("⚠️ Review duplicates before approving")
            else:
                st.caption("⚠️ Please confirm all items above")
    
    with col2:
        if st.button("Cancel", key=f"cancel_approve_{bundle_id}"):
            del st.session_state[f'approving_bundle_{bundle_id}']
            st.rerun()

def display_issue_resolution_flow(db, bundle, bundle_items):
    """Display UI flow for resolving bundle issues (vendor can't supply items)"""
    st.subheader("⚠️ Report Bundle Issue")
    
    bundle_id = bundle['bundle_id']
    vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
    vendor_id = bundle.get('recommended_vendor_id')
    
    # Step 1: Select problematic items
    if not st.session_state.get(f'selected_problem_items_{bundle_id}'):
        st.write(f"**Which items can {vendor_name} NOT provide?**")
        st.caption("Select items that are unavailable from this vendor")
        
        selected_items = []
        for item in bundle_items:
            if st.checkbox(
                f"{item['item_name']} ({item['total_quantity']} pcs)",
                key=f"issue_item_{bundle_id}_{item['item_id']}"
            ):
                selected_items.append(item['item_id'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Find Alternative Vendors", key=f"find_alt_{bundle_id}", type="primary"):
                if selected_items:
                    st.session_state[f'selected_problem_items_{bundle_id}'] = selected_items
                    st.rerun()
                else:
                    st.warning("Please select at least one item")
        with col2:
            if st.button("Cancel", key=f"cancel_issue_{bundle_id}"):
                del st.session_state[f'reporting_issue_{bundle_id}']
                st.rerun()
    
    # Step 2: Show alternative vendors for each selected item
    else:
        selected_item_ids = st.session_state[f'selected_problem_items_{bundle_id}']
        
        for item in bundle_items:
            if item['item_id'] in selected_item_ids:
                st.markdown(f"### 🔄 Alternative Vendors for {item['item_name']}")
                st.write(f"Current: **{vendor_name}** ❌ Not available")
                
                # Get alternative vendors
                alt_vendors = db.get_alternative_vendors_for_item(item['item_id'], vendor_id)
                
                if alt_vendors:
                    st.write("**Select new vendor:**")
                    
                    for vendor in alt_vendors:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{vendor['vendor_name']}**")
                            if vendor.get('vendor_email'):
                                st.write(f"📧 {vendor['vendor_email']}")
                            if vendor.get('vendor_phone'):
                                st.write(f"📞 {vendor['vendor_phone']}")
                        with col2:
                            if st.button(
                                "Move Here",
                                key=f"move_{bundle_id}_{item['item_id']}_{vendor['vendor_id']}"
                            ):
                                # Move item to this vendor
                                result = db.move_item_to_vendor(
                                    bundle_id,
                                    item['item_id'],
                                    vendor['vendor_id']
                                )
                                
                                if result['success']:
                                    st.success(f"✅ {result['message']}")
                                    # Clear session state
                                    del st.session_state[f'reporting_issue_{bundle_id}']
                                    del st.session_state[f'selected_problem_items_{bundle_id}']
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed: {result.get('error')}")
                        
                        st.markdown("---")
                else:
                    st.warning(f"⚠️ No alternative vendors found for {item['item_name']}")
        
        if st.button("← Back", key=f"back_issue_{bundle_id}"):
            del st.session_state[f'selected_problem_items_{bundle_id}']
            st.rerun()

def display_order_placement_form(db, bundle):
    """Display form for placing order (PO number + item costs)"""
    st.subheader("📦 Order Placement")
    
    bundle_id = bundle['bundle_id']
    vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
    
    st.write(f"**Place order with {vendor_name}**")
    st.caption("Enter PO number and unit costs for all items")
    
    # Get items with current costs
    items = db.get_bundle_item_costs(bundle_id)
    
    if not items:
        st.error("No items found in bundle")
        return
    
    # PO Number input
    po_number = st.text_input(
        "PO Number *",
        key=f"po_number_{bundle_id}",
        placeholder="e.g., PO-2025-001"
    )
    
    # Expected Delivery Date input
    from datetime import datetime, date
    expected_delivery = st.date_input(
        "Expected Delivery Date *",
        key=f"delivery_date_{bundle_id}",
        value=date.today(),  # Default to today
        min_value=date.today(),  # No past dates
        help="When do you expect this order to be delivered?"
    )
    
    st.markdown("---")
    st.write("**Enter unit costs for each item:**")
    
    # Store costs in session state
    if f'item_costs_{bundle_id}' not in st.session_state:
        st.session_state[f'item_costs_{bundle_id}'] = {}
    
    # Display each item with cost input
    for item in items:
        st.markdown(f"**{item['item_name']}** ({item['total_quantity']} pieces)")
        
        # Show last recorded cost
        if item.get('cost'):
            last_cost = f"${item['cost']:.2f}"
            if item.get('last_cost_update'):
                update_date = item['last_cost_update'].strftime('%Y-%m-%d') if hasattr(item['last_cost_update'], 'strftime') else str(item['last_cost_update'])[:10]
                st.caption(f"Last recorded cost: {last_cost} (updated: {update_date})")
            else:
                st.caption(f"Last recorded cost: {last_cost}")
        else:
            st.caption("Last recorded cost: N/A")
        
        # Cost input
        # If item has existing cost, pre-fill it. Otherwise start with min value
        if item.get('cost') and item['cost'] > 0:
            default_value = float(item['cost'])
        else:
            # No existing cost - use placeholder text to indicate operator must enter
            default_value = None
        
        cost_value = st.number_input(
            f"Unit Cost ($) *",
            min_value=0.01,
            step=0.01,
            format="%.2f",
            key=f"cost_{bundle_id}_{item['item_id']}",
            value=default_value,
            placeholder="Enter cost per unit"
        )
        
        st.session_state[f'item_costs_{bundle_id}'][item['item_id']] = cost_value if cost_value else 0.0
        st.markdown("---")
    
    # Validation and save
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirm Order Placement", key=f"confirm_order_{bundle_id}", type="primary"):
            # Validate
            if not po_number or not po_number.strip():
                st.error("⚠️ PO Number is required")
            elif not expected_delivery:
                st.error("⚠️ Expected Delivery Date is required")
            elif any(cost <= 0 for cost in st.session_state[f'item_costs_{bundle_id}'].values()):
                st.error("⚠️ All item costs must be greater than 0")
            else:
                # Save order
                result = db.save_order_placement(
                    bundle_id,
                    po_number.strip(),
                    expected_delivery,
                    st.session_state[f'item_costs_{bundle_id}']
                )
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    # Clean up session state
                    del st.session_state[f'placing_order_{bundle_id}']
                    del st.session_state[f'item_costs_{bundle_id}']
                    st.rerun()
                else:
                    st.error(f"❌ Failed: {result.get('error')}")
    
    with col2:
        if st.button("Cancel", key=f"cancel_order_{bundle_id}"):
            del st.session_state[f'placing_order_{bundle_id}']
            if f'item_costs_{bundle_id}' in st.session_state:
                del st.session_state[f'item_costs_{bundle_id}']
            st.rerun()

def display_completion_form(db, bundle):
    """Display form for marking bundle as completed (with packing slip)"""
    st.subheader("📦 Confirm Delivery")
    
    bundle_id = bundle['bundle_id']
    vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
    
    st.write(f"**Confirm delivery from {vendor_name}**")
    st.caption("Enter delivery date to complete this bundle")
    
    # PACKING SLIP - HIDDEN (Can reactivate if needed in future)
    # packing_slip = st.text_input(
    #     "Packing Slip Code *",
    #     key=f"packing_slip_{bundle_id}",
    #     placeholder="e.g., PS-12345, PKG/2025/001, SLIP-ABC-123",
    #     help="Enter the packing slip code from the delivery. Can include letters, numbers, and symbols."
    # )
    # st.caption("**Examples:** PS-12345, PKG/2025/001, SLIP-ABC-123, or any format from your vendor")
    packing_slip = None  # Not collecting packing slip for now
    
    # Actual delivery date input
    from datetime import date
    actual_delivery = st.date_input(
        "Actual Delivery Date *",
        key=f"actual_delivery_{bundle_id}",
        value=date.today(),  # Default to today
        max_value=date.today(),  # No future dates
        help="When did the items actually arrive?"
    )
    
    # Validation and save
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirm Completion", key=f"confirm_complete_{bundle_id}", type="primary"):
            # Validate
            if not actual_delivery:
                st.error("⚠️ Actual delivery date is required")
            else:
                # Mark as completed with delivery date (packing slip hidden)
                result = mark_bundle_completed_with_packing_slip(
                    db, 
                    bundle_id, 
                    None,  # Packing slip hidden - pass None
                    actual_delivery
                )
                
                if result['success']:
                    st.success(f"✅ Bundle marked as completed!")
                    # Clean up session state
                    del st.session_state[f'completing_bundle_{bundle_id}']
                    st.rerun()
                else:
                    st.error(f"❌ Failed: {result.get('error')}")
    
    with col2:
        if st.button("Cancel", key=f"cancel_complete_{bundle_id}"):
            del st.session_state[f'completing_bundle_{bundle_id}']
            st.rerun()

def display_analytics_dashboard(db):
    """Analytics Dashboard with simple, meaningful insights"""
    st.header("📊 Analytics Dashboard")
    st.caption("Understand your procurement patterns and optimize operations")
    
    try:
        # Date range selector
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Showing data from the last 30 days**")
        with col2:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        st.markdown("---")
        
        # Analytics Section 1: Request Status Overview
        st.subheader("📋 Request Status Overview")
        st.caption("💡 **What this shows:** Current state of all requests - helps you see what needs attention")
        
        status_query = """
        SELECT status, COUNT(*) as count
        FROM requirements_orders
        WHERE created_at >= DATEADD(day, -30, GETDATE())
        GROUP BY status
        ORDER BY count DESC
        """
        status_data = db.execute_query(status_query)
        
        if status_data:
            cols = st.columns(len(status_data))
            for idx, row in enumerate(status_data):
                with cols[idx]:
                    icon = "🟡" if row['status'] == 'Pending' else "🔵" if row['status'] == 'In Progress' else "✅" if row['status'] == 'Ordered' else "🎉"
                    st.metric(f"{icon} {row['status']}", row['count'])
            
            st.caption("**💬 What to do:** If too many 'Pending' requests, process them faster. If too many 'In Progress', check for bottlenecks.")
        else:
            st.info("No request data available for the last 30 days")
        
        st.markdown("---")
        
        # Analytics Section 2: Top Requested Items
        st.subheader("📦 Top Requested Items")
        st.caption("💡 **What this shows:** Most popular items - consider keeping these in stock or negotiating bulk prices")
        
        top_items_query = """
        SELECT TOP 10
            i.item_name,
            COUNT(DISTINCT roi.req_id) as request_count,
            SUM(roi.quantity) as total_quantity
        FROM requirements_order_items roi
        JOIN Items i ON roi.item_id = i.item_id
        JOIN requirements_orders ro ON roi.req_id = ro.req_id
        WHERE ro.created_at >= DATEADD(day, -30, GETDATE())
        GROUP BY i.item_name
        ORDER BY request_count DESC
        """
        top_items = db.execute_query(top_items_query)
        
        if top_items:
            for idx, item in enumerate(top_items, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    # Use HTML to avoid Markdown parsing issues with special characters in item names
                    st.markdown(f"<b>{idx}. {item['item_name']}</b>", unsafe_allow_html=True)
                with col2:
                    st.write(f"{item['request_count']} requests")
                with col3:
                    st.write(f"{item['total_quantity']} pcs")
            
            st.caption(f"**💬 Action:** Top item '{top_items[0]['item_name']}' was requested {top_items[0]['request_count']} times. Consider bulk ordering or keeping in stock.")
        else:
            st.info("No item data available")
        
        st.markdown("---")
        
        # Analytics Section 3: Most Used Vendors
        st.subheader("🏪 Most Used Vendors")
        st.caption("💡 **What this shows:** Which vendors you order from most - use this for price negotiations")
        
        vendor_query = """
        SELECT TOP 10
            v.vendor_name,
            COUNT(*) as order_count,
            CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM requirements_bundles WHERE status IN ('Ordered', 'Completed')) AS INT) as percentage
        FROM requirements_bundles b
        JOIN Vendors v ON b.recommended_vendor_id = v.vendor_id
        WHERE b.status IN ('Ordered', 'Completed')
        GROUP BY v.vendor_name
        ORDER BY order_count DESC
        """
        vendor_data = db.execute_query(vendor_query)
        
        if vendor_data:
            for idx, vendor in enumerate(vendor_data, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{idx}. {vendor['vendor_name']}**")
                with col2:
                    st.write(f"{vendor['order_count']} orders")
                with col3:
                    st.write(f"{vendor['percentage']}%")
            
            st.caption(f"**💬 Action:** '{vendor_data[0]['vendor_name']}' gets {vendor_data[0]['percentage']}% of your orders. Negotiate volume discounts!")
        else:
            st.info("No vendor data available")
        
        st.markdown("---")
        
        # Analytics Section 4: Items by Vendor
        st.subheader("📋 Items by Vendor")
        st.caption("💡 **What this shows:** What each vendor supplies most - helps find cheaper alternatives")
        
        # Vendor selector
        if vendor_data:
            selected_vendor = st.selectbox(
                "Select a vendor to see their most supplied items:",
                [v['vendor_name'] for v in vendor_data]
            )
            
            items_by_vendor_query = """
            SELECT TOP 5
                i.item_name,
                COUNT(*) as times_ordered,
                SUM(bi.total_quantity) as total_pieces
            FROM requirements_bundle_items bi
            JOIN requirements_bundles b ON bi.bundle_id = b.bundle_id
            JOIN Vendors v ON b.recommended_vendor_id = v.vendor_id
            JOIN Items i ON bi.item_id = i.item_id
            WHERE b.status IN ('Ordered', 'Completed')
                AND v.vendor_name = ?
            GROUP BY i.item_name
            ORDER BY times_ordered DESC
            """
            vendor_items = db.execute_query(items_by_vendor_query, (selected_vendor,))
            
            if vendor_items:
                st.write(f"**Top items from {selected_vendor}:**")
                for idx, item in enumerate(vendor_items, 1):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"{idx}. {item['item_name']}")
                    with col2:
                        st.write(f"{item['times_ordered']}× ordered")
                    with col3:
                        st.write(f"{item['total_pieces']} pcs")
                
                st.caption(f"**💬 Action:** Check if other vendors offer '{vendor_items[0]['item_name']}' at better prices.")
            else:
                st.info(f"No items found for {selected_vendor}")
        
        st.markdown("---")
        
        # Analytics Section 5: Recent Cost Updates
        st.subheader("💰 Recent Cost Updates")
        st.caption("💡 **What this shows:** Latest price changes - monitor for price increases")
        
        cost_query = """
        SELECT TOP 10
            i.item_name,
            v.vendor_name,
            ivm.cost,
            ivm.last_cost_update
        FROM ItemVendorMap ivm
        JOIN Items i ON ivm.item_id = i.item_id
        JOIN Vendors v ON ivm.vendor_id = v.vendor_id
        WHERE ivm.last_cost_update IS NOT NULL
        ORDER BY ivm.last_cost_update DESC
        """
        cost_data = db.execute_query(cost_query)
        
        if cost_data:
            for item in cost_data:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{item['item_name']}**")
                with col2:
                    st.write(f"{item['vendor_name']}")
                with col3:
                    update_date = item['last_cost_update'].strftime('%b %d') if hasattr(item['last_cost_update'], 'strftime') else str(item['last_cost_update'])[:10]
                    st.write(f"${item['cost']:.2f}")
                st.caption(f"   Updated: {update_date}")
            
            st.caption("**💬 Action:** If prices increased, check alternative vendors for better rates.")
        else:
            st.info("No cost data available")
        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def display_user_interface(db):
    """Regular user interface for non-operator users"""
    st.header("🏠 User Dashboard")
    st.write("Browse items and manage your requests")
    
    # Add user interface tabs here
    tab1, tab2 = st.tabs(["🛒 Browse Items", "📋 My Requests"])
    
    with tab1:
        st.info("Item browsing interface would go here")
    
    with tab2:
        display_user_requests(db)

def display_user_requests(db):
    """Display user's requests with order status and PO numbers"""
    user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.warning("Please log in to view your requests")
        return
    
    try:
        # Get user's requests
        query = """
        SELECT 
            ro.req_id,
            ro.req_number,
            ro.status,
            ro.created_at
        FROM requirements_orders ro
        WHERE ro.user_id = ?
        ORDER BY ro.created_at DESC
        """
        requests = db.execute_query(query, (user_id,))
        
        if not requests:
            st.info("You haven't submitted any requests yet")
            return
        
        st.write(f"**Your Requests ({len(requests)})**")
        
        for req in requests:
            with st.expander(f"📋 Request #{req['req_number']} - {req['status']}", expanded=False):
                # Get items for this request
                items_query = """
                SELECT i.item_name, roi.quantity
                FROM requirements_order_items roi
                JOIN Items i ON roi.item_id = i.item_id
                WHERE roi.req_id = ?
                """
                items = db.execute_query(items_query, (req['req_id'],))
                
                st.write("**Items:**")
                for item in items or []:
                    st.write(f"• {item['item_name']} ({item['quantity']} pcs)")
                
                # Get bundles for this request
                bundles_query = """
                SELECT DISTINCT
                    b.bundle_id,
                    b.bundle_name,
                    b.status,
                    b.po_number,
                    b.po_date,
                    b.expected_delivery_date
                FROM requirements_bundle_mapping rbm
                JOIN requirements_bundles b ON rbm.bundle_id = b.bundle_id
                WHERE rbm.req_id = ?
                ORDER BY b.bundle_id
                """
                bundles = db.execute_query(bundles_query, (req['req_id'],))
                
                if bundles:
                    st.markdown("---")
                    
                    # Count ordered bundles
                    ordered_count = sum(1 for b in bundles if b['status'] in ('Ordered', 'Completed'))
                    total_count = len(bundles)
                    
                    # Show message based on number of bundles and status
                    if len(bundles) > 1:
                        st.write(f"**Your items are being sourced from {len(bundles)} bundles:**")
                        
                        # Show progress message
                        if ordered_count == 0:
                            st.caption("⏳ Orders are being processed...")
                        elif ordered_count < total_count:
                            st.info(f"📦 {ordered_count} of {total_count} orders placed")
                        else:
                            st.success(f"✅ All items ordered! {total_count} PO(s) issued")
                    else:
                        st.write("**Order Status:**")
                    
                    for idx, bundle in enumerate(bundles, 1):
                        status_icon = "✅" if bundle['status'] == 'Ordered' else "⏳"
                        
                        # Get items in this bundle for this request
                        bundle_items_query = """
                        SELECT DISTINCT
                            i.item_name,
                            roi.quantity
                        FROM requirements_order_items roi
                        JOIN Items i ON roi.item_id = i.item_id
                        JOIN requirements_bundle_items bi ON roi.item_id = bi.item_id
                        WHERE roi.req_id = ? AND bi.bundle_id = ?
                        """
                        bundle_items = db.execute_query(bundle_items_query, (req['req_id'], bundle['bundle_id']))
                        
                        # Display bundle info
                        st.write(f"{status_icon} **Bundle {idx} - {bundle['status']}**")
                        
                        # Show PO number if ordered
                        if bundle['status'] == 'Ordered' and bundle.get('po_number'):
                            st.write(f"   📦 PO#: {bundle['po_number']}")
                            if bundle.get('po_date'):
                                po_date = bundle['po_date'].strftime('%Y-%m-%d') if hasattr(bundle['po_date'], 'strftime') else str(bundle['po_date'])[:10]
                                st.write(f"   📅 Order Date: {po_date}")
                        
                        # Show items in this bundle
                        if bundle_items:
                            items_text = ", ".join([f"{bi['item_name']} ({bi['quantity']} pcs)" for bi in bundle_items])
                            st.write(f"   📋 Items: {items_text}")
                        
                        st.write("")  # Add spacing between bundles
                
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")

def display_bundle_overview(db):
    """Display overview of all bundles"""
    st.header("📦 Bundle Overview")
    
    try:
        # Get all bundles
        bundles = get_all_bundles(db)
        
        if not bundles:
            st.info("No bundles created yet. Use 'Manual Bundling' to create the first bundle.")
            return
        
        # Display bundles in a table format
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Bundles", len(bundles))
        
        with col2:
            active_bundles = [b for b in bundles if b['status'] == 'Active']
            st.metric("Active Bundles", len(active_bundles))
        
        with col3:
            completed_bundles = [b for b in bundles if b['status'] == 'Completed']
            st.metric("Completed Bundles", len(completed_bundles))
        
        st.markdown("---")
        
        # Display each bundle
        for bundle in bundles:
            with st.expander(f"📦 {bundle['bundle_name']} - {get_status_badge(bundle['status'])}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Bundle ID:** {bundle['bundle_id']}")
                    st.write(f"**Status:** {get_status_badge(bundle['status'])}")
                    if bundle.get('created_at'):
                        st.write(f"**Created:** {bundle['created_at']}")
                    if bundle.get('total_items'):
                        st.write(f"**Total Items:** {bundle['total_items']}")
                    if bundle.get('total_quantity'):
                        st.write(f"**Total Quantity:** {bundle['total_quantity']}")
                
                with col2:
                    # Show vendor recommendations if available
                    if bundle.get('vendor_info'):
                        try:
                            vendor_data = json.loads(bundle['vendor_info'])  # Parse JSON properly
                            if vendor_data and len(vendor_data) > 0:
                                st.write("**Top Vendor Recommendation:**")
                                top_vendor = vendor_data[0]
                                st.write(f"• {top_vendor['vendor_name']} ({top_vendor.get('coverage_percentage', 'N/A')}% coverage)")
                                st.write(f"• Contact: {top_vendor['contact_email']}")
                                st.write(f"• Items: {top_vendor.get('items_covered', 'N/A')}")
                        except:
                            st.write("**Vendor Info:** Available in details")
                    else:
                        st.write("**Bundle Items:**")
                        # Get bundle items
                        items_query = """
                        SELECT bi.item_id, bi.total_quantity as quantity, i.item_name
                        FROM requirements_bundle_items bi
                        JOIN Items i ON bi.item_id = i.item_id
                        WHERE bi.bundle_id = ?
                        """
                        try:
                            bundle_items = db.execute_query(items_query, (bundle['bundle_id'],))
                            if bundle_items:
                                for item in bundle_items:
                                    st.write(f"• {item['item_name']}: {item['quantity']} pieces")
                            else:
                                st.write("No items found")
                        except:
                            st.write("Items info not available")
                
                # Action buttons
                if bundle['status'] == 'Active':
                    if st.button(f"✅ Mark as Completed", key=f"complete_{bundle['bundle_id']}"):
                        mark_bundle_completed(db, bundle['bundle_id'])
                        st.success("Bundle marked as completed!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"Error loading bundles: {str(e)}")

def display_manual_bundling(db):
    """Manual bundling trigger for operators"""
    st.header("🤖 Manual Bundling")
    st.write("Trigger the smart bundling process manually")
    
    # Show current pending requests
    try:
        pending_requests = db.get_all_pending_requests()
        
        if not pending_requests:
            st.info("No pending requests available for bundling.")
            return
        
        # Group by request for display
        requests_by_id = {}
        for req in pending_requests:
            req_id = req['req_id']
            if req_id not in requests_by_id:
                requests_by_id[req_id] = {
                    'req_number': req['req_number'],
                    'user_id': req['user_id'],
                    'req_date': req['req_date'],
                    'items': []
                }
            requests_by_id[req_id]['items'].append({
                'item_name': req['item_name'],
                'quantity': req['quantity'],
                'source_sheet': req['source_sheet']
            })
        
        st.write(f"**Found {len(requests_by_id)} pending requests with {len(pending_requests)} items:**")
        
        # Display pending requests
        for req_id, req_data in requests_by_id.items():
            with st.expander(f"📋 {req_data['req_number']} - User {req_data['user_id']}", expanded=False):
                for item in req_data['items']:
                    st.write(f"• {item['item_name']} - {item['quantity']} pieces ({item['source_sheet']})")
        
        st.markdown("---")
        
        # Bundling button
        if st.button("🚀 Run Smart Bundling", type="primary"):
            with st.spinner("Running smart bundling process..."):
                engine = SmartBundlingEngine()
                result = engine.run_bundling_process()
                
                if result['success']:
                    st.success("🎉 Bundling completed successfully!")
                    
                    # Display results
                    st.write(f"**Total Bundles Created:** {result.get('total_bundles', 0)}")
                    st.write(f"**Requests Processed:** {result.get('total_requests', 0)}")
                    st.write(f"**Total Items:** {result.get('total_items', 0)}")
                    st.write(f"**Coverage:** {result.get('coverage_percentage', 0):.1f}%")
                    
                    # Show debug information if available
                    debug_info = result.get('debug_info', {})
                    if debug_info:
                        st.markdown("---")
                        st.subheader("🔍 DEBUG VIEW - Bundling Analysis")
                        st.caption("(This detailed view will be removed in production)")
                        
                        # Items Analysis
                        if 'items_analysis' in debug_info:
                            st.write("**1. Items and Their Vendors:**")
                            for item_id, item_info in debug_info['items_analysis'].items():
                                with st.expander(f"📦 {item_info['item_name']} ({item_info['quantity']} pieces)", expanded=False):
                                    st.write(f"**Item ID:** {item_id}")
                                    st.write(f"**Available Vendors:** {item_info['vendor_count']}")
                                    for vendor_name in item_info['vendors']:
                                        st.write(f"• {vendor_name}")
                        
                        # Vendor Coverage Analysis
                        if 'vendor_coverage_analysis' in debug_info:
                            st.write("**2. Vendor Coverage Analysis:**")
                            for vendor_id, vendor_info in debug_info['vendor_coverage_analysis'].items():
                                with st.expander(f"🏪 {vendor_info['vendor_name']} - {vendor_info['coverage_percentage']:.1f}% coverage", expanded=False):
                                    st.write(f"**Vendor ID:** {vendor_id}")
                                    st.write(f"**Items Covered:** {vendor_info['items_count']}")
                                    st.write(f"**Total Pieces:** {vendor_info['total_pieces']}")
                                    st.write(f"**Contact:** {vendor_info['contact_email']}")
                                    st.write(f"**Phone:** {vendor_info['contact_phone']}")
                                    st.write("**Items this vendor can supply:**")
                                    for item in vendor_info['items_covered']:
                                        st.write(f"• {item['item_name']} ({item['quantity']} pieces)")
                        
                        # Bundle Creation Strategy
                        if 'coverage_strategy' in debug_info:
                            st.write("**3. Bundle Creation Strategy:**")
                            for strategy in debug_info['coverage_strategy']:
                                with st.expander(f"Bundle {strategy['bundle_number']}: {strategy['vendor_name']}", expanded=True):
                                    st.write(f"**Vendor:** {strategy['vendor_name']} (ID: {strategy['vendor_id']})")
                                    st.write(f"**Contact:** {strategy['contact_email']}")
                                    st.write(f"**Phone:** {strategy['contact_phone']}")
                                    st.write(f"**Items Covered:** {strategy['items_covered']}")
                                    st.write(f"**Total Pieces:** {strategy['total_pieces']}")
                                    st.write("**Items in this bundle:**")
                                    for item in strategy['items_list']:
                                        st.write(f"• {item['item_name']} - {item['quantity']} pieces")
                    
                    st.markdown("---")
                    st.write("**Created Bundles:**")
                    for i, bundle in enumerate(result.get('bundles_created', []), 1):
                        st.write(f"{i}. **{bundle['bundle_name']}**")
                        st.write(f"   • Vendor: {bundle['vendor_name']}")
                        st.write(f"   • Items: {bundle['items_count']}, Quantity: {bundle['total_quantity']}")
                        st.write("")
                    
                    st.info("All pending requests have been moved to 'In Progress' status. Users can no longer modify these requests.")
                    
                else:
                    st.error(f"❌ Bundling failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Error in manual bundling: {str(e)}")

def display_bundle_details(db):
    """Display detailed view of a specific bundle"""
    st.header("🔍 Bundle Details")
    
    try:
        bundles = get_all_bundles(db)
        
        if not bundles:
            st.info("No bundles available.")
            return
        
        # Bundle selection
        bundle_options = [f"{b['bundle_name']} ({b['status']})" for b in bundles]
        selected_bundle_name = st.selectbox("Select a bundle:", bundle_options)
        
        if selected_bundle_name:
            # Find selected bundle
            bundle_name = selected_bundle_name.split(' (')[0]
            selected_bundle = next((b for b in bundles if b['bundle_name'] == bundle_name), None)
            
            if selected_bundle:
                # Display bundle details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Bundle ID:** {selected_bundle['bundle_id']}")
                    st.write(f"**Name:** {selected_bundle['bundle_name']}")
                    st.write(f"**Status:** {get_status_badge(selected_bundle['status'])}")
                    if selected_bundle.get('created_at'):
                        st.write(f"**Created:** {selected_bundle['created_at']}")
                
                with col2:
                    if selected_bundle.get('total_items'):
                        st.write(f"**Total Items:** {selected_bundle['total_items']}")
                    if selected_bundle.get('total_quantity'):
                        st.write(f"**Total Quantity:** {selected_bundle['total_quantity']}")
                    
                    # Show related requests count
                    try:
                        requests_query = """
                        SELECT COUNT(*) as count 
                        FROM requirements_bundle_mapping 
                        WHERE bundle_id = ?
                        """
                        req_result = db.execute_query(requests_query, (selected_bundle['bundle_id'],))
                        req_count = req_result[0]['count'] if req_result else 0
                        st.write(f"**Related Requests:** {req_count}")
                    except:
                        pass
                
                # Show vendor recommendations
                if selected_bundle.get('vendor_info'):
                    try:
                        vendor_data = json.loads(selected_bundle['vendor_info'])
                        
                        st.markdown("---")
                        st.subheader("🏪 Vendor Recommendations")
                        
                        for i, vendor in enumerate(vendor_data, 1):
                            with st.expander(f"{i}. {vendor['vendor_name']} - {vendor.get('coverage_percentage', 'N/A')}% coverage"):
                                st.write(f"**Contact Email:** {vendor['contact_email']}")
                                st.write(f"**Contact Phone:** {vendor['contact_phone']}")
                                st.write(f"**Items Covered:** {vendor.get('items_covered', 'N/A')}")
                                st.write(f"**Total Quantity:** {vendor['total_quantity']}")
                                
                                st.write("**Items List:**")
                                for item in vendor.get('items_list', []):
                                    st.write(f"• {item['item_name']} - {item['quantity']} pieces")
                    
                    except Exception as e:
                        st.write(f"Error displaying vendor info: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading bundle details: {str(e)}")

def display_system_status(db):
    """Display system status and statistics"""
    st.header("📊 System Status")
    
    try:
        # Get statistics
        pending_requests = db.get_all_pending_requests()
        bundles = get_all_bundles(db)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pending_count = len(set([req['req_id'] for req in pending_requests]))
            st.metric("Pending Requests", pending_count)
        
        with col2:
            active_bundles = [b for b in bundles if b['status'] == 'Active']
            st.metric("Active Bundles", len(active_bundles))
        
        with col3:
            completed_bundles = [b for b in bundles if b['status'] == 'Completed']
            st.metric("Completed Bundles", len(completed_bundles))
        
        with col4:
            total_items = sum(req['quantity'] for req in pending_requests)
            st.metric("Pending Items", total_items)
        
        # Database connection status
        st.markdown("---")
        st.subheader("🔗 Database Status")
        
        is_connected, message, _, _ = db.check_db_connection()
        if is_connected:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")
    
    except Exception as e:
        st.error(f"Error loading system status: {str(e)}")

def display_system_reset(db):
    """System reset for testing - clears all Phase 3 data except users"""
    st.header("🧹 System Reset")
    st.caption("⚠️ Testing Tool - Clears all requests, orders, and bundles")
    
    st.warning("""
    **⚠️ WARNING: This will permanently delete:**
    - All user requests and orders
    - All bundles and bundle items
    - All bundle mappings
    - Order status history
    
    **✅ This will preserve:**
    - User accounts and login credentials
    - Phase 2 data (items, vendors, mappings)
    """)
    
    # Show current system state
    try:
        pending_requests = db.get_all_pending_requests()
        bundles = get_all_bundles(db)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            pending_count = len(set([req['req_id'] for req in pending_requests])) if pending_requests else 0
            st.metric("Pending Requests", pending_count)
        
        with col2:
            st.metric("Total Bundles", len(bundles) if bundles else 0)
        
        with col3:
            total_items = sum(req['quantity'] for req in pending_requests) if pending_requests else 0
            st.metric("Total Items", total_items)
        
        st.markdown("---")
        
        # Reset confirmation
        st.subheader("🔄 Reset System")
        
        # Two-step confirmation
        if st.checkbox("I understand this will delete all test data"):
            if st.button("🧹 RESET SYSTEM FOR TESTING", type="primary"):
                with st.spinner("Resetting system..."):
                    try:
                        success = db.reset_system_for_testing()
                        
                        if success:
                            st.success("✅ System reset completed successfully!")
                            st.info("You can now create new test requests and run bundling again.")
                            st.balloons()
                            
                            # Auto-refresh after 2 seconds
                            time.sleep(2)
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ System reset failed: {str(e)}")
        else:
            st.info("Check the box above to enable system reset.")
    
    except Exception as e:
        st.error(f"Error in system reset: {str(e)}")

def get_all_bundles(db):
    """Get all bundles from database"""
    try:
        # Use SELECT * to get all columns including bundle_id
        query = "SELECT * FROM requirements_bundles ORDER BY bundle_id DESC"
        result = db.execute_query(query)
        print(f"DEBUG: get_all_bundles returned {len(result) if result else 0} bundles")
        if result and len(result) > 0:
            print(f"DEBUG: First bundle keys: {list(result[0].keys())}")
        return result
    except Exception as e:
        print(f"Error in get_all_bundles: {str(e)}")
        return []


def fmt_dim(val):
    """Format numeric/string dimension values without trailing zeros.
    Examples: 48.0000 -> '48', 0.1250 -> '0.125'.
    """
    if val is None:
        return ''
    s = str(val).strip()
    if s == '':
        return ''
    try:
        from decimal import Decimal
        d = Decimal(s)
        s = format(d.normalize(), 'f')
    except Exception:
        pass
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s

def get_bundles_with_vendor_info(db):
    """Fetch bundles joined with vendor details in one query (performance optimization)."""
    try:
        query = """
        SELECT 
            b.bundle_id,
            b.bundle_name,
            b.status,
            b.total_items,
            b.total_quantity,
            b.recommended_vendor_id,
            b.duplicates_reviewed,
            b.po_number,
            b.po_date,
            b.expected_delivery_date,
            b.actual_delivery_date,
            b.packing_slip_code,
            b.merge_count,
            b.last_merged_at,
            b.merge_reason,
            v.vendor_name,
            v.vendor_email,
            v.vendor_phone,
            b.created_at,
            b.completed_at,
            b.completed_by,
            b.rejection_reason,
            b.rejected_at
        FROM requirements_bundles b
        LEFT JOIN Vendors v ON b.recommended_vendor_id = v.vendor_id
        ORDER BY b.bundle_id DESC
        """
        return db.execute_query(query)
    except Exception as e:
        print(f"Error in get_bundles_with_vendor_info: {str(e)}")
        return []

def get_bundle_items_for_bundles(db, bundle_ids):
    """Fetch all items for multiple bundles in a single query and return a flat list."""
    try:
        if not bundle_ids:
            return []
        placeholders = ','.join(['?' for _ in bundle_ids])
        query = f"""
        SELECT 
            bi.bundle_id,
            bi.item_id,
            i.item_name,
            i.height,
            i.width,
            i.thickness,
            bi.total_quantity,
            bi.user_breakdown
        FROM requirements_bundle_items bi
        JOIN Items i ON bi.item_id = i.item_id
        WHERE bi.bundle_id IN ({placeholders})
        ORDER BY i.item_name
        """
        return db.execute_query(query, tuple(bundle_ids))
    except Exception as e:
        print(f"Error in get_bundle_items_for_bundles: {str(e)}")
        return []

def get_user_names_map(db, user_ids):
    """Return dict of {user_id: name} for provided user IDs in one query."""
    try:
        if not user_ids:
            return {}
        placeholders = ','.join(['?' for _ in user_ids])
        query = f"""
        SELECT user_id, COALESCE(full_name, username) AS name
        FROM requirements_users
        WHERE user_id IN ({placeholders})
        """
        rows = db.execute_query(query, tuple(user_ids)) or []
        return {row['user_id']: row['name'] for row in rows}
    except Exception as e:
        print(f"Error in get_user_names_map: {str(e)}")
        return {}

def get_bundle_request_numbers_map(db, bundle_ids):
    """Return {bundle_id: [req_number,...]} for provided bundle IDs in one query."""
    try:
        if not bundle_ids:
            return {}
        placeholders = ','.join(['?' for _ in bundle_ids])
        query = f"""
        SELECT m.bundle_id, o.req_number
        FROM requirements_bundle_mapping m
        JOIN requirements_orders o ON m.req_id = o.req_id
        WHERE m.bundle_id IN ({placeholders})
        ORDER BY o.req_number
        """
        rows = db.execute_query(query, tuple(bundle_ids)) or []
        out = {}
        for r in rows:
            out.setdefault(r['bundle_id'], []).append(r['req_number'])
        return out
    except Exception as e:
        print(f"Error in get_bundle_request_numbers_map: {str(e)}")
        return {}

def mark_bundle_completed(db, bundle_id):
    """Mark a bundle as completed and update related requests (with multi-bundle check)"""
    try:
        # Update bundle status
        bundle_query = """
        UPDATE requirements_bundles 
        SET status = 'Completed'
        WHERE bundle_id = ?
        """
        db.execute_insert(bundle_query, (bundle_id,))
        
        # Get all request IDs in this bundle
        mapping_query = """
        SELECT req_id FROM requirements_bundle_mapping 
        WHERE bundle_id = ?
        """
        mappings = db.execute_query(mapping_query, (bundle_id,))
        
        if mappings:
            req_ids = [mapping['req_id'] for mapping in mappings]
            
            # Check each request to see if ALL its bundles are completed
            for req_id in req_ids:
                # Get all bundles for this request
                all_bundles = db.get_bundles_for_request(req_id)
                
                # Check if any bundles are still incomplete
                incomplete_bundles = [b for b in all_bundles if b['status'] != 'Completed']
                
                if len(incomplete_bundles) == 0:
                    # All bundles completed - mark request as completed
                    update_request_query = """
                    UPDATE requirements_orders 
                    SET status = 'Completed'
                    WHERE req_id = ?
                    """
                    db.execute_insert(update_request_query, (req_id,))
                # else: Request still has pending bundles - keep status as 'In Progress'
        
        db.conn.commit()
        return True
        
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise Exception(f"Failed to mark bundle as completed: {str(e)}")

def mark_bundle_completed_with_packing_slip(db, bundle_id, packing_slip_code, actual_delivery_date):
    """Mark a bundle as completed with packing slip code, delivery date, and update related requests"""
    try:
        from datetime import datetime
        
        # Update bundle status with packing slip and delivery date
        bundle_query = """
        UPDATE requirements_bundles 
        SET status = 'Completed',
            packing_slip_code = ?,
            actual_delivery_date = ?,
            completed_at = ?,
            completed_by = ?
        WHERE bundle_id = ?
        """
        completed_at = datetime.now()
        completed_by = st.session_state.get('user_id', 'operator')
        
        db.execute_insert(bundle_query, (packing_slip_code, actual_delivery_date, completed_at, completed_by, bundle_id))
        
        # Get all request IDs in this bundle
        mapping_query = """
        SELECT req_id FROM requirements_bundle_mapping 
        WHERE bundle_id = ?
        """
        mappings = db.execute_query(mapping_query, (bundle_id,))
        
        if mappings:
            req_ids = [mapping['req_id'] for mapping in mappings]
            
            # Check each request to see if ALL its bundles are completed
            for req_id in req_ids:
                # Get all bundles for this request
                all_bundles = db.get_bundles_for_request(req_id)
                
                # Check if any bundles are still incomplete
                incomplete_bundles = [b for b in all_bundles if b['status'] != 'Completed']
                
                if len(incomplete_bundles) == 0:
                    # All bundles completed - mark request as completed
                    update_request_query = """
                    UPDATE requirements_orders 
                    SET status = 'Completed'
                    WHERE req_id = ?
                    """
                    db.execute_insert(update_request_query, (req_id,))
                    
                    # Send email notification to user with ALL bundles data
                    try:
                        from user_notifications import send_user_notification
                        # Get all completed bundles with their details
                        bundles_data = []
                        for bundle in all_bundles:
                            if bundle['status'] == 'Completed':
                                bundles_data.append({
                                    'bundle_id': bundle['bundle_id'],
                                    'vendor_id': bundle['recommended_vendor_id'],
                                    'packing_slip_code': bundle.get('packing_slip_code'),
                                    'actual_delivery_date': bundle.get('actual_delivery_date'),
                                    'po_number': bundle.get('po_number')
                                })
                        
                        send_user_notification(db, req_id, 'completed', {'bundles': bundles_data})
                    except Exception as email_error:
                        # Don't fail the whole operation if email fails
                        print(f"[WARNING] Failed to send email notification: {str(email_error)}")
        
        db.conn.commit()
        return {'success': True, 'message': 'Bundle completed successfully'}
    except Exception as e:
        print(f"Error in mark_bundle_completed_with_packing_slip: {str(e)}")
        if db.conn:
            db.conn.rollback()
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def mark_bundle_approved(db, bundle_id):
    """Mark a bundle as approved by operator"""
    try:
        update_q = """
        UPDATE requirements_bundles
        SET status = 'Approved'
        WHERE bundle_id = ?
        """
        db.execute_insert(update_q, (bundle_id,))
        db.conn.commit()
        return True
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        return False

def get_status_badge(status):
    """Return colored status badge"""
    if status == "Active":
        return "🟡 Active"
    elif status == "Reviewed":
        return "🟢 Reviewed"
    elif status == "Approved":
        return "🔵 Approved"
    elif status == "Ordered":
        return "📦 Ordered"
    elif status == "Completed":
        return "🎉 Completed"
    else:
        return f"⚪ {status}"

if __name__ == "__main__":
    main()
