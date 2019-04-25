import argparse
import json
import copy
import sys
import importlib
from collections import namedtuple, defaultdict
from dags.lib import normalize_path

Edge = namedtuple('Edge', ['source', 'target', 'type'])
Node = namedtuple('Node', ['id', 'type'])

def execute_scripts(f):
    for k, script in json.load(f):
        sys.argv = script
        script_module = importlib.import_module(sys.argv[0])
        sys.argv.append('--dry-run')
        step_iodict = script_module.main()
        step_iodict['outputs'] = [
            normalize_path(output) for output in step_iodict['outputs']
        ]
        step_iodict['inputs'] = [
            normalize_path(input) for input in step_iodict['inputs']
        ]
        yield k, step_iodict


def create_graph(iodicts):
    graph = defaultdict(lambda: set())
    for step, iodict in iodicts:
        step_node = Node(step, 'script')
        for input in iodict.get('inputs', []):
            input_node = Node(input, 'file')
            graph[input_node].add(step_node)
        graph[step_node] = set([
            Node(output, 'file') for output in iodict.get('outputs', [])])
    return graph

def simplify_graph(graph, dependencies=False):
    simple = {}
    file_nodes = set([node for node in graph.keys() if node.type == 'file'])
    include_outputs = (lambda c: []) if dependencies else (lambda c: [c])
    for node, children in graph.items():
        if node.type == 'script':
            simple[node] = set([
                n for c in children
                for n in graph.get(c, include_outputs(c))
                # get all the children of the children
                # if a child node doesn't have any,
                # just add the child to the graph
                # if dependency is false
            ])
        file_nodes.difference_update(children)
    if not dependencies:
        for node in file_nodes:
            simple[node] = copy.deepcopy(graph[node])
    return simple

def to_edge_list(graph):
    for node, children in graph.items():
        for c in children:
            if node.type == 'file' and c.type == 'script':
                edge_type = 'input'
            elif node.type == 'script' and c.type == 'file':
                edge_type = 'output'
            else:
                edge_type = 'dependency'
            yield Edge(node, c, edge_type)

def to_d3(edge_list):
    return [
        {'source': edge.source.id, 'target': edge.dest.id, 'type': edge.type}
        for edge in edge_list
    ]

def to_json(graph):
    result = {}
    for n, children in graph.items():
        result[n.id] = [c.id for c in children]
    return result

def run(parsed_args):
    with open(parsed_args.script_list) as f:
        iodicts = list(execute_scripts(f))
    graph = create_graph(iodicts)
    if parsed_args.simple or parsed_args.dependencies:
        graph = simplify_graph(
            graph, dependencies=parsed_args.dependencies)
    graph = {k: v for k, v in graph.items() if v}
    if parsed_args.d3:
        graph = to_d3(to_edge_list(graph))
    else:
        graph = to_json(graph)
    output = json.dumps(graph)
    return output

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--script-list', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--simple', action='store_true')
    group.add_argument('--dependencies', action='store_true')
    group.add_argument('--full', action='store_true')
    parser.add_argument('--d3', action='store_true')
    return run(parser.parse_args(args))

if __name__ == '__main__':
    print(main())
