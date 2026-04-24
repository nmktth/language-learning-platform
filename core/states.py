from abc import ABC, abstractmethod

class EnrollmentState(ABC):
    @abstractmethod
    def complete(self, enrollment):
        pass

    @abstractmethod
    def pause(self, enrollment):
        pass

class ActiveState(EnrollmentState):
    def complete(self, enrollment):
        enrollment.status = 'completed'
        enrollment.save()
        print(f"Course {enrollment.course.title} completed by {enrollment.user.username}")

    def pause(self, enrollment):
        enrollment.status = 'paused'
        enrollment.save()
        print(f"Course {enrollment.course.title} paused by {enrollment.user.username}")

class CompletedState(EnrollmentState):
    def complete(self, enrollment):
        print("Already completed.")

    def pause(self, enrollment):
        print("Cannot pause a completed course.")

class PausedState(EnrollmentState):
    def complete(self, enrollment):
        print("Cannot complete a paused course directly.")

    def pause(self, enrollment):
        print("Already paused.")
