from abc import ABC, abstractmethod

class WorkflowTemplate(ABC):
    """
    Template Method Design Pattern.
    Определяет скелет алгоритма (BPMN процесса) в базовом классе.
    """
    def execute_workflow(self, data):
        self.step_start(data)
        if self.step_validate(data):
            self.step_process(data)
            self.step_log_progress(data)
        self.step_end(data)

    def step_start(self, data):
        print("Workflow Started...")

    @abstractmethod
    def step_validate(self, data) -> bool:
        pass

    @abstractmethod
    def step_process(self, data):
        pass

    @abstractmethod
    def step_log_progress(self, data):
        pass

    def step_end(self, data):
        print("Workflow Ended.\n")


class ExerciseCompletionWorkflow(WorkflowTemplate):
    """
    Делегирование субклассирования для процесса валидации упражнения из BPMN.
    """
    def __init__(self, validation_strategy):
        self.strategy = validation_strategy

    def step_validate(self, data) -> bool:
        print("Validating input data...")
        return "user_answer" in data and "correct_answer" in data

    def step_process(self, data):
        print("Processing exercise strategy...")
        self.is_correct = self.strategy.validate(data["user_answer"], data["correct_answer"])
        print(f"Result is correct: {self.is_correct}")

    def step_log_progress(self, data):
        print("Logging progress to database and updating math model...")
        # Здесь будет логика вызова БД
        pass
