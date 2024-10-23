
# MATWANA LOGISTIC PARCEL TRACKING SYSTEM

A full-stack logistic parcel tracking system that allows users to send, receive, and track parcels. It features role-based access for customers, customer service, and admins. The system also includes vehicle management, location-based shipping cost calculation, and JWT-based authentication for secure access.

## Features

- **User Roles:** Supports multiple user roles (Customer, Admin, and Customer Service) with different access levels.
- **Parcel Management:** Users can create, view, edit, and delete parcels, with real-time status updates for shipments.
- **Location-Based Shipping:** Shipping costs are calculated based on the origin, destination, and weight of the parcel.
- **Vehicle Management:** Admins can add vehicles and assign them to parcels. The system also tracks the status of vehicles.
- **JWT Authentication:** Secure login, signup, and session management with JWT tokens.
- **Role-Based Authorization:** Different routes and permissions for customers, customer service, and admins.


## Tech Stack

- **Frontend:** React (JavaScript)
- **Backend:** Flask (Python), Flask-RESTful, Flask-JWT-Extended
- **Database:** SQLAlchemy (PostgreSQL/MySQL/SQLite)
- **Styling:** CSS (with custom components)
- **Authentication:** JWT (JSON Web Tokens)
- **Notifications:** `toastify-js` for in-app notifications
- **Other Libraries:**
  - `SQLAlchemy-Serializer` for JSON serialization of models.
  - `werkzeug.security` for password hashing.

### API Endpoints

- `POST /auth/signup`: Register a new user.
- `POST /auth/login`: Login and receive JWT tokens.
- `GET /auth/logout`: Logout the user (JWT invalidation).
- `POST /parcels`: Create a new parcel.
- `GET /parcels`: View all parcels.
- `GET /parcels/:id`: View a specific parcel by its tracking number.
- `PUT /parcels/:id`: Edit an existing parcel.
- `DELETE /parcels/:id`: Delete a parcel.

- `POST /users`: Create a new user.
- `GET /users`: View all users.
- `GET /users/:id`: View a specific user by his/her id.
- `PUT /users/:id`: Edit an existing parcel by its id.
- `DELETE /users/:id`: Delete a user with that id.

- `POST /vehicles`: Create a new vehicle.
- `GET /vehicles`: View all vehicles.
- `GET /vehicles/:id`: View a specific vehicle by its id.
- `PUT /vehicles/:id`: Edit an existing vehicle.
- `DELETE /vehicles/:id`: Delete a vehicle with that specific id.

- `POST /locations`: Create a new location.
- `GET /locations`: View all locations.
- `GET /locations/:id`: View a specific location by its id.
- `PUT /locations/:id`: Edit an existing location.
- `DELETE /loacions/:id`: Deletes a location.

- `GET /assignments/:id`: View a parcel added by the customer service/admin.
- `DELETE /parcels/:id`: Delete a parcel assignment.

### Available User Roles

- **Customer:** Can track parcels.
- **Customer Service:** Can view, assign, and manage parcels.
- **Admin:** Full control over users, parcels, vehicles, and locations.

## Usage

1. **Login as a customer** to view and track parcels.
2. **Login as an admin** to manage users, parcels, vehicles, and locations.
3. **Login as customer service** to manage parcel assignments,vehicles and locations.

### Parcel Tracking

Customers can track their parcels using a unique tracking number or view all parcels in their "Parcels" section. The parcel status will update as it moves through various status.

### Vehicle Management

Admins can add vehicles, assign them to parcels, and update their status (e.g., "In Transit," "Delivered"). Vehicles have details like number plate, capacity, and driver information.

### Location-Based Shipping Costs

Admins can define rates for different origin-destination pairs, and the system will calculate shipping costs based on the weight of the parcel and selected route.

