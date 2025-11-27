import asyncio
from datetime import datetime
import pytz

# Constants instead of enum
class GoalType:
    TARGET_WEIGHT = 0
    WORKOUT_COUNT = 1
    EXERCISE_WEIGHT = 2

    @staticmethod
    def to_string(goal_type):
        if goal_type == GoalType.TARGET_WEIGHT:
            return "Target Weight"
        elif goal_type == GoalType.WORKOUT_COUNT:
            return "Workout Count"
        elif goal_type == GoalType.EXERCISE_WEIGHT:
            return "Exercise Weight"
        return "Unknown"

class GoalSystem:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    async def check_and_update_goals(self, workout=None):
        """Updates all goals based on new workout data"""
        if not self.db.is_connected():
            await self.db.connect()

        try:
            active_goals = await self.db.goal.find_many(
                where={
                    'userId': self.user_id,
                    'completed': False
                }
            )

            for goal in active_goals:
                if goal.goalType == GoalType.WORKOUT_COUNT:
                    await self._update_workout_count_goal(goal)
                elif goal.goalType == GoalType.EXERCISE_WEIGHT and workout:
                    await self._update_exercise_weight_goal(goal, workout)
                # TARGET_WEIGHT goals are updated manually when user inputs weight

        finally:
            await self.db.disconnect()

    async def _update_workout_count_goal(self, goal):
        """Update progress for workout count goals"""
        # Calculate the number of workouts in the target period
        start_date = goal.startDate
        end_date = goal.targetDate or datetime.now(pytz.utc)

        workout_count = await self.db.workout.count(
            where={
                'userId': self.user_id,
                'date': {
                    'gte': start_date.isoformat(),
                    'lte': end_date.isoformat()
                }
            }
        )

        # Update the goal's current value
        await self.db.goal.update(
            where={'id': goal.id},
            data={
                'currentValue': float(workout_count),
                'completed': workout_count >= goal.targetValue
            }
        )

    async def _update_exercise_weight_goal(self, goal, workout):
        """Update progress for exercise weight goals"""
        if not workout.exercises:
            return

        # Find matching exercise in workout
        for exercise in workout.exercises:
            if exercise.name == goal.exerciseName and exercise.weight:
                # Update if this is a new personal best
                if exercise.weight > goal.currentValue:
                    await self.db.goal.update(
                        where={'id': goal.id},
                        data={
                            'currentValue': float(exercise.weight),
                            'completed': exercise.weight >= goal.targetValue
                        }
                    )

    async def update_weight_goal(self, current_weight):
        """Update progress for weight-based goals"""
        if not self.db.is_connected():
            await self.db.connect()

        try:
            weight_goals = await self.db.goal.find_many(
                where={
                    'userId': self.user_id,
                    'completed': False,
                    'goalType': GoalType.TARGET_WEIGHT
                }
            )

            for goal in weight_goals:
                is_completed = (
                    (goal.targetValue > goal.currentValue and current_weight >= goal.targetValue) or
                    (goal.targetValue < goal.currentValue and current_weight <= goal.targetValue)
                )

                await self.db.goal.update(
                    where={'id': goal.id},
                    data={
                        'currentValue': float(current_weight),
                        'completed': is_completed
                    }
                )

        finally:
            await self.db.disconnect()

    def calculate_progress_percentage(self, goal):
        """Calculate the percentage progress for a goal"""
        if goal.targetValue == goal.currentValue:
            return 100
        elif goal.goalType == GoalType.TARGET_WEIGHT:
            # Handle both weight gain and loss goals
            total_change = abs(goal.targetValue - goal.currentValue)
            progress = abs(goal.currentValue - goal.startValue)
            return min(100, (progress / total_change) * 100)
        else:
            # For workout count and exercise weight goals
            return min(100, (goal.currentValue / goal.targetValue) * 100)