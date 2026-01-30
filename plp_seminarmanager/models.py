"""Data models for ProfiLehrePlus seminar management."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional


class DeliveryMode(str, Enum):
    """Seminar delivery mode derived from the announcement text."""

    PRESENCE = "praesenz"
    ONLINE = "online"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SeminarLink:
    """A link associated with a seminar."""

    label: str
    url: str


@dataclass
class SeminarDetail:
    """Details parsed from a seminar announcement page."""

    description: str
    delivery_mode: DeliveryMode
    registered_count: Optional[int] = None
    links: list[SeminarLink] = field(default_factory=list)

    def link_urls(self) -> list[str]:
        return [link.url for link in self.links]


@dataclass
class Seminar:
    """Seminar metadata parsed from the management overview."""

    seminar_id: Optional[str]
    title: str
    management_url: Optional[str] = None
    links: list[SeminarLink] = field(default_factory=list)
    detail: Optional[SeminarDetail] = None

    def all_links(self) -> list[SeminarLink]:
        merged = list(self.links)
        if self.detail:
            merged.extend(self.detail.links)
        return merged

    def link_urls(self) -> list[str]:
        return [link.url for link in self.all_links()]


@dataclass
class Task:
    """Team task related to a seminar (e.g., send mail 14 days before)."""

    seminar_id: Optional[str]
    title: str
    due_date: str
    assigned_to: str
    completed: bool = False
    notes: Optional[str] = None


@dataclass
class TaskManager:
    """In-memory task manager."""

    tasks: list[Task] = field(default_factory=list)

    def add_task(
        self,
        *,
        seminar_id: Optional[str],
        title: str,
        due_date: str,
        assigned_to: str,
        notes: Optional[str] = None,
    ) -> Task:
        task = Task(
            seminar_id=seminar_id,
            title=title,
            due_date=due_date,
            assigned_to=assigned_to,
            notes=notes,
        )
        self.tasks.append(task)
        return task

    def complete_task(self, task: Task) -> None:
        task.completed = True

    def tasks_for_seminar(self, seminar_id: Optional[str]) -> Iterable[Task]:
        return [task for task in self.tasks if task.seminar_id == seminar_id]
