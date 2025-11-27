import flet as ft
from nutrisync_2.Page import Page
from datetime import datetime

class History(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.workouts = []

    async def before_build(self):
        await self.load_workouts()

    async def load_workouts(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        self.workouts = await self.app.db.workout.find_many(
            where={'userId': self.app.current_user_id},
            order={'date': 'desc'},
            include={
                'exercises': True
            }
        )
        await self.app.db.disconnect()

    def build(self):
        workout_list = ft.ListView(
            spacing=10,
            padding=20,
            auto_scroll=True
        )

        for workout in self.workouts:
            workout_card = self.create_workout_card(workout)
            workout_list.controls.append(workout_card)

        return ft.Column([
            ft.Text("Workout History", size=24, weight=ft.FontWeight.BOLD),
            workout_list
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    def create_workout_card(self, workout):
        exercises_list = ft.Column(
            spacing=5,
            controls=[
                ft.Text(f"• {exercise.name}: {exercise.sets} sets, {exercise.reps} reps, {exercise.weight or 'N/A'} Kg")
                for exercise in workout.exercises
            ]
        )

        # Handle the date formatting
        formatted_date = workout.date.strftime('%Y-%m-%d') if isinstance(workout.date, datetime) else str(workout.date)

        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column([
                    ft.Text(
                        f"Date: {formatted_date}",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(f"Type: {workout.type}"),
                    ft.Text(f"Duration: {workout.duration} minutes"),
                    ft.Text("Exercises:", weight=ft.FontWeight.BOLD),
                    exercises_list,
                    ft.Text(f"Notes: {workout.notes or 'No notes'}", italic=True)
                ], spacing=10)
            )
        )