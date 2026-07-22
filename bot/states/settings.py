from aiogram.fsm.state import State, StatesGroup

class SettingsStates(StatesGroup):
    waiting_for_welcome = State()
    waiting_for_goodbye = State()
    waiting_for_bad_words = State()