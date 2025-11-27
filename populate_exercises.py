import asyncio
from prisma import Prisma

async def populate_exercise_options():
    db = Prisma()
    await db.connect()

    exercises = [
        "Bench Press", "Squat", "Deadlift", "Overhead Press",
        "Barbell Row", "Pull-up", "Dip", "Leg Press",
        "Lat Pulldown", "Bicep Curl", "Tricep Extension", "Leg Curl",
        "Leg Extension", "Calf Raise", "Shoulder Press", "Lateral Raise"
    ]

    for exercise in exercises:
        await db.exerciseoption.create(
            data={"name": exercise}
        )

    await db.disconnect()

asyncio.run(populate_exercise_options())