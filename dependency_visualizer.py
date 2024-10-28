import xml.etree.ElementTree as ET
import subprocess
from graphviz import Digraph
import argparse

def parse_config(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    config = {
        "package_name": root.findtext('package_name'),
        "output_file": root.findtext('output_file'),
    }
    return config

def get_dependencies(package_name, seen=None):
    if seen is None:
        seen = set()
    dependencies = []

    result = subprocess.run(['apt-cache', 'depends', package_name], capture_output=True, text=True)
    
    for line in result.stdout.splitlines():
        if 'Depends:' in line:
            dep = line.split(':')[1].strip()
            if dep not in seen:
                seen.add(dep)
                dependencies.append(dep)
                dependencies.extend(get_dependencies(dep, seen))
    return dependencies

def build_dependency_graph(package_name):
    graph = Digraph(comment=f"Dependency graph for {package_name}")
    dependencies = get_dependencies(package_name)
    seen = set()

    def add_edges(pkg):
        if pkg in seen:
            return
        seen.add(pkg)
        for dep in get_dependencies(pkg):
            graph.edge(pkg, dep)
            add_edges(dep)

    add_edges(package_name)
    return graph

def save_graph(graph, output_path):
    with open(output_path, 'w') as f:
        f.write(graph.source)

def main(config_file):
    config = parse_config(config_file)
    
    graph = build_dependency_graph(config['package_name'])
    save_graph(graph, config['output_file'])

    print(f"Graphviz code for {config['package_name']}:\n")
    print(graph.source)

main('./config.xml')
