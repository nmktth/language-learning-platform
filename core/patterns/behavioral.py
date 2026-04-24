# ==========================================
# OBSERVER PATTERN
# ==========================================
class Observer:
    def update(self, message):
        pass

class ProgressNotifier(Observer):
    def update(self, message):
        print(f"NOTIFICATION: {message}")

class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

# ==========================================
# COMMAND PATTERN
# ==========================================
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class SubmitAnswerCommand(Command):
    def __init__(self, workflow, data):
        self.workflow = workflow
        self.data = data

    def execute(self):
        self.workflow.execute_workflow(self.data)

class Invoker:
    def __init__(self):
        self._history = []

    def store_and_execute(self, command: Command):
        self._history.append(command)
        command.execute()

# ==========================================
# ADAPTER PATTERN
# ==========================================
class LegacyExternalSystem:
    """Внешняя система, которую нужно подключить через адаптер"""
    def get_raw_scores(self):
        return {"user123": [10, 20, 30]}

class ScoreAdapter:
    """Адаптер для приведения данных внешней системы к нашему формату"""
    def __init__(self, legacy_system):
        self.legacy_system = legacy_system

    def get_formatted_progress(self):
        raw_data = self.legacy_system.get_raw_scores()
        # Преобразуем в наш формат (например, для мат. модели)
        return [{"score": s} for s in raw_data.get("user123", [])]
