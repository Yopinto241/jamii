# Jamii Connect Admin Dashboard

A comprehensive React admin dashboard for managing the Jamii Connect USSD marketplace platform.

## Features

### 📊 Dashboard
- **Overview Statistics**: Providers, sellers, revenue, regions, categories, agents, payments
- **Recent Activity**: Latest system activities
- **System Health**: Service status monitoring

### 👥 Provider Management
- **View All Providers**: Complete list with location and subscription details
- **Add Providers**: Bypass payment system, instant activation
- **Delete Providers**: Remove inactive or problematic accounts

### 🛒 Product Provider Management
- **View Product Sellers**: Complete list with product and location details
- **Add Product Sellers**: Direct database insertion
- **Delete Product Sellers**: Account management

### 💰 Payment Monitoring
- **Payment History**: All transactions with status tracking
- **Revenue Analytics**: Financial performance metrics

### 📍 Location Management
- **Regions, Districts, Wards**: Hierarchical location structure
- **Add New Locations**: Expand service coverage areas
- **Visual Organization**: Easy-to-navigate location trees

### 🏷️ Categories & Services
- **Service Categories & Services**: Manage available services
- **Product Categories & Products**: Manage marketplace offerings
- **Add New Items**: Expand platform offerings instantly

### 🗄️ Database Overview
- **Complete Data View**: All tables in one place
- **Tab Navigation**: Switch between different data types
- **Record Counts**: Real-time data statistics
- **Comprehensive Tables**: Full database visibility

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Backend Integration

Ensure your FastAPI backend is running on `http://localhost:8000` with all admin routes enabled.

## API Endpoints Used

### Data Retrieval
- `GET /admin/stats` - Dashboard statistics
- `GET /admin/all-*` - Complete database tables
- `GET /admin/categories` - Category data
- `GET /admin/services/{id}` - Services by category
- `GET /admin/products/{id}` - Products by category
- `GET /admin/regions` - Location hierarchy
- `GET /admin/districts/{id}` - Districts by region
- `GET /admin/wards/{id}` - Wards by district

### Data Modification
- `POST /admin/providers` - Add service provider
- `DELETE /admin/providers/{id}` - Remove provider
- `POST /admin/product-providers` - Add product seller
- `DELETE /admin/product-providers/{id}` - Remove seller
- `POST /admin/add-*` - Add categories, services, locations

## Key Features

### 🔧 Admin Bypass
- **Payment Bypass**: Add providers without mobile money charges
- **Instant Activation**: 30-day free subscription on creation
- **Direct Database Access**: No USSD workflow required

### 📈 Real-time Monitoring
- **Live Statistics**: Auto-updating dashboard metrics
- **Activity Tracking**: Recent system events
- **Health Monitoring**: Service status indicators

### 🎯 Complete Control
- **Full CRUD Operations**: Create, read, update, delete all data
- **Bulk Management**: Efficient data handling
- **Search & Filter**: Easy data navigation

## Technologies Used

- **React 18** - Modern frontend framework
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icons

## Database Tables Managed

- `service_categories` - Service categories
- `services` - Individual services
- `product_categories` - Product categories
- `products` - Individual products
- `regions` - Geographic regions
- `districts` - Districts within regions
- `wards` - Wards within districts
- `providers` - Service providers
- `product_providers` - Product sellers
- `agents` - Commission agents
- `commissions` - Agent earnings
- `payments` - Transaction records

## Security Notes

- **Local Development**: Designed for local development
- **No Authentication**: Add authentication for production
- **Direct Database Access**: Use with caution in production
- **API Security**: Implement proper authentication on backend

---

**Built for Jamii Connect - Complete USSD Marketplace Management** 🚀