from airflow import DAG
from datetime import timedelta
from datetime import datetime
import json

from lib import create_python_task, configure_dependencies, create_graph


DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.utcnow(),
    'retries': 0
}

DAG_NAME = 'test_pipeline'
dependency_graph = json.loads("{\"create\": [\"copy\"]}")
script_list = json.loads("""[
  ["create", ["scripts.basic_example.create_file", "--output", "/tmp/test"]],
  ["copy",   ["scripts.basic_example.copy_file", "--input", "/tmp/test",
              "--output", "/tmp/test_out"]]
]
""")

dag = DAG(
    DAG_NAME,
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=4),
    schedule_interval=None
)

tasks = {
    k: create_python_task(k, dag, argv) for k, argv in script_list
}

configure_dependencies(tasks, dependency_graph)