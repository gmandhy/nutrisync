import flet as ft

from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from nutrisync_2.GymTrackerApp import GymTrackerApp

class Page:
    def __init__(self, app:'GymTrackerApp', name, route):
        self.app = app
        self.name = name
        self.route = route
    
    async def before_build(self):
        # Perform any async operations here
        pass

    def build(self):
        raise NotImplementedError
    