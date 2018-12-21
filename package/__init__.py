class dictionary(dict):
    """
    data = ((channel_num, channel_name, upper_channel, group_num), ...)
    """
    def search(self, data, node=None):
        if node is None:
            node = self

        if node['channel_num'] == data:
            return node

        for x in node['child']:
            result = self.search(data, x)
            if result:
                return result

    def insert_node(self, data):
        index = 0
        while data:
            if data[index][2] == None:
                self['channel_num'] = data[index][0]
                self['name'] = data[index][1]
                self['group_num'] = data[index][3]
                self['child'] = []
                del data[index]
                index = 0
            else:
                target = self.search(data[index][2])
                if target:
                    target['child'].append(dictionary(channel_num = data[index][0], name = data[index][1], group_num = data[index][3], child=[]))
                    del data[index]
                    index = 0
                else:
                    index += 1
                    if index >= len(data):
                        index = 0

    def print_under_target(self, data=None, result=[]):
        if not result:
            result.append(data['channel_num'])
        if data['child']:
            for x in data['child']:
                result.append(x['channel_num'])
                self.print_under_target(x, result)

        return result

