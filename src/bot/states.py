"""Finite State Machine (FSM) States for search preferences and ecosystem interactions."""

from aiogram.fsm.state import State, StatesGroup


class SearchConfigState(StatesGroup):
    """States for configuring user apartment search filters."""

    selecting_district = State()
    waiting_min_price = State()
    waiting_max_price = State()
    selecting_rooms = State()
    waiting_min_area = State()
    waiting_max_area = State()
    selecting_owner_only = State()
    configuring_quiet_hours = State()


class AIMatchState(StatesGroup):
    """States for natural language AI apartment matching."""

    waiting_query = State()


class AssistantChatState(StatesGroup):
    """States for AI rental consultation."""

    waiting_question = State()


class ComparisonState(StatesGroup):
    """States for side-by-side listing comparison."""

    waiting_listing_ids = State()


class RoommateCreationState(StatesGroup):
    """States for creating a roommate profile."""

    waiting_name = State()
    waiting_district = State()
    waiting_budget = State()
    waiting_about = State()
