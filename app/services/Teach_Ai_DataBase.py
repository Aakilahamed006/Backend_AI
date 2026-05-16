# ----------------------------
# 1. DATABASE SCHEMA FUNCTION
# ----------------------------

## You can paste your Database Schema Query Here
def get_database_schema():

    schema = """
DATABASE STRUCTURE:

Table: users
- id (int, primary key)
- name (text)
- age (int)

Table: orders
- id (int, primary key)
- user_id (int, foreign key -> users.id)
- total (float)

Table: order_items
- id (int, primary key)
- order_id (int, foreign key -> orders.id)
- product_name (text)
- price (float)
"""

    return schema