import flet as ft
from prisma import Prisma
import bcrypt
import asyncio
from functools import partial

from nutrisync_2.Page import Page
from nutrisync_2.Dashboard import Dashboard as DashboardPage
from nutrisync_2.Profile import Profile as ProfilePage
from nutrisync_2.History import History as HistoryPage
from nutrisync_2.WorkoutLogger import WorkoutLogger as WorkoutLoggerPage
from nutrisync_2.WorkoutPlans import WorkoutPlans as WorkoutPlansPage
from nutrisync_2.ProgressTracking import ProgressTracking as ProgressTrackingPage
from nutrisync_2.LoginPage import LoginPage

class GymTrackerApp:
    def __init__(self):
        self.pages = {}
        self.current_route = "/login"
        self.is_authenticated = False
        self.current_user_id = 0
        self.db:Prisma = Prisma()


    async def initialize(self, page: ft.Page):
        self.page = page
        self.page.title = "GymTracker"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20

        # Initialize pages
        self.pages["/"] = DashboardPage(self, "Dashboard", "/")
        self.pages["/login"] = LoginPage(self, "Login", "/login")
        self.pages["/profile"] = ProfilePage(self, "Profile", "/profile")
        self.pages["/history"] = HistoryPage(self, "History", "/history")
        self.pages["/log-workout"] = WorkoutLoggerPage(self, "Log Workout", "/log-workout")
        # self.pages["/workout-plans"] = WorkoutPlansPage(self, "Workout Plans", "/workout-plans")
        self.pages["/progress"] = ProgressTrackingPage(self, "Progress Tracking", "/progress")

        # Navigation bar
        self.nav_bar = ft.Row(
            [
                ft.IconButton(icon=ft.icons.DASHBOARD, selected_icon=ft.icons.DASHBOARD_OUTLINED,key="/", on_click=partial(self.handle_async_navigation, "/")),
                ft.IconButton(icon=ft.icons.PERSON, selected_icon=ft.icons.PERSON_OUTLINED,key="/profile", on_click=partial(self.handle_async_navigation, "/profile")),
                ft.IconButton(icon=ft.icons.HISTORY, selected_icon=ft.icons.HISTORY_OUTLINED,key="/history",on_click=partial(self.handle_async_navigation, "/history")),
                ft.IconButton(icon=ft.icons.ADD_CHART, selected_icon=ft.icons.ADD_CHART_OUTLINED,key="/log-workout", on_click=partial(self.handle_async_navigation, "/log-workout")),
                # ft.IconButton(icon=ft.icons.FITNESS_CENTER, selected_icon=ft.icons.FITNESS_CENTER_OUTLINED,key="/workout-plans", on_click=partial(self.handle_async_navigation, "/workout-plans")),
                ft.IconButton(icon=ft.icons.TRENDING_UP, selected_icon=ft.icons.TRENDING_UP_OUTLINED,key="/progress", on_click=partial(self.handle_async_navigation, "/progress")),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )

        # Main content area
        self.content_area = ft.Container(content=self.pages["/login"].build(), expand=True)

        # Main layout
        self.main_column = ft.Column(
            [
                self.content_area,
                self.nav_bar,
            ],
            expand=True,
        )
        self.page.add(self.main_column)

        # Initial navigation
        await self.navigate("/login")

    async def handle_async_navigation(self, route, _):
        asyncio.create_task(self.navigate(route))

    async def navigate(self, route):
        if not self.is_authenticated and route != "/login":
            print("User is not authenticated. Redirecting to login.")
            route = "/login"
        
        # Call before_build to handle any async operations
        await self.pages[route].before_build()
        
        # Now set the content using the synchronous build method
        self.content_area.content = self.pages[route].build()
        self.current_route = route
        
        # Show/hide navigation bar based on the current route
        if route == "/login":
            self.nav_bar.visible = False
        else:
            self.nav_bar.visible = True
            for nav_button in self.nav_bar.controls:
                if isinstance(nav_button, ft.IconButton):
                    nav_button.disabled = nav_button.key == route
        
        await self.page.update_async()

    async def login(self, email, password):
        if not self.db.is_connected():
            await self.db.connect()
        user = await self.db.user.find_first(where={'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            self.is_authenticated = True
            self.current_user_id = user.id
            await self.navigate("/")  # Navigate to dashboard after successful login
        else:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Invalid email or password")))

    async def logout(self):
        self.is_authenticated = False
        await self.navigate("/login")