from aiogram.fsm.state import StatesGroup, State


class SendReceipt(StatesGroup):
    receipt = State()
