# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import os

import pytest
from omegaconf import OmegaConf

from hydra._internal.config_loader import ConfigLoader
from hydra.errors import MissingConfigException
from hydra.test_utils.test_utils import chdir_hydra_root

chdir_hydra_root()


def test_override_run_dir_without_hydra_cfg():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf"], strict_cfg=False, conf_filename=None
    )
    cfg = config_loader.load_configuration(overrides=["hydra.run.dir=abc"])
    assert cfg.hydra.run.dir == "abc"


def test_override_run_dir_with_hydra_cfg():
    config_loader = ConfigLoader(
        config_path=[
            "pkg://hydra.default_conf",
            "demos/99_hydra_configuration/workdir/",
        ],
        strict_cfg=False,
        conf_filename=None,
    )
    cfg = config_loader.load_configuration(overrides=["hydra.run.dir=abc"])
    assert cfg.hydra.run.dir == "abc"


def test_load_configuration():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "demos/3_config_file"],
        strict_cfg=False,
        conf_filename="config.yaml",
    )
    cfg = config_loader.load_configuration(overrides=["abc=123"])
    del cfg["hydra"]
    assert cfg == OmegaConf.create(
        dict(abc=123, dataset=dict(name="imagenet", path="/datasets/imagenet"))
    )


def test_load_with_missing_default():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="missing-default.yaml",
    )
    with pytest.raises(MissingConfigException):
        config_loader.load_configuration()


def test_load_with_missing_optional_default():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="missing-optional-default.yaml",
    )
    cfg = config_loader.load_configuration()
    del cfg["hydra"]
    assert cfg == {}


def test_load_with_optional_default():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="optional-default.yaml",
    )
    cfg = config_loader.load_configuration()
    del cfg["hydra"]
    assert cfg == dict(foo=10)


def test_load_changing_group_in_default():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="optional-default.yaml",
    )
    cfg = config_loader.load_configuration(["group1=file2"])
    del cfg["hydra"]
    assert cfg == dict(foo=20)


def test_load_adding_group_not_in_default():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="optional-default.yaml",
    )
    cfg = config_loader.load_configuration(["group2=file1"])
    del cfg["hydra"]
    assert cfg == dict(foo=10, bar=100)


def test_load_history():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="missing-optional-default.yaml",
    )
    config_loader.load_configuration()
    assert config_loader.get_load_history() == [
        ("pkg://hydra.default_conf/default_hydra.yaml", True),
        ("tests/configs/missing-optional-default.yaml", True),
        ("pkg://hydra.default_conf.hydra_logging/default.yaml", True),
        ("pkg://hydra.default_conf.job_logging/default.yaml", True),
        ("pkg://hydra.default_conf.launcher/basic.yaml", True),
        ("pkg://hydra.default_conf.sweeper/basic.yaml", True),
        ("foo/missing.yaml", False),
    ]


def test_load_history_with_basic_launcher():
    config_loader = ConfigLoader(
        config_path=[
            "pkg://hydra.default_conf",
            "demos/6_sweep/conf",
            os.path.join("demos/6_sweep/conf", ".hydra"),
        ],
        strict_cfg=False,
        conf_filename="config.yaml",
    )
    config_loader.load_configuration(overrides=["launcher=basic"])

    assert config_loader.get_load_history() == [
        ("pkg://hydra.default_conf/default_hydra.yaml", True),
        ("demos/6_sweep/conf/.hydra/hydra.yaml", True),
        ("demos/6_sweep/conf/config.yaml", True),
        ("pkg://hydra.default_conf.hydra_logging/default.yaml", True),
        ("pkg://hydra.default_conf.job_logging/default.yaml", True),
        ("pkg://hydra.default_conf.launcher/basic.yaml", True),
        ("pkg://hydra.default_conf.sweeper/basic.yaml", True),
        ("demos/6_sweep/conf/optimizer/nesterov.yaml", True),
    ]


def test_load_strict():
    """
    Ensure that in strict mode we can override only things that are already in the config
    :return:
    """
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "demos/3_config_file"],
        conf_filename="config.yaml",
        strict_cfg=True,
    )
    cfg = config_loader.load_configuration(overrides=["dataset.name=foobar"])
    del cfg["hydra"]
    assert cfg == dict(dataset=dict(name="foobar", path="/datasets/imagenet"))
    with pytest.raises(KeyError):
        cfg.not_here

    with pytest.raises(KeyError):
        cfg.dataset.not_here

    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "demos/3_config_file"],
        conf_filename="config.yaml",
        strict_cfg=True,
    )
    with pytest.raises(KeyError):
        config_loader.load_configuration(overrides=["dataset.bad_key=foobar"])


def test_load_yml_file():
    config_loader = ConfigLoader(
        config_path=["pkg://hydra.default_conf", "tests/configs"],
        strict_cfg=False,
        conf_filename="config.yml",
    )
    cfg = config_loader.load_configuration()
    del cfg["hydra"]
    assert cfg == dict(yml_file_here=True)