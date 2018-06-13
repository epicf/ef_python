from ef.config.components import TimeGridConf, SpatialMeshConf
from ef.config.efconf import EfConf
from main import main


def test_main(mocker, tmpdir):
    config = tmpdir.join("test_main.conf")
    EfConf(TimeGridConf(4, 2, 1), SpatialMeshConf((3, 3, 3))).export_to_fname(str(config))
    mocker.patch("sys.argv", ["main.py", str(config)])
    main()
    assert True
