"""Seminar management parsing utilities for ProfiLehrePlus."""

from .models import DeliveryMode, Seminar, SeminarDetail, SeminarLink, Task
from .parser import parse_detail_html, parse_management_html
from .task_manager import TaskManager

__all__ = [
    "DeliveryMode",
    "Seminar",
    "SeminarDetail",
    "SeminarLink",
    "Task",
    "TaskManager",
    "parse_detail_html",
    "parse_management_html",
]
