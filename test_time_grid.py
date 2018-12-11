from TimeGrid import TimeGrid
from ef.config.components import time_grid


class TestTimeGrid:
    def test_print(self):
        grid = TimeGrid(100, 1, 10)
        assert str(grid) == ("### TimeGrid:\n"
                             "total_time = 100\n"
                             "total_nodes = 101\n"
                             "time_step_size = 1.0\n"
                             "time_save_step = 10.0\n"
                             "node_to_save = 10\n"
                             "current_time = 0.0\n"
                             "current_node = 0")

    def test_component_link(self):
        assert time_grid.TimeGrid().make() == TimeGrid(100.0, 1.0, 10.0)
        assert time_grid.TimeGrid() == TimeGrid(100.0, 1.0, 10.0).to_component()
