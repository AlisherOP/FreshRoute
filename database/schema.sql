CREATE TABLE restaurants (
    restaurant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(25) NOT NULL,
    address TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);



CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(25) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE food_categories (
    category_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    restaurant_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,

    FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id)
        ON DELETE CASCADE,

    UNIQUE (restaurant_id, name),
    UNIQUE (category_id, restaurant_id)

);



CREATE TABLE food_products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    restaurant_id BIGINT NOT NULL,
    category_id BIGINT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (category_id)
        REFERENCES food_categories(category_id)
        ON DELETE SET NULL,
       
    UNIQUE (product_id, restaurant_id)

);


CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    restaurant_id BIGINT NOT NULL,

    order_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN (
            'PENDING',
            'CONFIRMED',
            'PREPARING',
            'READY',
            'OUT_FOR_DELIVERY',
            'COMPLETED',
            'CANCELLED'
        )),

    delivery_address TEXT NOT NULL,

    delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 0
        CHECK (delivery_fee >= 0),

    payment_method VARCHAR(30) NOT NULL
        CHECK (payment_method IN (
            'CASH',
            'CARD',
            'ONLINE'
        )),

    payment_status VARCHAR(30) NOT NULL DEFAULT 'PENDING'
        CHECK (payment_status IN (
            'PENDING',
            'PAID',
            'FAILED'
        )),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id)
        ON DELETE RESTRICT
);


CREATE TABLE order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,

    quantity INT NOT NULL CHECK (quantity > 0),

    unit_price DECIMAL(10, 2) NOT NULL
        CHECK (unit_price >= 0),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES food_products(product_id)
        ON DELETE RESTRICT,

    UNIQUE (order_id, product_id)
);