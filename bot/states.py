from aiogram.fsm.state import StatesGroup, State


class RegisterState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()


from aiogram.fsm.state import StatesGroup, State

class CartAddStates(StatesGroup):
    waiting_for_color = State()
    waiting_for_size = State()
    waiting_for_quantity = State()

class CheckoutState(StatesGroup):    
    waiting_for_screenshot = State()