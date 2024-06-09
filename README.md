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
```bash
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

```bash
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
   ```bash
   packages:
    - package: dbt-labs/dbt_utils
      version: 1.2.0
   ```
6. Update dependancy with ```dbt deps``` in terminal
![image](https://github.com/hyeen24/ELT-pipeline/assets/81229303/178dd3c3-99b6-404b-8b76-939558dac5e6)
7. 

xx
=======

