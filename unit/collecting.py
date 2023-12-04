import time
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

root_dir = '..\data'
balance_dir = os.path.join(root_dir,'stock_balance')
cash_flow_dir = os.path.join(root_dir,'stock_cash_flow')
company_dir = os.path.join(root_dir,'company_list.csv')
industry_dir = os.path.join('..','company_list.csv')
web_01 = r'https://mops.twse.com.tw/mops/web/t164sb03'
web_02 = r'https://mops.twse.com.tw/mops/web/t164sb04'
BASE_DIR = os.path.abspath('..')
CHROME_DRIVER = os.path.join(BASE_DIR, 'chromedriver.exe')


def run_crawler(stock_id_list):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome = webdriver.Chrome(executable_path=CHROME_DRIVER, options=options)
    y_q = get_y_q()
    ans = []
    for i in tqdm(stock_id_list):
        result = get_IncomeBeforeIncomeTax(chrome, i, y_q)
        ans.append([str(i), str(y_q[0][0]+1911)+'Q'+str(y_q[0][1]), str(y_q[1][0]+1911)+'Q'+str(y_q[1][1]), round(result*100,2)])
    chrome.close()
    chrome.quit()
    return ans


def hasxpath(browser,xpath):
    try:
        browser.find_element(By.XPATH, value=xpath)
        return True
    except:
        return False


def get_IncomeBeforeIncomeTax(browser, stock_id, y_q):
    IncomeBeforeIncomeTax = []
    print(stock_id)
    while len(IncomeBeforeIncomeTax) != 2:
        try:
            for i in y_q:
                browser.get(web_02)
                Select(browser.find_element(By.ID, value='isnew')).select_by_visible_text("歷史資料")
                browser.find_element(By.ID, value='co_id').send_keys(stock_id)
                browser.find_element(By.ID, value='year').send_keys(i[0])
                Select(browser.find_element(By.ID, value='season')).select_by_visible_text(str(i[1]))
                browser.find_element(by=By.CSS_SELECTOR, value="#search_bar1 > div > input[type=button]").click()
                time.sleep(2)
                if hasxpath(browser, '//*[@id="table01"]/center/h4/font') == True:
                    status1 = browser.find_element(By.XPATH, value='//*[@id="table01"]/center/h4/font').text
                if hasxpath(browser, '//*[@id="table01"]/center/center/h3') == True:
                    return np.nan
                if hasxpath(browser, '//*[@id="fm1"]/table/tbody/tr[2]/td[3]/input') == True:
                    return np.nan
                    #browser.find_element(by=By.XPATH, value='//*[@id="fm1"]/table/tbody/tr[2]/td[3]/input').click()
                    #time.sleep(2)
                if '查無所需資料' in status1:
                    return np.nan
                for num in range(100):
                    if num == 99:
                        return np.nan
                    try:
                        name = browser.find_element(by=By.XPATH,
                                                    value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[1]".format(
                                                        num)).accessible_name
                        if name == '稅前淨利（淨損）':
                            if i[1] == 1 or i[1] == 4:
                                tax = browser.find_element(by=By.XPATH,
                                                           value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[2]".format(
                                                               num)).text
                            else:
                                tax = browser.find_element(by=By.XPATH,
                                                           value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[6]".format(
                                                               num)).text
                            break
                    except:
                        pass
                IncomeBeforeIncomeTax.append(int(tax.replace(',', '')))
        except Exception as e:
            IncomeBeforeIncomeTax = []
            time.sleep(15)
    Assets = []
    while len(Assets) != 2:
        try:
            for i in y_q:
                browser.get(web_01)
                Select(browser.find_element(By.ID, value='isnew')).select_by_visible_text("歷史資料")
                browser.find_element(By.ID, value='co_id').send_keys(stock_id)
                browser.find_element(By.ID, value='year').send_keys(i[0])
                Select(browser.find_element(By.ID, value='season')).select_by_visible_text(str(i[1]))
                browser.find_element(by=By.CSS_SELECTOR, value="#search_bar1 > div > input[type=button]").click()
                time.sleep(2)
                if hasxpath(browser, '//*[@id="table01"]/center/h4/font') == True:
                    status1 = browser.find_element(By.XPATH, value='//*[@id="table01"]/center/h4/font').text
                if hasxpath(browser, '//*[@id="table01"]/center/center/h3') == True:
                    return np.nan
                if hasxpath(browser, '//*[@id="fm1"]/table/tbody/tr[2]/td[3]/input') == True:
                    return np.nan
                    #browser.find_element(by=By.XPATH, value='//*[@id="fm1"]/table/tbody/tr[2]/td[3]/input').click()
                    #time.sleep(2)
                if '查無所需資料' in status1:
                    return np.nan
                for num in range(100):
                    if num == 99:
                        return np.nan
                    try:
                        name = browser.find_element(by=By.XPATH, value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[1]".format(num)).accessible_name
                        if '資產總額' in name or '資產總計'  in name:
                            AllAssets = browser.find_element(by=By.XPATH,
                                                             value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[2]".format(num)).text
                        if '\u3000流動負債合計'  in name:
                            CurrentLiabilities = browser.find_element(by=By.XPATH,
                                                                      value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[2]".format(num)).text
                        if '負債及權益總計' in name:
                            TotalAssets = browser.find_element(by=By.XPATH,
                                                               value="//*[@id='table01']/center/table[2]/tbody/tr[{}]/td[2]".format(num)).text
                            break
                    except:
                        pass
                #CurrentAssets = browser.find_element(by=By.XPATH, value="//*[@id='table01']/center/table[2]/tbody/tr[18]/td[2]").text
                #NoncurrentAssets = browser.find_element(by=By.XPATH, value="//*[@id='table01']/center/table[2]/tbody/tr[28]/td[2]").text
                Assets.append([int(AllAssets.replace(',', '')), int(CurrentLiabilities.replace(',', '')), int(TotalAssets.replace(',', ''))])
        except Exception as e:
            Assets = []
            time.sleep(15)
        '''
        // *[ @ id = "table01"] / center / table[2] / tbody / tr[18] / td[2]
        // *[ @ id = "table01"] / center / table[2] / tbody / tr[28] / td[2]
        //*[@id="table01"]/center/table[2]/tbody/tr[29]/td[2]
        //*[@id="table01"]/center/table[2]/tbody/tr[29]/td[2]
        // *[ @ id = "table01"] / center / table[2] / tbody / tr[40] / td[2]
        //*[@id="table01"]/center/table[2]/tbody/tr[66]/td[2]
        '''
    result_now = IncomeBeforeIncomeTax[0] / (
                Assets[0][0] - Assets[0][1]) + IncomeBeforeIncomeTax[0] / Assets[0][2]
    result_past = IncomeBeforeIncomeTax[1] / (
            Assets[1][0] - Assets[1][1]) + IncomeBeforeIncomeTax[1] / Assets[1][2]
    result = result_now - result_past
    return result


def get_y_q():
    y_now = pd.Timestamp(datetime.today()).year - 1911
    q_now = pd.Timestamp(datetime.today()).quarter
    if q_now == 1:
        q_now = 4
        y_now -= 1
    else:
        q_now -= 1
    if q_now == 1:
        y_past = y_now - 1
        q_past = 4
    else:
        y_past = y_now
        q_past = q_now -1
    return [[y_now, q_now], [y_past, q_past]]



def arrange_balance():
    all_path = glob.glob(os.path.join(balance_dir,'*'))
    list1 = ['CurrentAssets', 'NoncurrentAssets', 'CurrentLiabilities', 'TotalAssets']
    result = []
    for i in all_path:
        print(os.path.basename(i))
        cash_flow_path = os.path.join(cash_flow_dir, os.path.basename(i))
        if os.path.exists(cash_flow_path):
            try:
                cash_flow_df = pd.read_csv(cash_flow_path)
                df = pd.read_csv(i)
            except:
                print('stock_num {} not exists'.format(os.path.basename(i).split(".")[0]))
                continue
        else:
            print('stock_num {} not exists'.format(os.path.basename(i).split(".")[0]))
            continue
        try:
            cash_flow_df = cash_flow_df[cash_flow_df['type'] == 'IncomeBeforeIncomeTaxFromContinuingOperations']
            cash_flow_df.date = pd.to_datetime(cash_flow_df.date)
            cash_flow_df.date = cash_flow_df.date.dt.to_period('Q')
            cash_flow_df.columns = ['date', 'stock_id', 'type', 'IncomeBeforeIncomeTax', 'origin_name']
            df = df[df['type'].isin(list1)]
            df.date = pd.to_datetime(df.date)
            df.date = df.date.dt.to_period('Q')
            df = df.drop('origin_name', axis=1)
            df = df.groupby(['date', 'stock_id', 'type']).sum().squeeze().unstack().reset_index()
            df = pd.merge(df, cash_flow_df[['date', 'stock_id', 'IncomeBeforeIncomeTax']], how='left', on=['date', 'stock_id'])
            df['percentage'] = df.IncomeBeforeIncomeTax/(df.CurrentAssets-df.CurrentLiabilities+df.NoncurrentAssets) + df.IncomeBeforeIncomeTax/df.TotalAssets
            change = df.iloc[-1].percentage - df.iloc[-2].percentage
            result.append([df.iloc[-2].stock_id, df.iloc[-1].date, df.iloc[-2].date, format(change,'.2%')])
        except Exception as e:
            print(repr(e))
            continue
    longder_result = pd.DataFrame(np.array(result),columns=['stock_id', 'Past_date', 'current_date', 'diff'])
    company_df = pd.read_csv(company_dir)
    longder_result = longder_result.merge(company_df)
    longder_result.to_csv(r'..\result\longder_{}.csv'.format(datetime.today().strftime('%Y-%m-%d')), encoding='utf-8-sig')


def merge_eps(lon_path,eps_path):
    df = pd.read_csv(lon_path)
    eps_df = pd.read_csv(eps_path)
    eps_df = eps_df[['代碼', '名稱', '每股EPS(元)']]
    eps_df.columns = ['stock_id', 'stock_name', 'eps']
    df = df.drop('stock_name', axis=1)
    result = df.merge(eps_df,on='stock_id',how='left')
    result.to_csv(r'..\result\longder_result.csv', encoding='utf-8-sig',index=False)



if __name__ == '__main__':
    #arrange_balance()
    '''
    company_list = pd.read_csv(company_dir).stock_id.tolist()
    result_list = run_crawler(company_list)
    df = pd.DataFrame(np.array(result_list), columns=['stock_id', 'Past_date', 'current_date', 'diff'])
    company_df = pd.read_csv(industry_dir)
    company_df.stock_id = company_df.stock_id.astype(str)
    longder_result = df.merge(company_df, on='stock_id', how='left')
    longder_result.to_csv(r'..\result\longder_{}.csv'.format(datetime.today().strftime('%Y-%m-%d')), encoding='utf-8-sig', index=False)
    '''
    merge_eps(r'C:\Users\mick7\PycharmProjects\longder\result\longder_2022-03-30.csv', r'C:\Users\mick7\PycharmProjects\longder\result\eps.csv')
