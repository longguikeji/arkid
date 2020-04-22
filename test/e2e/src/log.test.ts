import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');

declare var global: any

jest.setTimeout(600000);

describe('一账通-测试操作日志', () => {
    let page : Page;
    
    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
       // await page.close();
    })

    test('TEST_001:验证操作日志' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
    
        await page.waitFor(2000);

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();
       
        await page.waitFor(3000);

        const logBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-middle > ul > a:nth-child(6)');
        await logBtn.click();
       
        await page.waitFor(10000); 
 
        const loginLog = await page.$eval('.ivu-table-tbody>tr:first-child>td:last-child>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLog).toEqual('查看详细日志');

        const loginLogPer = await page.$eval('.ivu-table-tbody>tr>td:nth-child(2)>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLogPer).toMatch('ad');

    });

    test('TEST_002:验证查看详细日志' , async() => {
      
        await page.waitFor(2000);

        const logDetailsBtn = await page.waitForSelector('.ivu-table-tbody>tr>td:last-child>div');
        await logDetailsBtn.click();
        
        await page.waitFor(3000);

        const loginLogPer = await page.$eval('div.ivu-modal-body > div > div.left > div.basic > div:nth-child(2) > span.content', elem => {
            return elem.innerHTML;
        });
        await expect(loginLogPer).toMatch('ad');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})
