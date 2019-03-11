from datetime import time, timedelta, datetime
from yaml import load, dump
from decimal import Decimal
import locale


class Activity():
    """invoice item, consisting of date, description, starttime, endtime, quantity, rate and sum"""

    def __init__(self, items):
        """Initialize activity properties from yml file and calculate quantity if not given"""
        self.type = items['type'] if 'type' in items else None
        self.occasion = items['occasion'] if 'occasion' in items else None
        self.date = items['date'] if 'date' in items else None
        self.description = items['description'] if 'description' in items else None
        self.occasion = items['occasion'] if 'occasion' in items else None
        self.rate = items['rate'] if 'rate' in items else None
        self.starttime = datetime.strptime(items['starttime'], '%H:%M') if 'starttime' in items else None
        self.endtime = datetime.strptime(items['endtime'], '%H:%M') if 'endtime' in items else None
        self.qty = float(items['qty']) if 'qty' in items else None
        self.sum = items['sum'] if 'sum' in items else 0


    def calculate_qty(self):
        """calculate length of activity based on starttime and endtime"""

        span = self.endtime - self.starttime
        span = span.seconds / 3600

        return(float(span))



    def compare_qty(self):
        """check if calculated qty equals given qty"""
        if(self.qty == self.calculate_qty()):
            return True
        else:
            return False

    def compute_sum(self):
        """multiply quantity with rate"""
        if self.qty and self.rate != None:

            return self.qty * self.rate
        else:
            return self.sum


class Invoiceitem():
    """activities of one category (with same rate) are combined to one position in invoice"""

    def __init__(self):
        self.name = ''
        self.rate = None
        self.sum = 0
        self.qty = 0
        self.date = None
        self.occasion = ''
        self.description = ''




class Invoice():
    """load data from yml, calculate sum and create pdf"""

    def __init__(self, data):
        """initialize invoice properties"""
        self.invoicenr = data['nr']
        self.language = data['language'] if 'language' in data else 'de'
        self.date = data['date']
        self.poref = data['poref'] if 'poref' in data else None
        self.kstref = data['kstref'] if 'kstref' in data else None
        self.subject = data['subject'] if 'subject' in data else None
        self.to = data['to']
        self.taxfree = data['taxfree'] if 'taxfree' in data else None
        self.account = data['account']
        self.opening = data['opening']
        self.closing = data['closing']
        self.billables = data['billables'] if 'billables' in data else []
        self.expenses = data['expenses'] if 'expenses' in data else None
        self.activitylist = []
        self.typelist = []
        self.expensetypelist = []
        self.invoiceitemlist_short = []
        self.invoiceitemlist = []
        self.expenseslist = []



    def create_activitylist(self):
        """initialize a new activity with data"""

        for item in self.billables:
            newActivity = Activity(item)
            self.activitylist.append(newActivity)
            self.typelist.append(newActivity.type)


    def create_expenseslist(self):
        """create new Expense and add to list"""

        for item in self.expenses:
            newExpense = Expense(item)
            self.expenseslist.append(newExpense)
            self.expensetypelist.append(newExpense.type)




    def calculate_quantities(self):
        """calculate qty for each activity and compare with given qty if it exists"""

        for activity in self.activitylist:
            if activity.qty is not None and activity.starttime is not None and activity.endtime is not None:
                same = activity.compare_qty()
                calcqty = activity.calculate_qty()

                if same == False:
                    print('Computed quantity {} and given quantity {} for {} are not the same,'
                          ' please check'.format(calcqty, activity.qty, activity.description))
                    activity.qty = float(input('Enter correct value'))
            elif activity.qty == None and activity.starttime is not None and activity.endtime is not None:
                activity.qty = activity.calculate_qty()



    def create_invoiceitemlist(self):
        """create list for invoice"""

        for activity in self.activitylist:
            newInvoiceitem = Invoiceitem()
            activity.sum = activity.compute_sum()
            newInvoiceitem.name = activity.description
            newInvoiceitem.rate = activity.rate
            newInvoiceitem.qty = activity.qty
            newInvoiceitem.sum = activity.sum
            newInvoiceitem.date = activity.date
            self.invoiceitemlist.append(newInvoiceitem)



    def create_short_invoiceitemlist(self):
        """combine activities with same type to one item and calculate sum """

        types = set(self.typelist)

        for type in types:

            newInvoiceitem = Invoiceitem()

            for activity in self.activitylist:
                if activity.type == type and activity.qty != None:
                    newInvoiceitem.rate = activity.rate
                    newInvoiceitem.sum += activity.compute_sum()
                    newInvoiceitem.qty += activity.qty
                    newInvoiceitem.name = activity.type
                elif activity.type == type and activity.qty == None:
                    newInvoiceitem.rate = activity.rate
                    newInvoiceitem.sum += activity.sum
                    newInvoiceitem.qty = None
                    newInvoiceitem.name = activity.type
            self.invoiceitemlist_short.append(newInvoiceitem)


        types = set(self.expensetypelist)
        for type in types:
            newInvoiceitem = Invoiceitem()

            for expense in self.expenseslist:
                if expense.type == type:
                    newInvoiceitem.name = expense.type
                    newInvoiceitem.sum += expense.sum

            self.invoiceitemlist_short.append(newInvoiceitem)

        return self.invoiceitemlist_short





    def prepare_data(self):
        """create activities and compute times and prices"""
        self.create_activitylist()
        self.calculate_quantities()

        if self.expenses != None:
            self.create_expenseslist()



    def calculate_total_sum(self, list):
        """sum of all activity prices without vat"""
        total_sum = 0

        for item in list:
            total_sum += item.sum

        return total_sum

    def calculate_vat(self, total_sum):
        """calculate vat 19% of total_sum"""

        vat = total_sum * 0.19

        return round(Decimal(vat), 2)

    def calculate_gross_sum(self, total_sum, vat):
        """gross incl vat"""

        gross_sum = Decimal(total_sum) + vat

        return gross_sum


    def prepare_shortinvoice(self):
        """combines activities with same rate"""

        invoiceitemlist_short = self.create_short_invoiceitemlist()

        return invoiceitemlist_short



class Expense():
    """representation of an expense like hotel or """

    def __init__(self, item):
        self.name = item['name'] if 'name' in item else ''
        self.type = item['type'] if 'type' in item else None
        self.sum = item['sum'] if 'sum' in item else 0
        self.date = item['date'] if 'date' in item else ''
        self.occasion = item['occasion'] if 'occasion' in item else''
        self.description = item['description'] if 'description' in item else ''







