
def test_add_employee(self):
    to_test = employees(self.connection)
    to_test.add_employee('Test1', 'Employee', date.today())
    cursor = self.connection.cursor()
    cursor.execute('''select * from employees order by date_of_employment''')
    self.assertEqual(tuple(cursor),(('Test2', 'Employee', date(year=2001,month=3,day=18)),\
                    ('Test1', 'Employee', date(year=2003,month=7,day=12)),\
                    ('Test1', 'Employee', date.today())))

def test_find_employees_by_name(self):
    to_test = employees(self.connection)
    found = tuple(to_test.find_employees_by_name('Test1', 'Employee'))
    expected = (('Test1', 'Employee', date(year=2003,month=7,day=12)),)
    self.assertEqual(found, expected)

def test_find_employee_by_date(self):
    to_test = employees(self.connection)
    target = date(year=2001, month=3, day=18)
    found = tuple(to_test.find_employees_by_date(target))
    expected = (('Test2', 'Employee', target),)
    self.assertEqual(found, expected)

if __name__ == '__main__':
    main()
