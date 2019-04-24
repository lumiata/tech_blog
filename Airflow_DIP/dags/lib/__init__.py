from airflow.operators.python_operator import PythonOperator
import importlib
import pathlib

def create_python_task(task_id, dag, argv):
    script_module = importlib.import_module(argv[0])
    def task_method(*argv):
        print(argv)
        return script_module.main(argv)
    task = PythonOperator(
        task_id=task_id,
        python_callable=task_method,
        op_args=argv[1:],
        dag=dag)
    return task

def configure_dependencies(tasks, dependency_graph):
    for upstream, downstreams in dependency_graph.items():
        for d in downstreams:
            tasks[upstream].set_downstream(tasks[d])

def normalize_path(path):
    return str(pathlib.Path(path).expanduser())
