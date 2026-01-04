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

exp_summary = expenses.groupby('Spent By')['Amount'].sum().rename('Total Amount Spent').reset_index()
receipt_summary = receipts.groupby('Paid To')['Amount'].sum().rename('Total Receipts').reset_index()
reconciled_data = pd.merge(left=exp_summary, right=receipt_summary,
                           how='outer', left_on='Spent By', right_on='Paid To').fillna(0)
reconciled_data.rename(columns={'Spent By': 'Name'}, inplace=True)
reconciled_data.drop(columns='Paid To', inplace=True)
reconciled_data['Amount Pending'] = reconciled_data['Total Amount Spent'] - reconciled_data['Total Receipts']

st.title('Expense and Receipts Reconciliation')

tabs = st.tabs(['Expenses', 'Receipts', 'Reconcile'])
tabs[0].write('Expenses by Person')
tabs[0].dataframe(expenses, hide_index=True)

tabs[0].dataframe(exp_summary, hide_index=True)

tabs[1].write('Receipts')
tabs[1].dataframe(receipts, hide_index=True)
tabs[1].dataframe(receipt_summary, hide_index=True)

tabs[2].write('Reconciled Data')
tabs[2].dataframe(reconciled_data, hide_index=True)