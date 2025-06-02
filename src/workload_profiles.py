# model/workload_profiles.py

from util import Settings
from abc import ABC, abstractmethod
import numpy as np

class WorkloadProfile(ABC):
    @abstractmethod
    def get_arrival_rate(self) -> float:
        """Return λ: task arrival rate (tasks/sec)"""
        pass

    @abstractmethod
    def get_task_size_rate(self) -> float:
        """Return μ: mean task size (MB) for exponential sampling"""
        pass


class DefaultProfile(WorkloadProfile):
    def get_arrival_rate(self):
        return np.random.uniform(Settings.lambda_min, Settings.lambda_max)

    def get_task_size_rate(self):
        return np.random.uniform(Settings.task_size_min, Settings.task_size_max)  # e.g., 0.75


class ARProfile(WorkloadProfile):
    def get_arrival_rate(self):
        return np.random.uniform(Settings.ar_lambda_min, Settings.ar_lambda_max)

    def get_task_size_rate(self):
        return np.random.uniform(Settings.ar_task_size_min, Settings.ar_task_size_max)  # e.g., 0.14

