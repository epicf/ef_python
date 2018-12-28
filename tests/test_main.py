import os
import subprocess
from os.path import basename
from shutil import copyfile

import pytest

from ef.config.components import TimeGridConf
from ef.config.efconf import EfConf
from ef.main import main


def test_main(mocker, capsys, tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    config = tmpdir.join("test_main.conf")
    EfConf(time_grid=TimeGridConf(10, 5, 1)).export_to_fname("test_main.conf")
    mocker.patch("sys.argv", ["main.py", str(config)])
    main()
    out, err = capsys.readouterr()
    assert err == ""
    assert out == f"""Config file is:  {config}
[ TimeGrid ]
total_time = 10
time_save_step = 5
time_step_size = 1
[ SpatialMesh ]
grid_x_size = 10.0
grid_x_step = 1.0
grid_y_size = 10.0
grid_y_step = 1.0
grid_z_size = 10.0
grid_z_step = 1.0
[ OutputFilename ]
output_filename_prefix = out_
output_filename_suffix = .h5
[ BoundaryConditions ]
boundary_phi_right = 0.0
boundary_phi_left = 0.0
boundary_phi_bottom = 0.0
boundary_phi_top = 0.0
boundary_phi_near = 0.0
boundary_phi_far = 0.0
[ ParticleInteractionModel ]
particle_interaction_model = PIC
Writing step 0 to file out_0000000.h5
Time step from 0 to 1 of 10
Time step from 1 to 2 of 10
Time step from 2 to 3 of 10
Time step from 3 to 4 of 10
Time step from 4 to 5 of 10
Writing step 5 to file out_0000005.h5
Time step from 5 to 6 of 10
Time step from 6 to 7 of 10
Time step from 7 to 8 of 10
Time step from 8 to 9 of 10
Time step from 9 to 10 of 10
Writing step 10 to file out_0000010.h5
"""


_examples = [("examples/minimal_working_example/minimal_conf.conf", ()),
             ("examples/single_particle_in_free_space/single_particle_in_free_space.conf",
              pytest.mark.slowish),
             ("examples/single_particle_in_magnetic_field/single_particle_in_magnetic_field.conf",
              pytest.mark.slowish),
             ("examples/single_particle_in_magnetic_field/large_time_step.conf",
              pytest.mark.slowish),
             ("examples/tube_source_test/contour.conf",
              pytest.mark.slow),
             ("examples/single_particle_in_radial_electric_field/single_particle_in_radial_electric_field.conf",
              pytest.mark.slowish),
             ("examples/ribbon_beam_contour/contour_bin.conf",
              pytest.mark.slow),
             ("examples/ribbon_beam_contour/contour.conf",
              pytest.mark.slow),
             ("examples/drift_tube_potential/pot.conf",
              pytest.mark.slow)]

_pytest_params = [pytest.param(f.replace('/', os.path.sep), marks=m) for f, m in _examples]


@pytest.mark.parametrize("fname", _pytest_params)
def test_example(fname, mocker, capsys, tmpdir, monkeypatch):
    copyfile(fname, tmpdir.join(basename(fname)))
    monkeypatch.chdir(tmpdir)
    mocker.patch("sys.argv", ["main.py", str(basename(fname))])
    main()
    out, err = capsys.readouterr()
    assert err == ""


@pytest.mark.parametrize("fname", _pytest_params)
def test_main_shell(fname, tmpdir, monkeypatch):
    basedir = os.path.join(os.path.dirname(__file__), '..')
    monkeypatch.chdir(tmpdir)
    result = subprocess.run(['ef', os.path.join(basedir, fname)], check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in result.stderr.split("\n"):
        assert line == '' or line.startswith("WARNING:")
    assert result.stdout != ""
