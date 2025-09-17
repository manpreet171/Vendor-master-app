# Phase 3: Requirements Management System - Complete Plan

## Overview
Phase 3 introduces a **Requirements Management System** - a shopping cart-style application where users can place material requirements for raw materials. This system allows multiple authenticated users to browse available raw materials, add them to a cart with quantities and needed-by dates, and submit formal requirements that are stored in the database.

## System Architecture

### Application Structure
```
Phase3/
├── app.py                    # Main Streamlit application
├── db_connector.py          # Database connection (extended from Phase 2)
├── user_manager.py          # User authentication and management
├── cart_manager.py          # Shopping cart functionality
├── requirements_manager.py  # Requirements/orders handling
├── utils.py                 # Shared utilities and styling
├── requirements.txt         # Python dependencies
├── packages.txt            # System packages for Streamlit Cloud
├── .env.template           # Environment variables template
└── README.md               # Phase 3 documentation
```

### Database Integration
- **Reuses existing Azure SQL Database** from Phase 2
- **Leverages existing tables**: `items`, `vendors`, `item_vendor_mapping`
- **Filters for Raw Materials**: `source_sheet = 'Raw Materials'`
- **Adds new tables** for user management and requirements

## Database Schema

### Existing Tables (From Phase 2)
These tables will be reused without modification:

```sql
-- Items table (existing)
items (
    item_id INT PRIMARY KEY,
    item_name NVARCHAR(255),
    item_type NVARCHAR(100),
    source_sheet NVARCHAR(50),  -- Filter by 'Raw Materials'
    sku NVARCHAR(100),
    barcode NVARCHAR(100),
    height DECIMAL(10,3),
    width DECIMAL(10,3),
    thickness DECIMAL(10,3)
)

-- Vendors table (existing)
vendors (
    vendor_id INT PRIMARY KEY,
    vendor_name NVARCHAR(255),
    contact_name NVARCHAR(255),
    vendor_email NVARCHAR(255),
    vendor_phone NVARCHAR(50)
)

-- Item-Vendor mapping (existing)
item_vendor_mapping (
    map_id INT PRIMARY KEY,
    item_id INT,
    vendor_id INT,
    cost DECIMAL(10,2)
)
```

### New Tables for Phase 3

#### 1. Users Table
```sql
CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    email NVARCHAR(255),
    department NVARCHAR(100),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    last_login DATETIME2
);
```

#### 2. Requirements Table
```sql
CREATE TABLE requirements (
    req_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    req_number NVARCHAR(20) UNIQUE NOT NULL,  -- Auto-generated: REQ-YYYY-NNNN
    req_date DATE NOT NULL,
    needed_by_date DATE NOT NULL,
    status NVARCHAR(20) DEFAULT 'Pending',    -- Pending, Approved, Ordered, Delivered, Cancelled
    total_items INT DEFAULT 0,
    notes NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### 3. Requirement Items Table
```sql
CREATE TABLE requirement_items (
    req_item_id INT IDENTITY(1,1) PRIMARY KEY,
    req_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity DECIMAL(10,3) NOT NULL,
    unit NVARCHAR(20) NOT NULL,              -- kg, pieces, meters, etc.
    needed_by_date DATE NOT NULL,
    item_notes NVARCHAR(500),
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (req_id) REFERENCES requirements(req_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);
```

#### 4. User Sessions Table (Optional - for enhanced security)
```sql
CREATE TABLE user_sessions (
    session_id NVARCHAR(100) PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    expires_at DATETIME2 NOT NULL,
    is_active BIT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## Application Flow

### 1. User Authentication
- **Login Page**: Username/Password authentication
- **Session Management**: Secure session handling
- **User Registration**: Self-service or admin-managed

### 2. Main Dashboard
- **Welcome Message**: Personalized greeting
- **Quick Stats**: Pending requests, recent activity
- **Navigation**: Browse Materials, My Cart, My Requests

### 3. Browse Raw Materials
- **Material Catalog**: Dropdown/search interface
- **Item Details**: Dimensions, available vendors, pricing
- **Add to Cart**: Quantity input, unit selection, needed-by date

### 4. Shopping Cart Management
- **Cart Review**: List of selected items
- **Edit Items**: Modify quantities, dates, notes
- **Remove Items**: Delete from cart
- **Cart Persistence**: Maintain cart across sessions

### 5. Requirements Submission
- **Review & Confirm**: Final cart review
- **Submit Request**: Generate requirement number
- **Confirmation**: Display request ID and details

### 6. Request Management
- **My Requests**: View submitted requirements
- **Request Details**: Full requirement information
- **Status Tracking**: Current status of each request

## Technical Specifications

### Authentication System
```python
# User authentication flow
def authenticate_user(username, password):
    # Hash password and verify against database
    # Create session state
    # Return user details

def check_session():
    # Verify active session
    # Refresh session if needed
    # Handle session expiry
```

### Cart Management
```python
# Cart item structure
cart_item = {
    'item_id': int,
    'item_name': str,
    'quantity': float,
    'unit': str,
    'needed_by': date,
    'notes': str,
    'dimensions': str,
    'estimated_cost': float
}

# Cart operations
def add_to_cart(item_id, quantity, unit, needed_by, notes)
def update_cart_item(cart_index, updates)
def remove_from_cart(cart_index)
def clear_cart()
```

### Requirements Processing
```python
# Requirement submission
def submit_requirement(user_id, cart_items, general_notes):
    # Generate requirement number
    # Create requirement record
    # Create requirement items
    # Clear user cart
    # Return requirement ID

def get_user_requirements(user_id, status_filter=None)
def get_requirement_details(req_id)
```

## User Interface Design

### Page Structure
1. **Login Page**: Clean, simple authentication
2. **Dashboard**: Overview with quick actions
3. **Browse Materials**: Searchable catalog with filters
4. **Shopping Cart**: Editable cart with totals
5. **My Requests**: Historical requirements list
6. **Request Details**: Individual requirement view

### UI Components
- **Material Selector**: Dropdown with search functionality
- **Quantity Input**: Numeric input with unit selector
- **Date Picker**: Calendar widget for needed-by dates
- **Cart Summary**: Real-time cart totals and item count
- **Status Badges**: Visual status indicators

## Data Validation & Security

### Input Validation
- **Quantities**: Positive numbers only
- **Dates**: Future dates for needed-by
- **Units**: Predefined unit list
- **Text Fields**: Length limits and sanitization

### Security Measures
- **Password Hashing**: Secure password storage
- **SQL Injection Prevention**: Parameterized queries
- **Session Security**: Secure session management
- **User Isolation**: Users see only their own data

## Deployment Configuration

### Streamlit Cloud Setup
```python
# streamlit_app.py (root level launcher)
import os
import sys
import runpy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE3_DIR = os.path.join(BASE_DIR, "Phase3")

if PHASE3_DIR not in sys.path:
    sys.path.insert(0, PHASE3_DIR)

APP_PATH = os.path.join(PHASE3_DIR, "app.py")
runpy.run_path(APP_PATH, run_name="__main__")
```

### Environment Configuration
```bash
# .env.template
AZURE_DB_SERVER=your-server.database.windows.net
AZURE_DB_NAME=your-database-name
AZURE_DB_USERNAME=your-username
AZURE_DB_PASSWORD=your-password
AZURE_DB_DRIVER={ODBC Driver 17 for SQL Server}

# App-specific settings
APP_SECRET_KEY=your-secret-key-for-sessions
DEFAULT_UNITS=kg,pieces,meters,liters,boxes
```

### Streamlit Secrets Configuration
```toml
# .streamlit/secrets.toml
[azure_sql]
AZURE_DB_SERVER = "your-server.database.windows.net"
AZURE_DB_NAME = "your-database-name"
AZURE_DB_USERNAME = "your-username"
AZURE_DB_PASSWORD = "your-password"
AZURE_DB_DRIVER = "ODBC Driver 17 for SQL Server"

[app_config]
SECRET_KEY = "your-secret-key"
DEFAULT_UNITS = ["kg", "pieces", "meters", "liters", "boxes"]
```

## Future Enhancements (Phase 4+)

### Administrative Features
- **Admin Dashboard**: View all user requirements
- **User Management**: Create/manage user accounts
- **Approval Workflow**: Requirement approval process
- **Reporting**: Usage analytics and reports

### Integration Features
- **Vendor Integration**: Send requirements to vendors
- **Email Notifications**: Automated status updates
- **Inventory Management**: Stock level tracking
- **Purchase Orders**: Generate formal POs

### Advanced Features
- **Bulk Upload**: CSV import for large requirements
- **Templates**: Saved requirement templates
- **Cost Estimation**: Real-time pricing
- **Mobile Optimization**: Responsive design

## Success Metrics

### Key Performance Indicators
- **User Adoption**: Number of active users
- **Request Volume**: Requirements submitted per period
- **Processing Time**: Average time from request to fulfillment
- **User Satisfaction**: Feedback and usage patterns

### Technical Metrics
- **Response Time**: Application performance
- **Uptime**: System availability
- **Error Rate**: Application stability
- **Database Performance**: Query execution times

## Implementation Timeline

### Phase 3.1: Core Functionality (Week 1-2)
- Database schema creation
- User authentication system
- Basic cart functionality
- Requirements submission

### Phase 3.2: Enhanced Features (Week 3)
- Request history and tracking
- Improved UI/UX
- Data validation and security
- Testing and deployment

### Phase 3.3: Polish & Optimization (Week 4)
- Performance optimization
- User feedback integration
- Documentation completion
- Production deployment

This comprehensive plan provides the foundation for building a robust requirements management system that integrates seamlessly with the existing Phase 2 infrastructure while providing a modern, user-friendly interface for material requirements processing.
