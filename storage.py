"""Работа с файлами: данные медиатеки (CSV) и отчёт о работе приложения."""
import csv
import os

from models import KindRegistry, SessionRecord


class Storage:
    @staticmethod
    def load_items(path):
        """Возвращает список элементов или None, если файла ещё нет."""
        if not os.path.exists(path):
            return None
        items = []
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                try:
                    items.append(KindRegistry.from_row(row))
                except (ValueError, IndexError):
                    continue  # пропускаем повреждённые строки
        return items

    @staticmethod
    def save_items(path, items):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for item in items:
                writer.writerow(item.to_row())


class ReportWriter:
    HEADER = ["login", "time_in", "time_out"]

    @staticmethod
    def load_records(path):
        records = []
        if not os.path.exists(path):
            return records
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|") or line.startswith("|-"):
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) != 3 or cells[0] == ReportWriter.HEADER[0]:
                    continue
                try:
                    records.append(SessionRecord.from_row(cells))
                except ValueError:
                    continue
        return records

    @staticmethod
    def render(records):
        rows = [r.to_row() for r in records]
        widths = [len(h) for h in ReportWriter.HEADER]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))

        def line(cells):
            return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

        header = line(ReportWriter.HEADER)
        border = "+" + "-" * (len(header) - 2) + "+"
        separator = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
        return "\n".join([border, header, separator]
                         + [line(r) for r in rows] + [border]) + "\n"

    @staticmethod
    def append(path, record):
        records = ReportWriter.load_records(path)
        records.append(record)
        with open(path, "w", encoding="utf-8") as f:
            f.write(ReportWriter.render(records))
