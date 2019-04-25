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

DAG_NAME = 'embedding_dag'
dependency_graph = json.loads("{\"load_data\": [\"eval\", \"train\"], \"get_informative_terms\": [\"eval\", \"train\"], \"train\": [\"eval\"]}")
script_list = json.loads("""[
  ["load_data", [
    "scripts.embedding_example.load_data", "--train-url", "https://download.mlcc.google.com/mledu-datasets/sparse-data-embedding/train.tfrecord",
    "--test-url",  "https://download.mlcc.google.com/mledu-datasets/sparse-data-embedding/test.tfrecord"
  ]],
  ["get_informative_terms", ["scripts.embedding_example.get_informative_terms"]],
  ["train", [
    "scripts.embedding_example.train_embedding",
    "--input", "~/.keras/datasets/train.tfrecord",
    "--informative-terms", "~/.keras/datasets/terms.txt",
    "--output", "/tmp/embedding_model"]],
  ["eval",["scripts.embedding_example.evaluate_embedding",
    "--train-input", "~/.keras/datasets/train.tfrecord",
    "--test-input", "~/.keras/datasets/test.tfrecord",
    "--model-folder", "/tmp/embedding_model",
    "--informative-terms", "~/.keras/datasets/terms.txt",
    "--output", "/tmp/embedding_report"]]

]""")

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