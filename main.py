import flet as ft
from nutrisync_2.Page import Page
from nutrisync_2.GymTrackerApp import GymTrackerApp

async def main(page: ft.Page):
    app = GymTrackerApp()
    await app.initialize(page)

ft.app(main)
