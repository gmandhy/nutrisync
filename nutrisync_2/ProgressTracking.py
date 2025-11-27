import flet as ft
from nutrisync_2.Page import Page
from datetime import datetime, timedelta
import pytz
from collections import defaultdict

class ProgressTracking(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.workouts = []
        self.date_range = "month"
        self.workout_stats = ft.Column(spacing=10)
        self.exercise_progress = ft.Column(spacing=10)

    async def before_build(self):
        await self.load_workouts()
        self.process_workout_data()

    async def load_workouts(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        # Get workouts for the last 30 days
        thirty_days_ago = datetime.now(pytz.utc) - timedelta(days=30)
        
        self.workouts = await self.app.db.workout.find_many(
            where={
                'userId': self.app.current_user_id,
                'date': {
                    'gte': thirty_days_ago.isoformat()
                }
            },
            include={
                'exercises': True
            },
            order={
                'date': 'asc'
            }
        )
        
        await self.app.db.disconnect()

    def process_workout_data(self):
        # Process workout statistics
        workout_by_date = defaultdict(int)
        for workout in self.workouts:
            date = workout.date.strftime("%Y-%m-%d") if isinstance(workout.date, datetime) else workout.date.split('T')[0]
            workout_by_date[date] += 1

        # Clear existing stats
        self.workout_stats.controls.clear()
        
        # Add workout frequency stats
        total_workouts = len(self.workouts)
        avg_workouts_per_week = total_workouts / 4  # Assuming monthly view
        
        self.workout_stats.controls.extend([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Workout Statistics", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text(f"Total Workouts: {total_workouts}"),
                        ft.Text(f"Average Workouts per Week: {avg_workouts_per_week:.1f}"),
                        ft.Text(f"Most Active Day: {max(workout_by_date.items(), key=lambda x: x[1])[0]} ({max(workout_by_date.values())} workouts)"),
                    ]),
                    padding=20,
                )
            )
        ])

        # Process exercise progress
        exercise_progress = defaultdict(list)
        for workout in self.workouts:
            for exercise in workout.exercises:
                if exercise.weight:
                    exercise_progress[exercise.name].append({
                        'date': workout.date,
                        'weight': exercise.weight
                    })

        # Clear existing progress cards
        self.exercise_progress.controls.clear()

        # Create progress cards
        for exercise_name, data in exercise_progress.items():
            if len(data) > 1:
                initial_weight = data[0]['weight']
                current_weight = data[-1]['weight']
                progress = current_weight - initial_weight
                progress_color = ft.colors.GREEN if progress > 0 else ft.colors.RED
                max_weight = max(d['weight'] for d in data)

                self.exercise_progress.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(exercise_name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                ft.Text(f"Current Weight: {current_weight} kg"),
                                ft.Text(f"Personal Best: {max_weight} kg", color=ft.colors.BLUE),
                                ft.Text(
                                    f"Progress: {'+' if progress > 0 else ''}{progress:.1f} kg",
                                    color=progress_color
                                ),
                                ft.ProgressBar(
                                    value=current_weight / max_weight,
                                    color=progress_color,
                                    bgcolor=ft.colors.GREY_300,
                                ),
                            ]),
                            padding=20,
                        )
                    )
                )

    def on_date_range_change(self, e):
        self.date_range = e.control.value
        self.process_workout_data()
        self.app.page.update()

    def build(self):
        date_range_dropdown = ft.Dropdown(
            label="Date Range",
            width=200,
            options=[
                ft.dropdown.Option("week", "Last Week"),
                ft.dropdown.Option("month", "Last Month"),
                ft.dropdown.Option("year", "Last Year"),
            ],
            value=self.date_range,
            on_change=self.on_date_range_change
        )

        return ft.Column([
            ft.Text("Progress Tracking", size=24, weight=ft.FontWeight.BOLD),
            date_range_dropdown,
            
            # Workout Statistics
            self.workout_stats,
            
            # Exercise Progress
            ft.Container(
                content=ft.Column([
                    ft.Text("Exercise Progress", size=18, weight=ft.FontWeight.BOLD),
                    self.exercise_progress,
                ]),
                padding=ft.padding.only(top=20)
            ),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)