import xml.etree.ElementTree as ET
import subprocess
from graphviz import Digraph
import argparse
import requests
import gzip
from io import BytesIO

def parse_config(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    config = {
        "graphviz_path": root.findtext('graphviz_path'),
        "package_name": root.findtext('package_name'),
        "output_file": root.findtext('output_file'),
        "repository_url": root.findtext('repository_url')
    }
    return config


cached_data = None

def fetch_package_data(url):
    global cached_data
    if cached_data is not None:
        return cached_data
    response = requests.get(url)
    print(url)
    if response.status_code == 200:
        with gzip.open(BytesIO(response.content), 'rt') as f:
            cached_data = f.read()
            return cached_data
    else:
        raise Exception(f"Can't fetch package data")

def parse_dependencies(package_data, package_name):
    dependencies = []
    in_package = False
    
    for line in package_data.splitlines():
        if line.startswith("Package:"):
            in_package = line.split(":")[1].strip() == package_name
        elif in_package and line.startswith("Depends:"):
            deps = line.split(":")[1].strip().split(", ")
            dependencies.extend(dep.split(" ")[0] for dep in deps)
            break
            
    return dependencies

def get_dependencies(repo_url, package_name, seen=None):
    if seen is None:
        seen = set()

    if package_name in seen:
        return []

    seen.add(package_name)
    package_data = fetch_package_data(repo_url)
    direct_dependencies = parse_dependencies(package_data, package_name)
    dependencies = list(direct_dependencies)

    for dep in direct_dependencies:
        dependencies.extend(get_dependencies(repo_url, dep, seen))

    return dependencies

def build_dependency_graph(repo_url, package_name):
    graph = Digraph(comment=f"Dependency graph for {package_name}")
    dependencies = get_dependencies(repo_url, package_name)
    seen = set()

    def add_edges(pkg):
        if pkg in seen:
            return
        seen.add(pkg)
        for dep in get_dependencies(repo_url, pkg):
            graph.edge(pkg, dep)
            add_edges(dep)

    add_edges(package_name)
    return graph

def save_graph(graph, output_path):
    with open(output_path, 'w') as f:
        f.write(graph.source)

def main(config_file):
    config = parse_config(config_file)
    
    graph = build_dependency_graph(config['repository_url'], config['package_name'])
    save_graph(graph, config['output_file'])

    print(f"Graphviz code for {config['package_name']}:\n")
    print(graph.source)

main('./config.xml')
