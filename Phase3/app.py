# Phase 3 Requirements System - Main Application
import streamlit as st
import os
from dotenv import load_dotenv
from db_connector import DatabaseConnector
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
                        
                        # Try to authenticate user
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
    
    # Create sidebar
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
    if st.session_state.user_role == "User":
        # Create tabs - clean and simple
        tab1, tab2, tab3, tab4 = st.tabs(["📦 BoxHero Items", "🔧 Raw Materials", "🛒 My Cart", "📋 My Requests"])
        
        with tab1:
            display_boxhero_tab(db)
        
        with tab2:
            display_raw_materials_tab(db)
        
        with tab3:
            display_cart_tab(db)
        
        with tab4:
            display_my_requests_tab(db)
    
    elif st.session_state.user_role == "Operator":
        st.info("⚙️ **Operator Dashboard** - You can manage bundles and view all requirements")
        
        # Show operator-specific info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Your Role", "Operator")
        
        with col2:
            # Test database connection by counting vendors
            try:
                vendors_query = "SELECT COUNT(*) as count FROM vendors"
                result = db.execute_query(vendors_query)
                vendor_count = result[0]['count'] if result else 0
                st.metric("Available Vendors", vendor_count)
            except Exception as e:
                st.metric("Available Vendors", "Error")
                st.error(f"Database query error: {str(e)}")
        
        with col3:
            st.metric("Status", "Connected" if is_connected else "Disconnected")
    
    
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
        # Get all BoxHero items
        all_items = db.get_all_items(source_filter="BoxHero")
        
        if not all_items:
            st.info("No BoxHero items available at the moment.")
            return
        
        # Filter out items that user has already requested (pending/in-progress)
        requested_item_ids = db.get_user_requested_item_ids(st.session_state.user_id)
        available_items = [item for item in all_items if item['item_id'] not in requested_item_ids]
        
        if not available_items:
            st.info("All BoxHero items are currently in your pending or in-progress requests. Check 'My Requests' tab to manage them.")
            return
        
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
                st.rerun()
        
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
        
        # Step 3: Quantity and Add to Cart
        if st.session_state.bh_step >= 3 and st.session_state.bh_selected_item:
            st.subheader("Step 3: How many do you need?")
            
            # Just show the item name - simple
            st.info(f"Selected: **{st.session_state.bh_selected_item.get('item_name', 'Unknown Item')}**")
            
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
                if st.button("🛒 Add to Cart", type="primary", key="bh_add_to_cart"):
                    result = add_to_cart(st.session_state.bh_selected_item, quantity, "BoxHero")
                    if result == "added":
                        st.success("✅ Added to cart!")
                        # Reset flow for next selection
                        reset_boxhero_flow()
                        st.rerun()
                    # If result is "duplicate_pending" or "duplicate_in_progress", don't rerun - let user see the options
        
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
        # Get all raw materials
        all_items = db.get_all_items(source_filter="Raw Materials")
        
        if not all_items:
            st.info("No raw materials available at the moment.")
            return
        
        # Filter out items that user has already requested (pending/in-progress)
        requested_item_ids = db.get_user_requested_item_ids(st.session_state.user_id)
        available_items = [item for item in all_items if item['item_id'] not in requested_item_ids]
        
        if not available_items:
            st.info("All raw materials are currently in your pending or in-progress requests. Check 'My Requests' tab to manage them.")
            return
        
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
                st.rerun()
        
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
                st.rerun()
        
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
                        height = item.get('height', 'N/A')
                        st.write(f"{height}" if height != 'N/A' else "N/A")
                    
                    with cols[2]:
                        width = item.get('width', 'N/A')
                        st.write(f"{width}" if width != 'N/A' else "N/A")
                    
                    with cols[3]:
                        thickness = item.get('thickness', 'N/A')
                        st.write(f"{thickness}" if thickness != 'N/A' else "N/A")
                    
                    with cols[4]:
                        if st.button(f"Select", key=f"select_variant_{idx}"):
                            st.session_state.rm_selected_item = item
                            st.session_state.rm_step = 4
                            st.rerun()
        
        # Step 4: Quantity and Add to Cart
        if st.session_state.rm_step >= 4 and st.session_state.rm_selected_item:
            st.subheader("Step 4: How many do you need?")
            
            # Just show the material name - simple
            st.info(f"Selected: **{st.session_state.rm_selected_item.get('item_name', 'Unknown Material')}**")
            
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
                if st.button("🛒 Add to Cart", type="primary", key="rm_add_to_cart"):
                    result = add_to_cart(st.session_state.rm_selected_item, quantity, "Raw Materials")
                    if result == "added":
                        st.success("✅ Added to cart!")
                        # Reset flow for next selection
                        reset_raw_materials_flow()
                        st.rerun()
                    # If result is "duplicate_pending" or "duplicate_in_progress", don't rerun - let user see the options
        
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
        height = item.get('height', 'N/A')
        st.metric("Height", f"{height}" if height != 'N/A' else "Not specified")
    
    with dim_col2:
        width = item.get('width', 'N/A')
        st.metric("Width", f"{width}" if width != 'N/A' else "Not specified")
    
    with dim_col3:
        thickness = item.get('thickness', 'N/A')
        st.metric("Thickness", f"{thickness}" if thickness != 'N/A' else "Not specified")

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
            
            # Dimensions if available
            dimensions = []
            if item.get('height'): dimensions.append(f"H: {item['height']}")
            if item.get('width'): dimensions.append(f"W: {item['width']}")
            if item.get('thickness'): dimensions.append(f"T: {item['thickness']}")
            
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

def add_to_cart(item, quantity, category):
    """Add item to cart - simple version"""
    try:
        # Check if item already in current cart
        for cart_item in st.session_state.cart_items:
            if cart_item['item_id'] == item['item_id']:
                # Update quantity if item already exists in cart
                cart_item['quantity'] += quantity
                return "added"
        
        # Add new item to cart
        cart_item = {
            'item_id': item['item_id'],
            'item_name': item.get('item_name', 'Unknown Item'),
            'sku': item.get('sku', ''),
            'category': category,
            'quantity': quantity,
            'item_type': item.get('item_type', '')
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
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{cart_item['item_name']}**")
            st.caption(f"{cart_item['category']} • SKU: {cart_item.get('sku', 'N/A')}")
        
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
        
        with col3:
            st.write(f"{cart_item['quantity']} pcs")
            total_items += cart_item['quantity']
        
        with col4:
            if st.button("Edit", key=f"edit_{i}"):
                # For now, just show current quantity
                st.info(f"Current quantity: {cart_item['quantity']}")
        
        with col5:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.cart_items.pop(i)
                st.rerun()
        
        st.markdown("---")
    
    # Cart summary
    st.subheader("Cart Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Items", f"{len(st.session_state.cart_items)} types")
        st.metric("Total Quantity", f"{total_items} pieces")
    
    with col2:
        # Action buttons
        col_clear, col_submit = st.columns(2)
        
        with col_clear:
            if st.button("Clear Cart", type="secondary"):
                st.session_state.cart_items = []
                st.rerun()
        
        with col_submit:
            if st.button("Submit Request", type="primary"):
                if submit_cart_as_request(db):
                    st.success("🎉 Request submitted successfully!")
                    st.session_state.cart_items = []  # Clear cart after submission
                    st.rerun()

def display_my_requests_tab(db):
    """Display user's past requests and their status"""
    st.header("📋 My Requests")
    st.caption("View your submitted requests and their current status")
    
    try:
        # Get user's requests from database
        user_requests = get_user_requests(db, st.session_state.user_id)
        
        if not user_requests:
            st.info("You haven't submitted any requests yet. Browse items and add them to your cart to get started!")
            return
        
        # Display requests
        for request in user_requests:
            # Format date nicely
            req_date = request.get('req_date', 'Unknown')
            if hasattr(req_date, 'strftime'):
                formatted_date = req_date.strftime('%Y-%m-%d %H:%M')
            else:
                formatted_date = str(req_date)
            
            with st.expander(f"📋 {request['req_number']} - {get_status_badge(request['status'])}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Request Date:** {formatted_date}")
                    st.write(f"**Status:** {get_status_badge(request['status'])}")
                    st.write(f"**Total Items:** {request['total_items']} pieces")
                
                with col2:
                    st.write(f"**Request ID:** {request['req_id']}")
                    if request.get('notes'):
                        st.write(f"**Notes:** {request['notes']}")
                
                # Show items in this request
                request_items = get_request_items(db, request['req_id'])
                if request_items:
                    st.write("**Items in this request:**")
                    for item in request_items:
                        # Build item description with dimensions for Raw Materials
                        item_desc = f"• **{item['item_name']}**"
                        
                        # Add dimensions for Raw Materials
                        if item.get('source_sheet') == 'Raw Materials':
                            dimensions = []
                            if item.get('height'): dimensions.append(f"H: {item['height']}")
                            if item.get('width'): dimensions.append(f"W: {item['width']}")
                            if item.get('thickness'): dimensions.append(f"T: {item['thickness']}")
                            
                            if dimensions:
                                dim_str = " × ".join(dimensions)
                                item_desc += f" ({dim_str})"
                        
                        # Add SKU for BoxHero items
                        elif item.get('source_sheet') == 'BoxHero' and item.get('sku'):
                            item_desc += f" (SKU: {item['sku']})"
                        
                        # Show quantity with edit option for pending requests
                        if request['status'] == 'Pending':
                            col_item, col_qty, col_btn = st.columns([3, 1, 1])
                            with col_item:
                                st.write(item_desc)
                            with col_qty:
                                new_qty = st.number_input(
                                    "Qty", 
                                    min_value=1, 
                                    value=item['quantity'], 
                                    key=f"qty_{request['req_id']}_{item['item_name']}"
                                )
                            with col_btn:
                                if new_qty != item['quantity']:
                                    if st.button("Update", key=f"update_{request['req_id']}_{item['item_name']}"):
                                        try:
                                            success = db.update_order_item_quantity(request['req_id'], item['item_id'], new_qty)
                                            if success:
                                                st.success("✅ Updated!")
                                                st.rerun()
                                            else:
                                                st.error("❌ Failed to update")
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                        else:
                            # For non-pending requests, just show the quantity
                            item_desc += f" - {item['quantity']} pieces"
                            st.write(item_desc)
                else:
                    st.write("*No items found for this request*")
    
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
    SELECT req_id, req_number, req_date, status, total_items, notes
    FROM requirements_orders 
    WHERE user_id = ?
    ORDER BY req_date DESC
    """
    return db.execute_query(query, (user_id,))

def get_request_items(db, req_id):
    """Get items for a specific request with dimensions"""
    query = """
    SELECT ri.quantity, ri.item_notes, i.item_id, i.item_name, i.sku, i.source_sheet,
           i.height, i.width, i.thickness, i.item_type
    FROM requirements_order_items ri
    JOIN items i ON ri.item_id = i.item_id
    WHERE ri.req_id = ?
    """
    return db.execute_query(query, (req_id,))

def submit_cart_as_request(db):
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
        
        # Submit to database
        result = db.submit_cart_as_order(user_id, cart_items)
        
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

if __name__ == "__main__":
    main()
