# This file contains the base Observer and Subject classes for the Observer pattern.

from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, national_code: str):
        """
        This method is called by the Subject when an event occurs (here, when a national_code is received).
        """
        pass


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        """
        Add an observer to the list of observers.
        """
        self._observers.append(observer)

    def detach(self, observer: Observer):
        """
        Remove an observer from the list of observers.
        """
        self._observers.remove(observer)

    def notify(self, national_code: str):
        """
        Call the update() method on all attached observers.
        """
        for observer in self._observers:
            observer.update(national_code)