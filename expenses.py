import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data(ttl=3600, max_entries=10)
def load_data():
    file_id = st.secrets['file_id']
    url = st.secrets['url']+file_id 
    xls =  pd.ExcelFile(url)
    return xls.parse('Expenses'), xls.parse('Receipts')

expenses, receipts = load_data()

expenses.sort_values(by='Date', inplace=True, ignore_index=True)
expenses['Date'] = expenses['Date'].dt.strftime('%d-%b-%Y')

receipts.sort_values(by='Date', inplace=True, ignore_index=True)
receipts['Date'] = receipts['Date'].dt.strftime('%d-%b-%Y')

exp_summary = expenses.groupby('Spent By')['Amount'].sum().rename('Total Amount Spent').reset_index()
exp_summary.loc[len(exp_summary)] = ['TOTAL', exp_summary['Total Amount Spent'].sum()]

receipt_summary = receipts.groupby('Paid To')['Amount'].sum().rename('Total Receipts').reset_index()
receipt_summary.loc[len(exp_summary)] = ['TOTAL', receipt_summary['Total Receipts'].sum()]

reconciled_data = pd.merge(left=exp_summary, right=receipt_summary,
                           how='outer', left_on='Spent By', right_on='Paid To').fillna(0)
reconciled_data.rename(columns={'Spent By': 'Name'}, inplace=True)
reconciled_data.drop(columns='Paid To', inplace=True)
reconciled_data['Amount Pending'] = reconciled_data['Total Amount Spent'] - reconciled_data['Total Receipts']

st.write('Expenses and Receipts - Bapat Kaku')

tabs = st.tabs(['Expenses', 'Receipts', 'Reconcile'])
tabs[0].write('Expense Summary')
tabs[0].dataframe(exp_summary, hide_index=True)
tabs[0].write('Expense Details')
tabs[0].dataframe(expenses, hide_index=True)

tabs[1].write('Amount Received Summary')
tabs[1].dataframe(receipt_summary, hide_index=True)
tabs[1].write('Amount Received Details')
tabs[1].dataframe(receipts, hide_index=True)

tabs[2].write('Receivables Summary')
tabs[2].dataframe(reconciled_data, hide_index=True)