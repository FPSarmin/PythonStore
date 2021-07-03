import os

from common import User, Item, Order, users, goods, orders, input_with_range, not_logged_in_menu, logged_in_menu, logged_in_admin

if __name__ == '__main__':
    command = int(-1)
    loggedIn = False
    login = ""
    while command != 0:
        if not loggedIn:
            loggedIn, login = not_logged_in_menu(status=True)
        else:
           logged_in_admin()
