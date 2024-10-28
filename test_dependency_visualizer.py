import unittest
from dependency_visualizer import parse_config, get_dependencies, build_dependency_graph

class TestDependencyVisualizer(unittest.TestCase):

    def test_parse_config(self):
        config = parse_config('config.xml')
        self.assertEqual(config['package_name'], 'bash')

    def test_get_dependencies(self):
        dependencies = get_dependencies('bash')
        self.assertIn('libc6', dependencies)

    def test_build_dependency_graph(self):
        graph = build_dependency_graph('bash')
        self.assertIn('digraph', graph.source)

if __name__ == '__main__':
    unittest.main()
