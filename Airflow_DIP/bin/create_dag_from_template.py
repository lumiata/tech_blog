from jinja2 import Template
import argparse
import json
from airflow.settings import DAGS_FOLDER
from dags.lib import create_graph

def run(parsed_args):
    template_path = f'templates/{parsed_args.template}.py'
    with open(template_path) as f:
        template = Template(f.read())

    scripts_path = (
        f'scripts/{parsed_args.scripts_folder}/{parsed_args.scripts_list}'
    )
    dependency_graph = json.dumps(create_graph.main(
        ['--script-list', scripts_path,
         '--dependencies']
    ), indent=4)
    with open(scripts_path) as f:
        script_list = f.read()

    rendered_template = template.render(
        dag_name=parsed_args.dag_name,
        dependency_graph=dependency_graph,
        script_list=script_list
    )
    with open(f'{DAGS_FOLDER}/{parsed_args.dag_name}.py', 'w') as f:
        f.write(rendered_template)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', type=str)
    parser.add_argument('--dag-name', type=str)
    parser.add_argument('--scripts-folder', type=str)
    parser.add_argument('--scripts-list', type=str, default='run_config.json')
    run(parser.parse_args())

if __name__ == '__main__':
    main()
