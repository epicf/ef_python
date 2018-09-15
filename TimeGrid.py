from math import ceil


class TimeGrid():

    def __init__(self):
        self.total_time = None
        self.current_time = None
        self.time_step_size = None
        self.time_save_step = None
        self.total_nodes = None
        self.current_node = None
        self.node_to_save = None


    @classmethod
    def init_from_config(cls, conf):
        new_obj = cls()
        new_obj.check_correctness_of_related_config_fields(conf)
        new_obj.get_values_from_config(conf)
        new_obj.init_total_nodes()
        new_obj.shrink_time_step_size_if_necessary(conf)
        new_obj.shrink_time_save_step_if_necessary(conf)
        new_obj.set_current_time_and_node()
        TimeGrid.mark_timegrid_sec_as_used(conf)
        return new_obj


    @staticmethod
    def mark_timegrid_sec_as_used(conf):
        # For now simply mark sections as 'used' instead of removing them.
        conf["TimeGrid"]["used"] = "True"


    @classmethod
    def init_from_h5(cls, h5group):
        new_obj = cls()
        new_obj.total_time = h5group.attrs["total_time"]
        new_obj.current_time = h5group.attrs["current_time"]
        new_obj.time_step_size = h5group.attrs["time_step_size"]
        new_obj.time_save_step = h5group.attrs["time_save_step"]
        new_obj.total_nodes = h5group.attrs["total_nodes"]
        new_obj.current_node = h5group.attrs["current_node"]
        new_obj.node_to_save = h5group.attrs["node_to_save"]
        return new_obj


    def check_correctness_of_related_config_fields(self, conf):
        self.total_time_gt_zero(conf)
        self.time_step_size_gt_zero_le_total_time(conf)
        self.time_save_step_ge_time_step_size(conf)


    def get_values_from_config(self, conf):
        self.total_time = conf["TimeGrid"].getfloat("total_time")
        self.time_step_size = conf["TimeGrid"].getfloat("time_step_size")
        self.time_save_step = conf["TimeGrid"].getfloat("time_save_step")


    def init_total_nodes(self):
        self.total_nodes = ceil(self.total_time / self.time_step_size) + 1


    def shrink_time_step_size_if_necessary(self, conf):
        self.time_step_size = self.total_time / (self.total_nodes - 1)
        if self.time_step_size != conf["TimeGrid"].getfloat("time_step_size"):
            print("Time step was shrinked to {:.3E} "
                  "from {:.3E} "
                  " to fit round number of cells.".format(
                      self.time_step_size,
                      conf["TimeGrid"].getfloat("time_step_size")))


    def shrink_time_save_step_if_necessary(self, conf):
        self.time_save_step = \
            int(self.time_save_step / self.time_step_size) * self.time_step_size
        if self.time_save_step != conf["TimeGrid"].getfloat("time_save_step"):
            print("Time save step was shrinked to {:.3E} "
                  "from {:.3E} "
                  "to be a multiple of time step.".format(
                      self.time_save_step,
                      conf["TimeGrid"].getfloat("time_save_step")))
        self.node_to_save = int(self.time_save_step / self.time_step_size)


    def set_current_time_and_node(self):
        self.current_time = 0.0
        self.current_node = 0


    def update_to_next_step(self):
        self.current_node += 1
        self.current_time += self.time_step_size


    def print(self):
        print("### TimeGrid:")
        print("Total time = {:.3E}".format(self.total_time))
        print("Current time = {:.3E}".format(self.current_time))
        print("Time step size = {:.3E}".format(self.time_step_size))
        print("Time save step = {:.3E}".format(self.time_save_step))
        print("Total nodes = {:d}".format(self.total_nodes))
        print("Current node = {:d}".format(self.current_node))
        print("Node to save = {:d}".format(self.node_to_save))


    def write_to_file(self, h5file):
        groupname = "/TimeGrid"
        h5group = h5file.create_group(groupname)
        h5group.attrs.create("total_time", self.total_time)
        h5group.attrs.create("current_time", self.current_time)
        h5group.attrs.create("time_step_size", self.time_step_size)
        h5group.attrs.create("time_save_step", self.time_save_step)
        h5group.attrs.create("total_nodes", self.total_nodes)
        h5group.attrs.create("current_node", self.current_node)
        h5group.attrs.create("node_to_save", self.node_to_save)


    def total_time_gt_zero(self, conf):
        if conf["TimeGrid"].getfloat("total_time") <= 0:
            raise ValueError("Expect total_time > 0")


    def time_step_size_gt_zero_le_total_time(self, conf):
        if (conf["TimeGrid"].getfloat("time_step_size") <= 0) or \
           (conf["TimeGrid"].getfloat("time_step_size") > \
            conf["TimeGrid"].getfloat("total_time")):
            raise ValueError("Expect time_step_size > 0 and time_step_size <= total_time")


    def time_save_step_ge_time_step_size(self, conf):
        if conf["TimeGrid"].getfloat("time_save_step") < \
           conf["TimeGrid"].getfloat("time_step_size"):
            raise ValueError("Expect time_save_step >= time_step_size")
