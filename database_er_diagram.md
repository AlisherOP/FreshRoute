# Food Delivery – Database ER Diagram

Generated from the final `models.py` files (accounts, delivery, customer, restaurants, orders, dashboard).
GitHub renders this automatically; you can also paste the code block into https://mermaid.live.

```mermaid
erDiagram
    users ||--o| customers : "has profile"
    users ||--o| couriers : "has profile"
    users ||--o{ restaurants : owns

    customers ||--o{ saved_addresses : has
    delivery_zones |o--o{ saved_addresses : covers

    restaurants ||--o{ opening_hours : has
    restaurants ||--o{ food_categories : has
    restaurants ||--o{ food_products : sells
    food_categories |o--o{ food_products : groups
    restaurants |o--o{ coupons : offers

    customers ||--o{ orders : places
    restaurants ||--o{ orders : receives
    couriers |o--o{ orders : delivers
    coupons |o--o{ orders : "applied to"

    orders ||--|{ order_items : contains
    food_products ||--o{ order_items : "ordered as"
    orders ||--o| reviews : has
    orders ||--o{ complaints : has

    users {
        bigint id PK
        string username UK
        string email UK
        string role "CUSTOMER, OWNER or COURIER"
        boolean is_staff "site admin"
        boolean is_active
    }

    customers {
        bigint customer_id PK
        bigint user_id FK, UK
        string phone
        datetime created_at
    }

    saved_addresses {
        bigint address_id PK
        bigint customer_id FK
        bigint zone_id FK "nullable, SET_NULL"
        string label
        text street_address
        boolean is_default "max one true per customer"
    }

    delivery_zones {
        bigint zone_id PK
        string name UK
        decimal fee ">= 0"
        boolean is_active
    }

    couriers {
        bigint courier_id PK
        bigint user_id FK, UK
        string phone
        boolean is_available
    }

    restaurants {
        bigint restaurant_id PK
        bigint owner_id FK "PROTECT, role OWNER"
        string name
        string phone
        text address
        text description
        boolean is_approved "set by site admin"
        boolean is_active "set by owner"
        datetime created_at
    }

    opening_hours {
        bigint id PK
        bigint restaurant_id FK
        int day_of_week "0 Mon to 6 Sun, unique per restaurant"
        time open_time "null if closed"
        time close_time "null if closed"
        boolean is_closed
    }

    food_categories {
        bigint category_id PK
        bigint restaurant_id FK
        string name "unique per restaurant"
    }

    food_products {
        bigint product_id PK
        bigint restaurant_id FK "RESTRICT"
        bigint category_id FK "nullable, same restaurant"
        string name
        text description
        decimal price ">= 0"
        string image
        boolean is_vegetarian
        boolean is_available "out of stock today"
        boolean is_archived "removed from menu"
    }

    coupons {
        bigint coupon_id PK
        bigint restaurant_id FK "null means platform-wide"
        string code UK "stored uppercase"
        string discount_type "PERCENT or FIXED"
        decimal discount_value "> 0, <= 100 if PERCENT"
        decimal min_order_amount ">= 0"
        int max_uses "null means unlimited"
        int times_used "<= max_uses"
        datetime valid_until
        boolean is_active
    }

    orders {
        bigint order_id PK
        bigint customer_id FK "RESTRICT"
        bigint restaurant_id FK "RESTRICT"
        bigint courier_id FK "nullable"
        bigint coupon_id FK "nullable"
        string status "PENDING to DELIVERED or CANCELLED"
        text delivery_address "snapshot"
        text notes
        string payment_method "STRIPE or COD"
        string payment_status "UNPAID, PAID, FAILED, REFUNDED"
        string stripe_payment_intent_id UK "nullable"
        decimal subtotal ">= 0"
        decimal discount_amount "<= subtotal"
        decimal delivery_fee ">= 0"
        decimal total_amount "computed in save()"
        datetime created_at
        datetime updated_at
        datetime accepted_at
        datetime delivered_at
        datetime cancelled_at
    }

    order_items {
        bigint order_item_id PK
        bigint order_id FK
        bigint product_id FK "RESTRICT, same restaurant"
        int quantity ">= 1"
        decimal unit_price "price snapshot"
    }

    reviews {
        bigint review_id PK
        bigint order_id FK, UK "delivered orders only"
        smallint rating "1 to 5"
        text comment
        datetime created_at
    }

    complaints {
        bigint complaint_id PK
        bigint order_id FK
        text description
        string status "OPEN, IN_PROGRESS, RESOLVED"
        text admin_notes
        datetime created_at
        datetime resolved_at
    }
```

## Order status flow

```mermaid
stateDiagram-v2
    [*] --> PENDING
    PENDING --> ACCEPTED
    PENDING --> CANCELLED
    ACCEPTED --> PREPARING
    ACCEPTED --> CANCELLED
    PREPARING --> READY
    READY --> OUT_FOR_DELIVERY
    OUT_FOR_DELIVERY --> DELIVERED
    DELIVERED --> [*]
    CANCELLED --> [*]
```

## App ownership

| App | Owner | Models |
|---|---|---|
| accounts | shared | User |
| customer | Person 1 | Customer, SavedAddress |
| restaurants | Person 2 | Restaurant, OpeningHour, FoodCategory, FoodProduct |
| orders | shared (Person 1 & 2) | Coupon, Order, OrderItem, Review |
| delivery | Person 3 | DeliveryZone, Courier |
| dashboard | Person 3 | Complaint |
