from bs4 import BeautifulSoup

def parseXml(f):
    with open(f) as fp:
        return BeautifulSoup(fp, 'lxml-xml')

def rackControl(filename, control = 0):
    soup = parseXml(filename)
    cc = []
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
    return soup, cc, control

if __name__ == '__main__':
    from os.path import join
    from json import dumps
    racks = ['calf_vocal', 'calf_submix', 'calf_synth', 'calf_postfx', 'calf_jacktrip']
    control = 0
    plugins = []
    for rack in racks:
        soup, cc, control = rackControl(join('../holophonor', rack), control=control)
        with open(join('../holophonor', rack + '_auto.xml'), 'w') as f:
            f.write(soup.prettify())
        plugins.append({rack: cc})
    with open('racks.json', 'w') as f:
        f.write(dumps({'racks': plugins}))
