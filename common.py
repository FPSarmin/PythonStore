import datetime


class User:
    def __init__(self, name, password, Admin, Backets):
        self.name = name
        self.password = password
        self.Admin = True if Admin == 1 else False
        self.Baskets = Backets


class Item:
    def __init__(self, price, amount):
        self.price = int(price)
        self.amount = int(amount)


class Order:
    def __init__(self, date, status, basket):
        self.Date = date
        self.Status = status
        self.basket = basket


class Status:
    CREATED = "CREATED"
    PAID = "PAID"
    SENT = "SENT"
    FINISHED = "FINISHED"


StatusTypes = {"CREATED": Status.CREATED, "PAID": Status.PAID, "SENT": Status.SENT, "FINISHED": Status.FINISHED}


def not_logged_in_menu(status=False):
    msg = "1. Регистрация\n2. Авторизация\n3. Посмотреть список товаров\nВ любой момент введите exit, чтобы покинуть магазин\n"
    command = input_with_range(msg, range(4))
    if command == 1:
        name = input("Введите ваше имя:\n")
        login = input("Введите логин:\n")
        password = input("Введите пароль:\n")
        if not status:
            users.data[login] = User(name, password, status, [len(orders.data)])
            users.update()
            orders.data[len(orders.data)] = Order(datetime.date.today(), Status.CREATED, dict())
            orders.update()
        else:
            users.data[login] = User(name, password, status, [])
            users.update()
        print("Поздравляю с завершением регистрации, теперь вы можете авторизоваться\n")
        return False, ""
    elif command == 2:
        login = input("Введите логин:\n")
        password = input("Введите пароль:\n")
        if login in users.data and users.data[login].password == password and ((status and users.data[login].Admin) or not status):
            print("Добро пожаловать, " + users.data[login].name + '\n')
            return True, login
        else:
            print("Вы ввели неверный логин пользователя или пароль, попробуйте заново\n")
            return False, ""
    elif command == 3:
        command = goods.Goods()
        if command != 0:
            name = goods.name_of_goods[command - 1]
            print("Название товара: " + name + "\nЦена товара: " + str(goods.data[name].price) +
                  "\nКоличество товара: " + str(goods.data[name].amount) + '\n')
            input_with_range("0. Назад\n", range(1))
            return False, ""


def logged_in_menu(login):
    curr_id = users.find_good_basket(login)
    command = -1
    while command != 0:
        msg = "1. Посмотреть товары/Добавить в корзину\n" \
              "2. Отредактировать заказы\n3. Оплатить заказ\nexit\n"
        command = input_with_range(msg, range(4))
        if command == 1:
            command = goods.Goods()
            if command != 0:
                name = goods.name_of_goods[command - 1]
                cur_am = 0
                if name in orders.data[curr_id].basket:
                    cur_am = orders.data[curr_id].basket[name].amount
                print("Название товара: " + name + "\nЦена товара: " + str(goods.data[name].price) +
                      "\nКоличество товара: " + str(goods.data[name].amount - cur_am) + '\n')
                msg = "1. Добавить в корзину\n0. Назад\n"
                command = input_with_range(msg, range(2))
                if command == 1:
                    amount = input_with_range("Введите количество товара, которое вы хотите купить\n", range(goods.data[name].amount - cur_am + 1))
                    if name not in orders.data[curr_id].basket:
                        orders.data[curr_id].basket[name] = Item(goods.data[name].price, amount)
                    else:
                        orders.data[curr_id].basket[name].amount += amount
                    orders.update()
                    if curr_id not in users.data[login].Baskets:
                        users.data[login].Baskets.append(curr_id)
                        users.update()
            else:
                command = -1
        elif command == 2:
            while command != -1:
                command = orders.showOrders(login, "0. Назад\nВыберите корзину чтобы посмотреть\n")
                if command != -1:
                    curr_id = command
                    basket = orders.data[curr_id].basket
                    orders.showItemsInOrder(curr_id)
                    name = input()
                    if name != '0':
                        if orders.data[curr_id].Status != Status.CREATED:
                            command = 0
                            print("Вы не можете изменять уже оплаченный товар\n")
                            continue
                    if name != '0' and name in basket:
                        msg = "1. Удаление товара\n2. Изменение количества\n0. Назад\n"
                        command = input_with_range(msg, range(3))
                        if command == 1:
                            basket.pop(name)
                            orders.data[curr_id] = Order(datetime.date.today(), Status.CREATED, basket)
                            orders.update()
                        elif command == 2:
                            new_amount = input_with_range("Введите новое количество\n", range(basket[name].amount + 1))
                            basket[name].amount = new_amount
                            orders.data[curr_id] = Order(datetime.date.today(), Status.CREATED, basket)
                            orders.update()
                    elif name != '0' and name not in basket:
                        print("Введено некорректное название товара, попробуйте снова\n")
                        command = -1
                    else:
                        command = -1
            else:
                command = -1
        elif command == 3:
            while command != 0:
                command = input_with_range("0.Назад\n1.Оплатить?\n", range(2))
                if command != 0:
                    changed = False
                    for item in orders.data[curr_id].basket:
                        if goods.data[item].amount < orders.data[curr_id].basket[item].amount:
                            changed = True
                    if len(orders.data[curr_id].basket) == 0:
                        print("Вы не можете оплатить данный заказ.\nКорзина пуста\n")
                        command = -1
                    elif changed:
                        print("Вы не можете оплатить данный заказ."
                              "\nОдин или несколько товаров не могут быть куплены из-за их нехватка на складе\n"
                              "Попробуйте позже или измените количество\n")
                        command = -1
                    else:
                        for item in orders.data[curr_id].basket:
                            goods.data[item].amount -= orders.data[curr_id].basket[item].amount
                        orders.data[curr_id].Status = Status.PAID
                        orders.update()
                        goods.update()
                        print("Корзина успешно оплачена, ожидайте получения\n")
                        users.data[login].Baskets.append(len(orders.data))
                        users.update()
                        orders.data[len(orders.data)] = Order(datetime.date.today(), Status.CREATED, dict())
                        orders.update()
                        curr_id = len(orders.data)
                else:
                    command = -1
                    break
            else:
                command = -1


def logged_in_admin():
    command = -1
    while command != 0:
        msg = "1. Посмотреть или изменить каталог товаров\n2. Посмотреть или изменить статус заказа\nexit\n"
        command = input_with_range(msg, range(3))
        if command == 1:
            while command != 0:
                msg = "1. Показать все товары\n2. Добавить товар\n0.Назад\n"
                command = input_with_range(msg, range(3))
                if command == 1:
                    command = goods.Goods()
                    if command != 0:
                        name = goods.name_of_goods[command - 1]
                        print("Название товара: " + name + "\nЦена товара: " + str(goods.data[name].price) +
                              "\nКоличество товара: " + str(goods.data[name].amount) + '\n')
                        msg = "1. Изменить цену\n2. Изменить количество\n0.Назад\n"
                        command = input_with_range(msg, range(3))
                        if command == 1:
                            new_cost = input_with_range("Введите новую цену:\n", range(1000000))
                            goods.data[name].price = new_cost
                            goods.update()
                        elif command == 2:
                            new_amount = input_with_range("Введите новое количество", range(10000000))
                            goods.data[name].amount = new_amount
                            goods.update()
                elif command == 2:
                    command = goods.addItem()
            else:
                command = -1
                break
        if command == 2:
            command = orders.showOrdersNotCreated("0.Назад\nВыберете заказ, у которого вы хотите повысить статус заказа\n")
            if command != 0:
                orders.UpgradeStatus(command - 1)
                orders.update()
            else:
                command = -1


def input_with_range(msg, r):
    while True:
        try:
            command = input(msg)
            if command == "exit":
                exit(0)
            else:
                command = int(command)
                if command not in r:
                    raise Exception
            return command
        except Exception:
            print("Вы ввели неверную команду, попробуйте снова")


class Users:
    def __init__(self):
        self.name_of_file = "users.txt"
        self.data = dict()
        try:
            with open(self.name_of_file, 'r') as UsersData:
                for line in UsersData:
                    data = line.strip().split("\t")
                    Baskets = list()
                    for i in range(4, len(data)):
                        Baskets.append(int(data[i]))
                    self.data[data[0]] = User(data[1], data[2], int(data[3]), Baskets)
        except FileNotFoundError:
            file = open(self.name_of_file, 'w')
            file.close()

    def update(self):
        with open(self.name_of_file, 'w') as UsersData:
            for login in self.data:
                UsersData.write(login + '\t' + self.data[login].name + '\t' + self.data[login].password + '\t' + (
                    '1\t' if self.data[login].Admin else '0\t'))
                for id in self.data[login].Baskets:
                    UsersData.write(str(id) + '\t')
                UsersData.write('\n')

    def register(self, login, name, password, admin):
        users.data[login] = User(name, password, admin, list())
        users.update()

    def find_good_basket(self, login):
        for b in self.data[login].Baskets:
            if orders.data[b].Status == Status.CREATED:
                return b


class Goods:
    def __init__(self):
        self.name_of_file = "goods.txt"
        self.data = dict()
        self.name_of_goods = list()
        try:
            with open(self.name_of_file, 'r') as GoodsData:
                for line in GoodsData:
                    name, price, amount = line.strip().split("\t")
                    self.name_of_goods.append(name)
                    self.data[name] = Item(price, amount)
        except FileNotFoundError:
            file = open(self.name_of_file, 'w')
            file.close()

    def update(self):
        with open(self.name_of_file, 'w') as GoodsData:
            for name in self.data:
                GoodsData.write(name + "\t" + str(self.data[name].price) + '\t' + str(self.data[name].amount) + '\n')

    def Goods(self):
        msg = "0. Назад\n"
        if len(self.name_of_goods) == 0:
            print("На данный момент нет никаких товаров")
        else:
            for i in range(len(self.name_of_goods)):
                msg = msg + str(i + 1) + ": " + self.name_of_goods[i] + '\n'
        command = input_with_range(msg, range(len(self.name_of_goods) + 2))
        return command

    def addItem(self):
        name = input("Введите название товара")
        cost = input_with_range("Введите цену на единицу товара", range(100000000))
        amount = input_with_range("Введите количество товара", range(1000000000))
        if name not in self.data:
            self.name_of_goods.append(name)
        self.data[name] = Item(cost, amount)
        self.update()
        print("Товар добавлен")
        return 0


class Orders:
    def __init__(self):
        self.name_of_file = "orders.txt"
        self.data = dict()
        try:
            with open(self.name_of_file, 'r') as OrdersData:
                for line in OrdersData:
                    data = list(line.strip().split("\t"))
                    basket = dict()
                    for i in range(5, len(data), 3):
                        basket[data[i]] = Item(data[i + 1], data[i + 2])
                    self.data[int(data[0])] = Order(datetime.date(int(data[1]), int(data[2]), int(data[3])),
                                                    StatusTypes[data[4]], basket)
        except FileNotFoundError:
            file = open(self.name_of_file, 'w')
            file.close()

    def update(self):
        with open(self.name_of_file, 'w') as OrdersData:
            for id in self.data:
                OrdersData.write(str(id) + '\t' + str(self.data[id].Date.year) + '\t' + str(self.data[id].Date.month) + '\t' + str(
                    self.data[id].Date.day) + '\t' + self.data[id].Status + '\t')
                for item in self.data[id].basket:
                    OrdersData.write(
                        item + '\t' + str(self.data[id].basket[item].price) + '\t' + str(
                            self.data[id].basket[item].amount) + '\t')
                OrdersData.write('\n')

    def showOrdersCreated(self, login, msg):
        for id in users.data[login].Baskets:
            if self.data[id].Status != Status.CREATED:
                continue
            changed = False
            changedPrice = False
            for item in orders.data[id].basket:
                if goods.data[item].amount < self.data[id].basket[item].amount:
                    changed = True
                if goods.data[item].price != self.data[id].basket[item].price:
                    changedPrice = True
                self.data[id].basket[item].price = goods.data[item].price
            msg = msg + str(id) + ' ' + orders.data[id].Status + ' ' + (
                'Требуются изменения' if orders.data[id].Status == Status.CREATED and changed else " ") + (
                      "Измененная цена" if orders.data[id].Status == Status.CREATED and changedPrice else "") + '\n'
        return input_with_range(msg, range(len(users.data[login].Baskets) + 2))

    def showOrders(self, login, msg):
        for id in users.data[login].Baskets:
            changed = False
            changedPrice = False
            for item in orders.data[id].basket:
                if goods.data[item].amount < orders.data[id].basket[item].amount:
                    changed = True
                if goods.data[item].price != orders.data[id].basket[item].price:
                    changedPrice = True
                orders.data[id].basket[item].price = goods.data[item].price
            msg = msg + str(id + 1) + ' ' + orders.data[id].Status + ' ' + (
                'Недостаточно товара на складе' if orders.data[id].Status == Status.CREATED and changed else "") + (
                      ", Измененная цена" if orders.data[id].Status == Status.CREATED and changedPrice else "") + '\n'
        command = input_with_range(msg, range(len(users.data[login].Baskets) + 2))
        print(command)
        return command - 1

    def showItemsInOrder(self, id):
        msg = "0. Назад\nДля изменения количества необходимо полностью ввести название товара (С учетом регистра)\n"
        for item in orders.data[id].basket:
            msg += item + ' Количество: ' + str(orders.data[id].basket[item].amount)
            if goods.data[item].amount < orders.data[id].basket[item].amount and orders.data[id].Status == Status.CREATED:
                msg += " (Недостаточно товара, требуется изменение, на складе " + str(
                    goods.data[item].amount) + " ед. товара)"
            msg += ' Цена: ' + str(orders.data[id].basket[item].price) + '\n'
        print(msg)

    def UpgradeStatus(self, id):
        if self.data[id].Status == Status.PAID:
            self.data[id].Status = Status.SENT
        elif self.data[id].Status == Status.SENT:
            self.data[id].Status = Status.FINISHED
        print("Статус успешно измненен\n")

    def showOrdersNotCreated(self, msg):
        Range = [0]
        for id in self.data:
            if self.data[id].Status == Status.CREATED or self.data[id].Status == Status.FINISHED:
                continue
            msg += str(id + 1) + ' ' + self.data[id].Status + '\n'
            Range.append(id + 1)
        return input_with_range(msg, Range)


users = Users()
orders = Orders()
goods = Goods()
