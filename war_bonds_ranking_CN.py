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

st.header('向日葵战争券排行榜')
st.write('更新時間：' + now_str)
st.write('注意：数据源非同步更新，建议2-3小时刷新一次。')


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

    df = pd.DataFrame(zip(owner, tickets), columns=['所有者地址', '战争票数量'])
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

        df['战争票数量'] = df['战争票数量'].astype('int')
        df = df.sort_values(['战争票数量'], ascending=False)
        df = df.reset_index(drop=True)
        col_name = group + '排名'
        df[col_name] = df.index + 1
        df = df[[col_name, '战争票数量', '所有者地址' ]]
    return df


df_m = get_list(m_url, df_m, cursor_m, pages_m, '人类')
df_g = get_list(g_url, df_g, cursor_g, pages_g, '哥布林')

m_tickets = df_m['战争票数量'].sum()
g_tickets = df_g['战争票数量'].sum()
t_tickets = m_tickets + g_tickets
m_owners = df_m.shape[0]
g_owners = df_g.shape[0]

st.write(f'到目前为止，人类共有{m_owners}个贡献者，而哥布林有{g_owners}个。人类贡献了{m_tickets}票，哥布林{g_tickets}票。总票数是{t_tickets}。')

st.title('人类部落战争券排行榜')
st.table(df_m.head(100))


st.title('哥布林部落战争券排行榜')
st.table(df_g.head(100))

st.caption('''
如果发现问题或者有什么建议，请给我信息: \n
Discord: datory.men#9568 \n
\n
''')


