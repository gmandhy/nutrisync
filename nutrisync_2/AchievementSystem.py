import asyncio
from datetime import datetime, timedelta
import pytz

class AchievementSystem:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        
    async def check_achievements(self):
        """Check for new achievements after a workout is logged."""
        achievements = []
        
        # Get all user workouts
        workouts = await self.db.workout.find_many(
            where={'userId': self.user_id},
            include={'exercises': True}
        )
        
        # Get current streak
        streak = await self.db.streak.find_first(
            where={'userId': self.user_id},
            order={'endDate': 'desc'}
        )
        
        # Check total workouts achievements
        total_workouts = len(workouts)
        workout_milestones = {
            1: "First Workout",
            5: "Getting Started",
            10: "Dedicated Athlete",
            25: "Fitness Enthusiast",
            50: "Workout Warrior",
            100: "Centurion",
            200: "Double Centurion",
            365: "Year-Round Athlete"
        }
        
        for count, title in workout_milestones.items():
            if total_workouts >= count:
                await self._award_achievement(
                    title,
                    f"Completed {count} workouts!",
                    achievements
                )
        
        # Check streak achievements
        if streak:
            streak_milestones = {
                3: "Three-Day Streak",
                7: "Week Warrior",
                14: "Two-Week Terror",
                30: "Monthly Master",
                60: "Consistency King",
                90: "Quarterly Champion",
                180: "Half-Year Hero",
                365: "Year of Dedication"
            }
            
            for days, title in streak_milestones.items():
                if streak.currentStreak >= days:
                    await self._award_achievement(
                        title,
                        f"Maintained a {days}-day workout streak!",
                        achievements
                    )
        
        # Check exercise variety achievements
        unique_exercises = set()
        for workout in workouts:
            for exercise in workout.exercises:
                unique_exercises.add(exercise.name)
                
        variety_milestones = {
            5: "Jack of All Trades",
            10: "Exercise Explorer",
            20: "Variety Virtuoso",
            30: "Master of Many",
        }
        
        exercise_count = len(unique_exercises)
        for count, title in variety_milestones.items():
            if exercise_count >= count:
                await self._award_achievement(
                    title,
                    f"Performed {count} different exercises!",
                    achievements
                )
        
        # Check weekly consistency
        now = datetime.now(pytz.utc)
        one_week_ago = now - timedelta(days=7)
        recent_workouts = [w for w in workouts if w.date >= one_week_ago]
        
        if len(recent_workouts) >= 3:
            await self._award_achievement(
                "Weekly Warrior",
                "Completed 3 or more workouts in a week!",
                achievements
            )
        
        if len(recent_workouts) >= 5:
            await self._award_achievement(
                "Five-Star Week",
                "Completed 5 or more workouts in a week!",
                achievements
            )
        
        # Check workout duration achievements
        duration_milestones = {
            60: "Hour Champion",
            90: "Endurance Explorer",
            120: "Marathon Trainer"
        }
        
        for workout in workouts:
            for duration, title in duration_milestones.items():
                if workout.duration >= duration:
                    await self._award_achievement(
                        title,
                        f"Completed a {duration}-minute workout!",
                        achievements
                    )
        
        return achievements
    
    async def _award_achievement(self, title, description, achievements_list):
        """Award an achievement if it hasn't been earned yet."""
        existing_achievement = await self.db.achievement.find_first(
            where={
                'userId': self.user_id,
                'title': title
            }
        )
        
        if not existing_achievement:
            new_achievement = await self.db.achievement.create(
                data={
                    'userId': self.user_id,
                    'title': title,
                    'description': description,
                    'dateEarned': datetime.now(pytz.utc)
                }
            )
            achievements_list.append(new_achievement)
