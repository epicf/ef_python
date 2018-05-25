from configparser import ConfigParser
import io

from jupyter.ef_jupyter_visualize import ConfigComponent
from glob import glob

for f in glob('../examples/minimal_working_example/*.conf'):
    conf = ConfigParser()
    conf.read(f)
    [print(conf.items(section)) for section in conf if section != 'DEFAULT']
    c = ConfigComponent.config_to_components(conf)
    for x in c:
        print(x)
    for x in c:
        print(x.make())

    conf = ConfigParser()
    for x in c:
        x.to_section(conf)
    str_out = io.StringIO()
    conf.write(str_out)
    print(str_out.getvalue())
