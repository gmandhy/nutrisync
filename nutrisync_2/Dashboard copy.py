import flet as ft
import datetime
from nutrisync_2.Page import Page

class Dashboard(Page):
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
                        ft.Row([ft.Icon(ft.icons.CALENDAR_TODAY), ft.Text("This Week's Progress", weight=ft.FontWeight.BOLD)]),
                        ft.ProgressBar(width=None, value=0.6, height=20),
                        ft.Text("3 out of 5 visits completed", size=14, color=ft.colors.GREY),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Metrics Row
        metrics_row = ft.Row(
            [
                create_metric_container("Total Visits", "42", ft.icons.FITNESS_CENTER),
                create_metric_container("Current Streak", "7 days", ft.icons.EMOJI_EVENTS),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Quick Log Workout Button
        log_workout_button = ft.ElevatedButton(
            "Log Workout",
            icon=ft.icons.ADD,
            on_click=lambda _: self.app.navigate("/log-workout")
        )

        # Motivational Quote
        motivational_quote = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Today's Motivation", weight=ft.FontWeight.BOLD),
                        ft.Text("The only bad workout is the one that didn't happen.", 
                                italic=True, size=14),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Recent Achievements
        recent_achievements = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Recent Achievements", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Icon(ft.icons.STAR, color=ft.colors.YELLOW),
                            ft.Text("5-Day Streak Achieved!", size=14),
                        ]),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Upcoming Goals
        upcoming_goals = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Upcoming Goals", weight=ft.FontWeight.BOLD),
                        ft.Text("• Complete 20 workouts this month", size=14),
                        ft.Text("• Increase bench press by 10 lbs", size=14),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        # Recent Workouts
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
                            rows=[
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(datetime.datetime.now().strftime("%Y-%m-%d"))),
                                    ft.DataCell(ft.Text("Strength")),
                                    ft.DataCell(ft.Text("60 min")),
                                ]),
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))),
                                    ft.DataCell(ft.Text("Cardio")),
                                    ft.DataCell(ft.Text("45 min")),
                                ]),
                            ],
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
        )

        return ft.Column([
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
            log_workout_button,
            weekly_progress,
            metrics_row,
            motivational_quote,
            recent_achievements,
            upcoming_goals,
            recent_workouts,
        ], spacing=20, scroll=ft.ScrollMode.AUTO)