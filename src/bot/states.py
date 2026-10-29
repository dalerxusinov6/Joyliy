"""Finite State Machine (FSM) States for search preferences configuration."""

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

