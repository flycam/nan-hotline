import re


class CommunicationGraph(object):
    def __init__(self, filename):
        self.nodes = {}
        self.firstNode = None
        rex = re.compile(r'^(-?[0-9]*) ?- ?([^-]*) ?- ?\[(.*)\]$')
        folRex = re.compile(r'^ *([0-9\*#]*):(-?[0-9]*) *$')
        with open(filename, 'r') as f:
            for line in f.readlines():
                groups = rex.match(line).groups()
                node = CommunicationNode()
                node.description = groups[1]
                for followNodeStr in groups[2].split(','):
                    folMatch = folRex.match(followNodeStr)
                    if folMatch is not None:
                        folGroups = folMatch.groups()
                        node.followingNodes[folGroups[0]] = int(folGroups[1])
                node.id = int(groups[0])
                node.graph = self

                self.nodes[node.id] = node

                if self.firstNode is None:
                    self.firstNode = node

    def getNodeById(self, id):
        return self.nodes[id]

    def __str__(self):
        string = 'Graph'
        for n in self.nodes.values():
            string += '\n' + str(n)
        return string


class CommunicationNode(object):
    def __init__(self):
        self.description = None
        self.followingNodes = {}
        self.graph = None
        self.id = None

    def get_following_node(self, number):
        return self.graph.getNodeById(self.followingNodes[number])

    def get_filename(self, language):
        return 'sounds/' + str(self.id) + '_' + language + '.wav'

    def __str__(self):
        return 'Node {} - {} - {}'.format(self.id, self.description, self.followingNodes)

if __name__ == '__main__':
    print CommunicationGraph('config')