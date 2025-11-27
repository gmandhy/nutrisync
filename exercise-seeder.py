from prisma import Prisma
import asyncio

async def seed_exercises():
    db = Prisma()
    await db.connect()

    exercises = [
        # Chest Exercises
        {"name": "Bench Press", "category": "Chest"},
        {"name": "Incline Bench Press", "category": "Chest"},
        {"name": "Decline Bench Press", "category": "Chest"},
        {"name": "Dumbbell Press", "category": "Chest"},
        {"name": "Incline Dumbbell Press", "category": "Chest"},
        {"name": "Push-Ups", "category": "Chest"},
        {"name": "Dips", "category": "Chest"},
        {"name": "Cable Flyes", "category": "Chest"},
        {"name": "Dumbbell Flyes", "category": "Chest"},
        
        # Back Exercises
        {"name": "Pull-Ups", "category": "Back"},
        {"name": "Lat Pulldowns", "category": "Back"},
        {"name": "Barbell Rows", "category": "Back"},
        {"name": "Dumbbell Rows", "category": "Back"},
        {"name": "T-Bar Rows", "category": "Back"},
        {"name": "Face Pulls", "category": "Back"},
        {"name": "Deadlift", "category": "Back"},
        {"name": "Cable Rows", "category": "Back"},
        
        # Legs Exercises
        {"name": "Squats", "category": "Legs"},
        {"name": "Front Squats", "category": "Legs"},
        {"name": "Leg Press", "category": "Legs"},
        {"name": "Romanian Deadlift", "category": "Legs"},
        {"name": "Leg Extensions", "category": "Legs"},
        {"name": "Leg Curls", "category": "Legs"},
        {"name": "Calf Raises", "category": "Legs"},
        {"name": "Lunges", "category": "Legs"},
        {"name": "Bulgarian Split Squats", "category": "Legs"},
        
        # Shoulders Exercises
        {"name": "Military Press", "category": "Shoulders"},
        {"name": "Overhead Press", "category": "Shoulders"},
        {"name": "Lateral Raises", "category": "Shoulders"},
        {"name": "Front Raises", "category": "Shoulders"},
        {"name": "Reverse Flyes", "category": "Shoulders"},
        {"name": "Upright Rows", "category": "Shoulders"},
        {"name": "Arnold Press", "category": "Shoulders"},
        {"name": "Shrugs", "category": "Shoulders"},
        
        # Arms Exercises
        {"name": "Bicep Curls", "category": "Arms"},
        {"name": "Hammer Curls", "category": "Arms"},
        {"name": "Preacher Curls", "category": "Arms"},
        {"name": "Tricep Extensions", "category": "Arms"},
        {"name": "Tricep Pushdowns", "category": "Arms"},
        {"name": "Skull Crushers", "category": "Arms"},
        {"name": "Concentration Curls", "category": "Arms"},
        {"name": "Diamond Push-Ups", "category": "Arms"},
        
        # Core Exercises
        {"name": "Crunches", "category": "Core"},
        {"name": "Planks", "category": "Core"},
        {"name": "Russian Twists", "category": "Core"},
        {"name": "Leg Raises", "category": "Core"},
        {"name": "Ab Wheel Rollouts", "category": "Core"},
        {"name": "Mountain Climbers", "category": "Core"},
        {"name": "Hanging Leg Raises", "category": "Core"},
        {"name": "Wood Choppers", "category": "Core"},
        
        # Cardio Exercises
        {"name": "Treadmill Running", "category": "Cardio"},
        {"name": "Cycling", "category": "Cardio"},
        {"name": "Jump Rope", "category": "Cardio"},
        {"name": "Rowing", "category": "Cardio"},
        {"name": "Stair Climber", "category": "Cardio"},
        {"name": "Elliptical", "category": "Cardio"},
        {"name": "Burpees", "category": "Cardio"},
        {"name": "High Knees", "category": "Cardio"},
        
        # Compound Exercises
        {"name": "Clean and Press", "category": "Compound"},
        {"name": "Power Clean", "category": "Compound"},
        {"name": "Turkish Get-Up", "category": "Compound"},
        {"name": "Kettlebell Swings", "category": "Compound"},
        {"name": "Thrusters", "category": "Compound"},
        {"name": "Man Makers", "category": "Compound"},
    ]

    try:
        for exercise in exercises:
            await db.exerciseoption.create(data=exercise)
        print(f"Successfully seeded {len(exercises)} exercises")
    except Exception as e:
        print(f"Error seeding exercises: {str(e)}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_exercises())
