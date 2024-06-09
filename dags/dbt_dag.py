
import os 
from datetime import datetime 
from pathlib import Path 

from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping 


profile_config = ProfileConfig( 
    profile_name="default", 
    target_name="dev", 
    profile_mapping=SnowflakeUserPasswordProfileMapping( 
        conn_id="snowflake_conn", 
        profile_args={"database":"dbt_db","schema":"dbt_schema"}, 
    ), 
) 

# [START local_example] 
basic_cosmos_dag = DbtDag( 
    # dbt/cosmos-specific parameters 
    project_config=ProjectConfig("/usr/local/airflow/dags/dbt/data_pipeline",), 
    operator_args={ 
        "install_deps": True  # install any necessary dependencies before running any dbt command 
    }, 
    profile_config=profile_config,
    
    execution_config=ExecutionConfig(
        dbt_executable_path=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt",
    ), 
    
    # normal dag parameters 
    schedule_interval="@daily", 
    start_date=datetime(2023, 1, 1), 
    catchup=False, 
    dag_id="dbt_dag", 
) 
# [END local_example] 