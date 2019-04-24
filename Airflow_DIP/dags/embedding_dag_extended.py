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

DAG_NAME = 'embedding_dag_extended'
dependency_graph = json.loads("{\"load_data\": [\"eval_default_terms_1\", \"train_default_terms_1\", \"train_default_terms_0\", \"eval_all_terms_1\", \"train_all_terms_0\", \"eval_all_terms_0\", \"train_all_terms_1\", \"eval_default_terms_0\"], \"get_default_informative_terms\": [\"eval_default_terms_0\", \"train_default_terms_0\", \"eval_default_terms_1\", \"train_default_terms_1\"], \"get_all_informative_terms\": [\"train_all_terms_1\", \"eval_all_terms_1\", \"train_all_terms_0\", \"eval_all_terms_0\"], \"train_default_terms_0\": [\"eval_default_terms_0\"], \"eval_default_terms_0\": [\"compare\"], \"train_default_terms_1\": [\"eval_default_terms_1\"], \"eval_default_terms_1\": [\"compare\"], \"train_all_terms_0\": [\"eval_all_terms_0\"], \"eval_all_terms_0\": [\"compare\"], \"train_all_terms_1\": [\"eval_all_terms_1\"], \"eval_all_terms_1\": [\"compare\"]}")
script_list = json.loads("""[
  ["load_data", [
    "scripts.embedding_example.load_data", "--train-url", "https://download.mlcc.google.com/mledu-datasets/sparse-data-embedding/train.tfrecord",
    "--test-url",  "https://download.mlcc.google.com/mledu-datasets/sparse-data-embedding/test.tfrecord"
  ]],
  ["get_default_informative_terms", [
    "scripts.embedding_example.get_informative_terms",
    "--terms-filename", "default_terms.txt"
  ]],
  ["get_all_informative_terms", [
    "scripts.embedding_example.get_informative_terms",
    "--url", "https://download.mlcc.google.com/mledu-datasets/sparse-data-embedding/terms.txt",
    "--terms-filename", "all_terms.txt"
  ]],
  ["train_default_terms_0", [
    "scripts.embedding_example.train_embedding",
    "--input", "~/.keras/datasets/train.tfrecord",
    "--informative-terms", "~/.keras/datasets/default_terms.txt",
    "--output", "/tmp/embedding_model_default_terms_0"]],
  ["eval_default_terms_0",["scripts.embedding_example.evaluate_embedding",
    "--train-input", "~/.keras/datasets/train.tfrecord",
    "--test-input", "~/.keras/datasets/test.tfrecord",
    "--model-folder", "/tmp/embedding_model_default_terms_0",
    "--informative-terms", "~/.keras/datasets/default_terms.txt",
    "--output", "/tmp/embedding_report_default_terms_0"]],
  ["train_default_terms_1", [
    "scripts.embedding_example.train_embedding",
    "--input", "~/.keras/datasets/train.tfrecord",
    "--informative-terms", "~/.keras/datasets/default_terms.txt",
    "--dimension", "8",
    "--learning-rate", "0.05",
    "--hidden-units",  "20", "20",
    "--output", "/tmp/embedding_model_default_terms_1"]],
  ["eval_default_terms_1",["scripts.embedding_example.evaluate_embedding",
    "--train-input", "~/.keras/datasets/train.tfrecord",
    "--test-input", "~/.keras/datasets/test.tfrecord",
    "--dimension", "8",
    "--hidden-units",  "20", "20",
    "--model-folder", "/tmp/embedding_model_default_terms_1",
    "--informative-terms", "~/.keras/datasets/default_terms.txt",
    "--output", "/tmp/embedding_report_default_terms_1"]],
  ["train_all_terms_0", [
    "scripts.embedding_example.train_embedding",
    "--input", "~/.keras/datasets/train.tfrecord",
    "--informative-terms", "~/.keras/datasets/all_terms.txt",
    "--output", "/tmp/embedding_model_all_terms_0"]],
  ["eval_all_terms_0",["scripts.embedding_example.evaluate_embedding",
    "--train-input", "~/.keras/datasets/train.tfrecord",
    "--test-input", "~/.keras/datasets/test.tfrecord",
    "--model-folder", "/tmp/embedding_model_all_terms_0",
    "--informative-terms", "~/.keras/datasets/all_terms.txt",
    "--output", "/tmp/embedding_report_all_terms_0"]],
  ["train_all_terms_1", [
    "scripts.embedding_example.train_embedding",
    "--input", "~/.keras/datasets/train.tfrecord",
    "--informative-terms", "~/.keras/datasets/all_terms.txt",
    "--dimension", "8",
    "--learning-rate", "0.05",
    "--hidden-units",  "20", "20",
    "--output", "/tmp/embedding_model_all_terms_1"]],
  ["eval_all_terms_1",["scripts.embedding_example.evaluate_embedding",
    "--train-input", "~/.keras/datasets/train.tfrecord",
    "--test-input", "~/.keras/datasets/test.tfrecord",
    "--model-folder", "/tmp/embedding_model_all_terms_1",
    "--dimension", "8",
    "--hidden-units",  "20", "20",
    "--informative-terms", "~/.keras/datasets/all_terms.txt",
    "--output", "/tmp/embedding_report_all_terms_1"]],
  ["compare", ["scripts.embedding_example.compare_models",
    "--model-reports", "/tmp/embedding_report_default_terms_0",
    "/tmp/embedding_report_default_terms_1",
    "/tmp/embedding_report_all_terms_0", "/tmp/embedding_report_all_terms_1",
    "--output", "/tmp/golden_model"
  ]]
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