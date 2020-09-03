from bs4 import BeautifulSoup

def parseXml(f):
    with open(f) as fp:
        return BeautifulSoup(fp, 'lxml-xml')

def rackControl(filename, control = 0):
    soup = parseXml(filename)
    rack = {}
    for i, plugin in enumerate(soup.findAll('plugin')):
        pluginName = plugin['instance-name']
        params = {}
        for j, param in enumerate(plugin.preset.findAll('param')):
            params[param['name']] = {
                'value': param['value'],
                'control': control,
            }
            auto = soup.new_tag('automation')
            auto['key'] = f'automation_v1_{control}_to_{param["name"]}'
            auto['value'] = '0 1'
            plugin.append(auto)
            if control % 128 == 127:
                control += 129
            else:
                control += 1
        rack[pluginName] = params
    return soup, rack, control

if __name__ == '__main__':
    from os.path import join
    from json import dumps
    racks = ['calf_vocal', 'calf_submix', 'calf_synth', 'calf_postfx', 'calf_jacktrip']
    control = 0
    plugins = {}
    for rackName in racks:
        soup, rack, control = rackControl(join('../holophonor', rackName), control=control)
        with open(join('../holophonor', rackName + '_auto.xml'), 'w') as f:
            f.write(soup.prettify())
        plugins[rackName] = rack
    with open('racks.json', 'w') as f:
        f.write(dumps(plugins))
