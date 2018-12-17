import h5py

from TimeGrid import TimeGrid
from ef.config.components import time_grid


class TestTimeGrid:
    def test_print(self):
        grid = TimeGrid(100, 1, 10)
        assert str(grid) == ("### TimeGrid:\n"
                             "total_time = 100.0\n"
                             "total_nodes = 101\n"
                             "time_step_size = 1.0\n"
                             "time_save_step = 10.0\n"
                             "node_to_save = 10\n"
                             "current_time = 0.0\n"
                             "current_node = 0")

    def test_component_link(self):
        assert time_grid.TimeGridConf().make() == TimeGrid(100.0, 1.0, 10.0)
        assert time_grid.TimeGridConf() == TimeGrid(100.0, 1.0, 10.0).to_component()
        assert time_grid.TimeGridConf() == TimeGrid(100, 1, 10).to_component()
        # should config component also store parameters as float?
        assert time_grid.TimeGridConf(123.0, 13.0, 3.0) != TimeGrid(123, 3, 13).to_component()
        assert time_grid.TimeGridConf(123, 13, 3) != TimeGrid(123, 3, 13).to_component()
        assert time_grid.TimeGridConf(123, 13, 3).make() == TimeGrid(123, 3, 13)

    def test_init_h5(self, tmpdir):
        fname = tmpdir.join('test_timegrid_init.h5')
        grid1 = TimeGrid(100, 1, 10)
        with h5py.File(fname, mode="w") as h5file:
            grid1.write_to_file(h5file)
        with h5py.File(fname, mode="r") as h5file:
            grid2 = TimeGrid.load_h5(h5file["/TimeGrid"])
        assert grid1 == grid2
