select
    customer_id,
    customer_name,
    email,
    city,
    country,
    signup_date
from {{ ref('stg_customers') }}
