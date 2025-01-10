import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute("DELETE FROM Users WHERE id=6")

cursor.execute("SELECT COUNT(*) FROM Users")
total_users = cursor.fetchone()[0]

cursor.execute("SELECT SUM(balance) FROM Users")
all_balances = cursor.fetchone()[0]

if total_users > 0:
    average_balance = all_balances / total_users
    print(f'Средний баланс всех пользователей: {average_balance}')
else:
    print('Нет пользователей для расчета среднего баланса.')

conn.close()
