# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
from typing import Any, Optional

from omegaconf import DictConfig, OmegaConf

from hydra.conf import HydraConf
from hydra.core.singleton import Singleton


class HydraConfig(metaclass=Singleton):
    def __init__(self) -> None:
        self.cfg: Optional[HydraConf] = None

    def set_config(self, cfg: DictConfig) -> None:
        assert cfg is not None
        OmegaConf.set_readonly(cfg.hydra, True)
        assert OmegaConf.get_type(cfg, "hydra") == HydraConf
        self.cfg = cfg  # type: ignore

    @staticmethod
    def get() -> HydraConf:
        instance = HydraConfig.instance()
        if instance.cfg is None:
            raise ValueError("HydraConfig was not set")
        return instance.cfg.hydra  # type: ignore

    @staticmethod
    def initialized() -> bool:
        instance = HydraConfig.instance()
        return instance.cfg is not None

    @staticmethod
    def instance(*args: Any, **kwargs: Any) -> "HydraConfig":
        return Singleton.instance(HydraConfig, *args, **kwargs)  # type: ignore
