from collections import namedtuple

from ef.config.parser import ConfigComponent, register, DataClass


class TimeGrid(DataClass):
    def __init__(self, total=100.0, save_step=10.0, step=1.0):
        self.total = total
        self.save_step = save_step
        self.step = step

    def to_conf(self):
        return TimeGridConf(self.total, self.save_step, self.step)


@register
class TimeGridConf(ConfigComponent):
    section = "Time grid"
    ContentTuple = namedtuple("TimeGridTuple", ('total_time', 'time_save_step', 'time_step_size'))
    convert = ContentTuple(float, float, float)

    def make(self):
        return TimeGrid(*self.content)
