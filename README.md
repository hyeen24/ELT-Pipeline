Overview
========

This project stimulate a creation of an ELT pipeline.

Technologies
================
- Airflow  --> orchestration
- Snowflake --> warehousing
- dbt --> tranformation

Setting Environment
===========================
<h2> dbt core </h2>
1. create new environment in directory

```bash
python -m venv debt-env
```

2. Activate virtual environment (Windows)

```bash
dbt-env\Scripts\activate
```

3. install dbt core and dbt snowflake

```bash
python -m pip install dbt-core dbt-snowflake
```

[Official dbt Documentation](https://docs.getdbt.com/docs/core/pip-install)

<h2> Snowflake </h2>

1. [Register an account](https://signup.snowflake.com/?utm_source=google&utm_medium=paidsearch&utm_campaign=ap-sg-en-brand-core-exact&utm_content=go-eta-evg-ss-free-trial&utm_term=c-g-snowflake-e&_bt=562156041580&_bk=snowflake&_bm=e&_bn=g&_bg=125204683182&gclsrc=aw.ds&gad_source=1&gclid=CjwKCAjwgpCzBhBhEiwAOSQWQeBkaIHICqxGi-DEvMo-5aO8airs4iymD1IhQfcFyfIcZgvLMGcuexoCfeAQAvD_BwE)

2. Setting up warehouse
```sql
# Creating admin role (superuser)
use role accountadmin;

#Create warehouse
create warehouse dbt_wh;

#Create database
create database dbt_db;

#Create role
create role dbt_role;

#checking grants
show grants on warehouse dbt_wh;

#Grant usage for warehouse and database to role and role to user
grant usage on warehouse dbt_wh to role dbt_role;
grant role dbt_role to user <your user>;
grant all on database dbt_db to role dbt_role;

#using the role
use role dbt_role;

#creating empty schema
create schema dbt_db.dbt_schema;
```

Project - Step by Step
=================================
1. Initialize dbt

```bash
dbt init
```

- name your project
- Select your database profile -- > enter number
- Enter your account --> Go to snowflake > account > locator
   Copy the locator address and remove the .snowflakecomputing.com
   eg.
   https://abcde.southeast-asia.azure.snowflakecomputing.com
   account = abcde.southeast-asia.azure
- Enter your password
   # Below 6-9 must be same as what is created in snowflake
- Enter role : dbt_role 
- Enter warehouse : dbt_wh 
- Enter database : dbt_db 
- Enter Schema : dbt_schema
- Enter thread : 10
- cd <project name> #try using wsl mode
- code . to enter VS code

2. Configure project and packages
- update dbt_project.yml (Main reference file)

```yml
  #raw data from source file
  stagging: 
      +materialized: view
      snowflake_warehouse: dbt_wh

  #transform data from source file
    marts:
      +materialized: table
      snowflake_warehouse: dbt_wh
```

3. delete the example folder in models
4. Add 2 new folder: ```stagging``` and ```mart```
5. Add new packages.yml [Latest version](https://github.com/dbt-labs/dbt-utils/releases)
   ```yml
   packages:
    - package: dbt-labs/dbt_utils
      version: 1.2.0
   ```
6. Update dependancy with ```dbt deps``` in terminal
   
   <img src="https://github.com/hyeen24/ELT-pipeline/assets/81229303/178dd3c3-99b6-404b-8b76-939558dac5e6)" width="500" height="100">

7. create a new file "tpch_sources.yml under staging folder
```yml
   version: 2

   sources:
     - name: tpch
       database: snowflake_sample_data
          schema: tpch_sf1
          tables:
            - name: orders
              columns:
                - name: o_orderkey
                  tests: 
                    - unique
                    - not_null
            - name: lineitem
              columns:
                - name: l_orderkey
                  tests:
                    - relationships:
                        to: source('tpch','orders')
                        field: o_orderkey
         
```

9.  create a ```stg_orders.sql``` file in staging :

```sql
select
    o_orderkey as order_key,
    o_custkey as customer_key,
    o_orderstatus as order_status,
    o_totalprice as total_price,
    o_orderdate as order_date
from
    {{ source('tpch','orders') }}     
```

11. test run the model with ```dbt run```

10. create a ```stg_line_items.sql``` file in staging:

```sql
select
    {{
        dbt_utils.generate_surrogate_key([
            'l_orderkey',
            'l_linenumber'
        ])
    }} as order_item_key,
    l_orderkey as order_key,
    l_partkey as part_key,
    l_linenumber as line_number,
    l_quantity as quantity,
    l_extendedprice as extended_price,
    l_discount as discount_percentage,
    l_tax as tax_rate
from
   {{ source('tpch','lineitem') }}
```
12. run the model with ```dbt run -s stg_line_items.sql``` to single model only 
13. create a ```int_order_items.sql``` in marts:

```sql
select  
    line_item.order_item_key,
    line_item.part_key,
    line_item.extended_price,
    line_item.line_number,
    orders.order_key,
    orders.customer_key,
    orders.order_date,
      {{ discounted_amount('line_item.extended_price', 'line_item.discount_percentage') }} as item_discount_amount
from 
    {{ ref('stg_tpch_orders') }} as orders
join
    {{ reg('stg_tpch_line_items')} } as stg_tpch_line_items 
        on orders.order_key = line_item.order_key
order by 
    orders.order_date
```

14. Testing with macros
    create a file ```pricing.sql``` under macros
 ```sql
       {% macro discount_amount(extended_pice, dicount_percentage, scale=2) %}
       (-1 * {{ extended_price }} * {{discount_percentage}})::numeric(16, {{ scale }})
       {% endmacro %}
 ```
15. Create another file ```int_order_items_summary.sql```
```sql
select
   order_key,
   sum(extended_price) as gross_item_sales_amount,
   sum(item_discount_amount) as item_discount_amount
from
   {{ ref('int_order_items') }}
group by
   order_key
```

16. Create a fact model ```fct_order.sql```
```sql
select
   orders.*,
   order_item_summary.gross_item_sales_amount,
   order_item_summary.item_discount_amount
from
   {{ ref('stg_orders') }} as orders
join
   {{ ref('int_order_items_summary') }} as order_item_summary
      on orders.order_key = order_item_summary.order_key
order by
   order_date
```

17. run each model and troubleshoot for any error (It should reflect in snowflake)

<h3> Writing test </h3>

1. create  ```tests.yml``` file in marts (Generic test)

```yml
models:
   - name: fct_orders
     columns:
         - name: order_key
           test:
             - unique
             - not_null
             - relationship:
                to: ref('stg_orders')
                field: order_key
                severity: warn
         - name: status_code
           tests:
             - accepted_values:
                 values: ['P', 'O', 'F']
```

2. Create ```fct_orders_discount.sql``` file in tests (singular test)

```sql
select
   *
from
   {{ ref('fct_orders') }}
where
   item_discount_amount > 0
```
3. Create a date test ```fct_orders_date_valid.sql```

```sql
select
   *
from
   {{ ref('fct_orders') }}
where
   date(order_date) > cURRENT_DATE()
      or date(order_date) < date('2000-01-01')
```

<h3> Setting up airflow with cosmos </h3>  

[Guide](https://github.com/hyeen24/ELT-pipeline/tree/main/.astro)

1. After setting up, update docker file:
```
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-snowflake && deactivate
```
make sure the directry of active is correct







