from bs4 import BeautifulSoup

def parseXml(f):
    with open(f) as fp:
        return BeautifulSoup(fp, 'lxml-xml')

def rackControl(filename):
    soup = parseXml(filename)
    cc = []
    control = 0
    for i, plugin in enumerate(soup.findAll('plugin')):
        pluginName = plugin['instance-name']
        params = []
        for j, param in enumerate(plugin.preset.findAll('param')):
            params.append({
                'name': param['name'],
                'value': param['value'],
                'control': control,
            })
            auto = soup.new_tag('automation')
            auto['key'] = f'automation_v1_{control}_to_{param["name"]}'
            auto['value'] = '0 1'
            plugin.append(auto)
            control += 1
        cc.append({ pluginName: params })
    return soup, cc

if __name__ == '__main__':
    from pprint import pprint
    soup, cc = rackControl('../holophonor/calf-holo.xml')
    with open('test.xml', 'w') as f:
        f.write(soup.prettify())
