import streamlit as st
import pandas as pd
import datetime
import pytz
import cloudscraper
import json


st.set_page_config(layout='wide')

now_time = (datetime.datetime.now(pytz.timezone('Asia/Hong_Kong')))
now_str = now_time.strftime("%Y-%m-%d %H:%M")

today_time = datetime.datetime.date(now_time)
today = today_time.strftime('%Y-%m-%d')
today_str = today_time.strftime("%Y-%m-%d %H:%M")



# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

st.header('Sunflower Land War Bonds Ranking')
st.write('Updated：' + now_str)
st.write('Note：This free data source is not updated immediately. Suggest to refresh every 2-3 hours.')

st.caption('''
Any feedback or suggestion，please message me: \n
Discord: datory.men#9568 \n
''')

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    "X-API-Key": "test"
}

m_url = "https://deep-index.moralis.io/api/v2/nft/0x22d5f9b75c524fec1d6619787e582644cd4d7422/919/owners?chain=polygon&format=decimal"
g_url = "https://deep-index.moralis.io/api/v2/nft/0x22d5f9b75c524fec1d6619787e582644cd4d7422/918/owners?chain=polygon&format=decimal"

def get_owners(url):
    res = scraper.get(url, headers=headers)
    output= json.loads(res.text)
    results = output['result']
    owner = []
    tickets = []
    df = pd.DataFrame()
    for result in results:
        owner.append(result['owner_of'])
        tickets.append(result['amount'])

    df = pd.DataFrame(zip(owner, tickets), columns=['Farm Address', 'Bonds'])
    cursor = output['cursor']
    pages = output['total']//100+1
    return df, cursor, pages

df_m, cursor_m, pages_m = get_owners(m_url)
df_g, cursor_g, pages_g = get_owners(g_url)

def get_list(url, df, cursor, pages, group):

    for page in range(1, pages):
        if cursor:
            new_url = url + "&cursor=%s" % cursor
        df_next, cursor, pages = get_owners(new_url)
        df = df.append(df_next)

        df['Bonds'] = df['Bonds'].astype('int')
        df = df.sort_values(['Bonds'], ascending=False)
        df = df.reset_index(drop=True)
        col_name = group + ' Ranking'
        df[col_name] = df.index + 1
        df['Group'] = group
        df = df[[col_name, 'Bonds', 'Farm Address', 'Group']]
    return df


df_m = get_list(m_url, df_m, cursor_m, pages_m, 'Human')
df_g = get_list(g_url, df_g, cursor_g, pages_g, 'Goblin')

m_tickets = df_m['Bonds'].sum()
g_tickets = df_g['Bonds'].sum()
t_tickets = m_tickets + g_tickets
m_owners = df_m.shape[0]
g_owners = df_g.shape[0]

df_overall = df_m[['Bonds', 'Farm Address', 'Group']].append(df_g[['Bonds', 'Farm Address', 'Group']])
df_overall = df_overall.sort_values('Bonds', ascending=False)
df_overall = df_overall.reset_index(drop=True)
df_overall['Ranking'] = df_overall.index + 1
df_overall = df_overall[['Ranking','Group', 'Bonds', 'Farm Address']]


st.write(f'Up to now，there are {m_owners} Human contributors and {g_owners} Goblin contributors. Human team has {m_tickets} bonds. Goblin team has {g_tickets} bonds. Total bond quantity is {t_tickets}.')


st.title('Overall War Bonds Ranking')
st.table(df_overall.head(100))

st.title('Human Team War Bonds Ranking')
st.table(df_m.head(100))


st.title('Goblin Team War Bonds Ranking')
st.table(df_g.head(100))




