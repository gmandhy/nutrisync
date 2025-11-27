from prisma import Prisma
import asyncio

async def clean_database():
    print("Starting database cleanup...")
    db = Prisma()
    await db.connect()

    try:
        # Delete records from all tables in the correct order to respect foreign key constraints
        
        # First, delete dependent tables
        print("Deleting exercises...")
        await db.exercise.delete_many()
        
        print("Deleting plan exercises...")
        await db.planexercise.delete_many()
        
        print("Deleting achievements...")
        await db.achievement.delete_many()
        
        print("Deleting goals...")
        await db.goal.delete_many()
        
        print("Deleting streaks...")
        await db.streak.delete_many()
        
        print("Deleting exercise options...")
        await db.exerciseoption.delete_many()
        
        print("Deleting motivational quotes...")
        await db.motivationalquote.delete_many()
        
        print("Deleting workouts...")
        await db.workout.delete_many()
        
        print("Deleting workout plans...")
        await db.workoutplan.delete_many()
        
        # Finally, delete users
        print("Deleting users...")
        await db.user.delete_many()
        
        print("Database cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error during database cleanup: {str(e)}")
        
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(clean_database())
