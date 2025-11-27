import flet as ft
import datetime
from nutrisync_2.Page import Page
from functools import partial
import asyncio
from datetime import datetime, timedelta
import pytz

class Dashboard(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.total_visits = 0
        self.current_streak = 0
        self.recent_workouts = []
        self.weekly_progress = 0
        self.weekly_target = 5  # Can be made configurable later
        self.achievements = []
        self.quote = None

    async def before_build(self):
        await self.load_dashboard_data()

    def to_rfc3339(self, dt):
        """Convert a datetime object to RFC 3339 format."""
        return dt.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    async def load_dashboard_data(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        try:
            # Load total visits
            self.total_visits = await self.app.db.workout.count(
                where={'userId': self.app.current_user_id}
            )

            # Load current streak
            streak = await self.app.db.streak.find_first(
                where={'userId': self.app.current_user_id},
                order={'endDate': 'desc'}
            )
            self.current_streak = streak.currentStreak if streak else 0

            # Load this week's workouts
            week_start = datetime.now(pytz.utc) - timedelta(days=datetime.now(pytz.utc).weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            self.weekly_progress = await self.app.db.workout.count(
                where={
                    'userId': self.app.current_user_id,
                    'date': {
                        'gte': self.to_rfc3339(week_start)
                    }
                }
            )

            # Load recent workouts
            self.recent_workouts = await self.app.db.workout.find_many(
                where={'userId': self.app.current_user_id},
                order={'date': 'desc'},
                take=5  # Get last 5 workouts
            )

            # Load recent achievements
            self.achievements = await self.app.db.achievement.find_many(
                where={'userId': self.app.current_user_id},
                order={'dateEarned': 'desc'},
                take=3  # Get last 3 achievements
            )

            # Load random motivational quote
            self.quote = await self.app.db.motivationalquote.find_first(
                order=[{'dateDisplayed': 'asc'}]  # Get least recently displayed quote
            )
            
            if self.quote:
                # Update quote's display date
                await self.app.db.motivationalquote.update(
                    where={'id': self.quote.id},
                    data={'dateDisplayed': self.to_rfc3339(datetime.now(pytz.utc))}
                )

        finally:
            await self.app.db.disconnect()

    async def handle_async_navigation(self, route, _):
        asyncio.create_task(self.app.navigate(route))

    def build(self):
        def create_metric_container(title: str, value: str, icon: str):
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=icon, size=24),
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=150,
                height=100,
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                padding=10,
            )

        # Weekly Progress Card
        weekly_progress = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.icons.CALENDAR_TODAY), 
                            ft.Text("This Week's Progress", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.ProgressBar(
                            width=None, 
                            value=self.weekly_progress / self.weekly_target 
                            if self.weekly_target > 0 else 0,
                            height=20
                        ),
                        ft.Text(
                            f"{self.weekly_progress} out of {self.weekly_target} visits completed", 
                            size=14, 
                            color=ft.colors.GREY
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Metrics Row
        metrics_row = ft.Row(
            [
                create_metric_container(
                    "Total Visits", 
                    str(self.total_visits), 
                    ft.icons.FITNESS_CENTER
                ),
                create_metric_container(
                    "Current Streak", 
                    f"{self.current_streak} days", 
                    ft.icons.EMOJI_EVENTS
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Quick Log Workout Button
        log_workout_button = ft.ElevatedButton(
            "Log Workout",
            icon=ft.icons.ADD,
            on_click=partial(self.handle_async_navigation, "/log-workout")
        )

        # Motivational Quote
        motivational_quote = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Today's Motivation", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            self.quote.quote if self.quote else "Stay consistent, stay strong!", 
                            italic=True, 
                            size=14
                        ),
                        ft.Text(
                            f"- {self.quote.author}" if self.quote and self.quote.author else "",
                            size=12,
                            color=ft.colors.GREY
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Recent Achievements
        achievement_items = []
        if self.achievements:
            for achievement in self.achievements:
                achievement_items.append(
                    ft.Row([
                        ft.Icon(ft.icons.STAR, color=ft.colors.YELLOW),
                        ft.Text(achievement.title, size=14),
                        ft.Text(
                            achievement.dateEarned.strftime("%Y-%m-%d"), 
                            size=12, 
                            color=ft.colors.GREY
                        ),
                    ])
                )
        else:
            achievement_items.append(
                ft.Text("No achievements yet. Keep working!", size=14)
            )

        recent_achievements = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Recent Achievements", weight=ft.FontWeight.BOLD),
                        *achievement_items,
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Recent Workouts
        workout_rows = []
        if self.recent_workouts:
            for workout in self.recent_workouts:
                workout_date = workout.date
                if isinstance(workout_date, str):
                    workout_date = datetime.fromisoformat(workout_date.replace('Z', '+00:00'))
                
                workout_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(workout_date.strftime("%Y-%m-%d"))),
                            ft.DataCell(ft.Text(workout.type)),
                            ft.DataCell(ft.Text(f"{workout.duration} min")),
                        ]
                    )
                )
        else:
            workout_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No workouts logged yet")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )

        recent_workouts = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Recent Workouts", weight=ft.FontWeight.BOLD),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Date")),
                                ft.DataColumn(ft.Text("Type")),
                                ft.DataColumn(ft.Text("Duration")),
                            ],
                            rows=workout_rows,
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        return ft.Column(
            [
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                log_workout_button,
                weekly_progress,
                metrics_row,
                motivational_quote,
                recent_achievements,
                recent_workouts,
            ], 
            spacing=20, 
            scroll=ft.ScrollMode.AUTO
        )