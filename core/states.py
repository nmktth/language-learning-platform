from abc import ABC, abstractmethod


class EnrollmentState(ABC):
    @abstractmethod
    def complete(self, enrollment):
        raise NotImplementedError

    @abstractmethod
    def pause(self, enrollment):
        raise NotImplementedError

    @abstractmethod
    def resume(self, enrollment):
        raise NotImplementedError


class ActiveState(EnrollmentState):
    def complete(self, enrollment):
        enrollment.status = 'completed'
        enrollment.save(update_fields=['status'])

    def pause(self, enrollment):
        enrollment.status = 'paused'
        enrollment.save(update_fields=['status'])

    def resume(self, enrollment):
        return None


class CompletedState(EnrollmentState):
    def complete(self, enrollment):
        return None

    def pause(self, enrollment):
        return None

    def resume(self, enrollment):
        return None


class PausedState(EnrollmentState):
    def complete(self, enrollment):
        return None

    def pause(self, enrollment):
        return None

    def resume(self, enrollment):
        enrollment.status = 'active'
        enrollment.save(update_fields=['status'])


class EnrollmentContext:
    def __init__(self, enrollment):
        self.enrollment = enrollment
        self.state = self._resolve_state(enrollment.status)

    def _resolve_state(self, status):
        if status == 'completed':
            return CompletedState()
        if status == 'paused':
            return PausedState()
        return ActiveState()

    def complete(self):
        self.state.complete(self.enrollment)
        return self.enrollment

    def pause(self):
        self.state.pause(self.enrollment)
        return self.enrollment

    def resume(self):
        self.state.resume(self.enrollment)
        return self.enrollment
