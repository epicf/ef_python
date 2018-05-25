import io
import os
import shlex
import subprocess
import tempfile
from configparser import ConfigParser


class EfConf:

    def __init__(self):
        self.time_grid = TimeGrid()
        self.spatial_mesh = SpatialMesh()
        self.sources = []
        self.inner_regions = []
        self.output_file = OutputFile()
        self.boundary_conditions = BoundaryConditions()
        self.particle_interaction_model = ParticleInteractionModel()
        self.ex_fields = []

    def add_source(self, src):
        self.sources.append(src)

    def add_inner_region(self, ir):
        self.inner_regions.append(ir)

    def add_ex_field(self, ef):
        self.ex_fields.append(ef)

    def visualize_all(self, visualizer):
        visualizer.visualize([self.time_grid, self.spatial_mesh] + self.sources + self.inner_regions + self.ex_fields)

    def export_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.as_text())

    def as_text(self):
        as_dict = {}
        as_dict.update(self.time_grid.export())
        as_dict.update(self.spatial_mesh.export())
        for src in self.sources:
            as_dict.update(src.export())
        for ir in self.inner_regions:
            as_dict.update(ir.export())
        as_dict.update(self.output_file.export())
        as_dict.update(self.boundary_conditions.export())
        as_dict.update(self.particle_interaction_model.export())
        for ef in self.ex_fields:
            as_dict.update(ef.export())
        # can't construct config from dictionary; have to do it manually
        # config = ConfigParser( as_dict )
        config = ConfigParser()
        for sec_name, sec in as_dict.items():
            config[sec_name] = {}
            for k, v in sec.items():
                config[sec_name][k] = str(v)
        f = io.StringIO()
        config.write(f)
        return f.getvalue()

    def print_config(self):
        print(self.as_text())

    def run(self, ef_command="python3 ../../main.py", workdir="./",
            save_config_as=None):
        current_dir = os.getcwd()
        os.chdir(workdir)
        if save_config_as:
            self.export(save_config_as)
            command = ef_command + " " + save_config_as
        else:
            tmpfile, tmpfilename = tempfile.mkstemp(suffix=".ini", text=True)
            self.export(tmpfilename)
            command = ef_command + " " + tmpfilename
        print("command:", command)
        self.run_command(command)
        # stdout = subprocess.Popen( command, shell = True,
        #                           stdout = subprocess.PIPE ).stdout.read()
        # Jupyter magick
        # !{command}
        # print( stdout )
        if tmpfile:
            os.remove(tmpfilename)
        os.chdir(current_dir)

    @classmethod
    def run_from_file(cls, startfile, ef_command="python3 ../../main.py", workdir="./"):
        current_dir = os.getcwd()
        os.chdir(workdir)
        command = ef_command + " " + startfile
        print("command:", command)
        stdout = subprocess.Popen(command, shell=True,
                                  stdout=subprocess.PIPE).stdout.read()
        print(stdout)
        os.chdir(current_dir)

    def run_command(self, command):
        # https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc
    # try instead
    # https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running


def main():
    conf = EfConf()
    box = ParticleSource(Box.init_rlbtnf())
    tube = ParticleSource(Tube((5, 5, 5), (7, 5, 7), 1, 2))
    segment = InnerRegion(Cylinder((2, 2, 2), (1, 1, 1), 1))
    c1 = InnerRegion(Tube.init_aligned_z(8, 3, 2, 5, 2, 3))
    conf.add_source(box)
    conf.add_source(tube)
    conf.add_inner_region(segment)
    conf.add_inner_region(c1)
    vis = Visualizer3d()
    conf.visualize_all(vis)


if __name__ == "__main__":
    main()
