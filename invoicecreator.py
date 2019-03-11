import os
import shutil
import sys
import subprocess
from datetime import time, timedelta, datetime
import locale
import yaml
import argparse
import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2.loaders import FileSystemLoader
import latex
from latex.jinja2 import make_env

from items import Invoice


def read_file(filename):
    """read a yml file"""
    try:
        with open(filename, 'r') as stream:
            data_loaded = yaml.load(stream)

        return data_loaded
    except IOError:
        print("Could not read file:", filename)
    except TypeError:
        print('something went wrong')


def create_pdf(filename, template, context):
    """compile tex to pdf and save in source directory"""
    build_d = os.path.join(source_dir, 'results/')
    output_dir = os.path.join(source_dir, 'output/')
    out_file = '{}{}'.format(output_dir, filename)

    if not os.path.exists(output_dir):  # create directory for tex files if not existing
        os.makedirs(output_dir)

    with open(out_file + ".tex", "w") as f:  # saves tex_code to output file
        f.write(template.render(**context))

    if not os.path.exists(build_d):  # create the directory for the pdf if not existing
        os.makedirs(build_d)

    result = subprocess.call(['pdflatex',
                              '-output-directory', '{}'.format(os.path.realpath(build_d)),
                                '{}'.format(os.path.realpath(out_file + '.tex'))],
                               shell=False)


def collect_context(newInvoice):
    """add all variables to context dict for passing to template"""

    context = {}
    if (args.invoicetype == 'short'):

        itemslist = newInvoice.prepare_shortinvoice()
    elif (args.invoicetype == 'long'):
        itemslist = newInvoice.invoiceitemlist_long

    else:
        print('please select an invoicetype')
        sys.exit()

    total_sum = newInvoice.calculate_total_sum(itemslist)
    context['total_sum'] = locale.currency(total_sum, symbol=False)
    vat = newInvoice.calculate_vat(total_sum)
    context['vat'] = locale.currency(vat, symbol=False)
    gross_sum = newInvoice.calculate_gross_sum(total_sum, vat)
    context['gross_sum'] = locale.currency(gross_sum, symbol=False)


    context['poref'] = newInvoice.poref
    context['kstref'] = newInvoice.kstref
    context['invoicenr'] = newInvoice.invoicenr
    context['to'] = newInvoice.to
    context['opening'] = newInvoice.opening
    context['closing'] = newInvoice.closing

    for item in itemslist:
        item.sum = locale.currency(item.sum, symbol=False)
        if item.rate != None:
            item.rate = locale.currency(item.rate, symbol=False)

    context['itemslist'] = itemslist

    return context


def select_template():
    """choose tex template according to language set in yml"""

    if new_invoice.language == 'en':
        template = env.get_template('invoice-eng.tex')
    else:
        template = env.get_template('invoice.tex')

    return template



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='please enter filename')
    parser.add_argument('--invoicetype',  choices=['short', 'long'], default='short')
    parser.add_argument('--timesheet', choices=['timesheet', 'no'], default='timesheet')

    locale.setlocale(locale.LC_ALL, '')

    args = parser.parse_args()
    data = read_file(args.filename)
    # split source directory and filename
    source_dir, filename = os.path.split(args.filename)
    filename = os.path.splitext(filename)[0]
    working_dir = os.getcwd()

    new_invoice = Invoice(data)

    if new_invoice.language == 'en':
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')


    new_invoice.prepare_data()
    new_invoice.create_invoiceitemlist()

    context = collect_context(new_invoice)
    env = make_env(loader=FileSystemLoader(working_dir + '/templates/'))
    template = select_template()


    create_pdf(filename, template, context)



    if (args.timesheet == 'timesheet'):

        itemslist = new_invoice.invoiceitemlist
        for item in itemslist:
            item.sum = locale.currency(item.sum, symbol=False)
        context['itemslist'] = itemslist
        if new_invoice.language == 'eng':
            template = env.get_template('stundennachweis-eng.tex')
        else:
            template = env.get_template('stundennachweis.tex')
        create_pdf(filename + '_timesheet', template, context)


    if new_invoice.expenses is not None:
        itemslist = new_invoice.expenseslist
        for item in itemslist:
            item.sum = locale.currency(item.sum, symbol=False)
        context['itemslist'] = itemslist
        if new_invoice.language == 'eng':
            template = env.get_template('reisekosten-eng.tex')
        else:
            template = env.get_template('reisekosten.tex')
        create_pdf(filename + '_travel', template, context)

